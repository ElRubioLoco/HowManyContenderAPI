import base64
import http.client
import json
import sys
import traceback

from flask import Flask

from src.utils.Enums import *
from src.utils.Functions import prepare_to_send


class Server(Flask):
    headers = {
        RequestKeys.CONTENTTYPE.value: 'application/json',
        # RequestKeys.REFRESHTOKEN.value: "", They don't exist on startup
        # RequestKeys.ACCESSTOKEN.value: "",
        RequestKeys.USERAGENT.value: 'How many contenders / howmanycontenders@gmail.com',
        RequestKeys.UBIAPPID.value: '86263886-327a-4328-ac69-527f0d20a237'
    }

    def __init__(self, name: str):
        super().__init__(name)

    def _send_request(self, method: Methods, host: str, path: str, body: dict = None) -> dict:
        """
        This method sends a request with the specified method to the specified host (ex: http://localhost:8080)\n
        with the specified path (ex: /path/to/your/route).

        You have the possibility to specify also the headers and body used in this request.

        NB: You can use the values of the Method enumeration to specify the method used.
        """
        if body is None:
            body = {}

        conn = http.client.HTTPSConnection(host, 443)
        body = prepare_to_send(body)
        conn.request(method, path, body=body, headers=self.headers)  # <---
        r = conn.getresponse().read()


        if len(r) == 0:
            print("Invalid response", file=sys.stderr)
            return {RequestKeys.ERROR.value: "Got an invalid response from " + host + path}

        return json.loads(r)

    def send_post_request(self, host: str, path: str, body: dict = None):
        return self._send_request(Methods.POST, host, path, body)

    def send_get_request(self, host: str, path: str):
        return self._send_request(Methods.GET, host, path)

    def authenticate(self, audience: Audiences) -> dict:
        """
        This method authenticates the server to nadeo services with the specified audience.

        Use the Audiences enumeration available at src/utils/Enums.py to specify the audience.
        """
        try:

            authorization = open("src/utils/authenticate.txt", 'r', encoding='utf-8').read()
            self.headers[RequestKeys.AUTHORIZATION.value] = 'Basic {}'.format(
                base64.b64encode(authorization.encode('ascii')).decode('ascii'))

            response = self.send_post_request('public-ubiservices.ubi.com', '/v3/profiles/sessions')

            if response.get(NadeoResponsesKeys.TICKET.value) is None:
                if not response.get(NadeoResponsesKeys.ERRORCODE.value) is None:
                    print("API error : " + str(response), file=sys.stderr)
                    message = response.get(NadeoResponsesKeys.MESSAGE)
                else:
                    message = "Unknown error"
                return {RequestKeys.ERROR.value: message}

            body = {RequestKeys.AUDIENCE.value: audience.value}

            self.headers[RequestKeys.AUTHORIZATION.value] = 'ubi_v1 t={}'.format(response["ticket"])

            response = self.send_post_request("prod.trackmania.core.nadeo.online",
                                              "/v2/authentication/token/ubiservices", body)

            self.update_tokens(response)
            self.headers[RequestKeys.AUTHORIZATION.value]\
                = 'nadeo_v1 t={}'.format(response[RequestKeys.ACCESSTOKEN])

            return response

        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            return {RequestKeys.ERROR.value: traceback.format_exc()}

    def refresh_token(self) -> None:
        """
        This method allows to get a new refresh token once the old one is not active anymore.
        """
        if self.headers.get(RequestKeys.REFRESHTOKEN.value) is None:
            raise ConnectionError("The server needs to be authenticated before refreshing it's tokens")

        self.headers[RequestKeys.AUTHORIZATION.value] = "nadeo_v1 t={}".format(self.headers.get(RequestKeys.REFRESHTOKEN.value))
        tokens = self.send_post_request("prod.trackmania.core.nadeo.online", "/v2/authentication/token/refresh")
        self.update_tokens(tokens)

    def get_player_count(self, mapuid: str) -> dict:
        """
        This method gets the total count of players that played the specified map.

        This is got done by calling the Nadeo Live services route : https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/map?scores[<mapuid>]=<integerMaxValue>
        """
        if not self.is_authenticated():
            print("Server isn't authenticated, authenticating...")
            self.authenticate(Audiences.NADEOLIVESERVICES)

        body = {
            "maps": [
                {
                    "mapUid": mapuid,
                    "groupUid": "Personal_Best"
                }
            ]
        }

        res = self.send_post_request("live-services.trackmania.nadeo.live",
                                     "/api/token/leaderboard/group/map?scores[{}]={}".format(mapuid, sys.maxsize), body)
        print(res)
        return res

    def update_tokens(self, tokens: dict) -> None:
        self.headers[RequestKeys.ACCESSTOKEN.value] = tokens.get(RequestKeys.ACCESSTOKEN.value)
        self.headers[RequestKeys.REFRESHTOKEN.value] = tokens.get(RequestKeys.REFRESHTOKEN.value)

    def is_authenticated(self) -> bool:
        return RequestKeys.ACCESSTOKEN not in self.headers
