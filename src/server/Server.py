from flask import Flask
import http.client, traceback
import json, sys, base64
from src.utils.Enums import *
from src.utils.Functions import prepare_to_send
from os.path import abspath


class Server(Flask):

    headers = {
        RequestKeys.CONTENTTYPE: 'application/json',
        #RequestKeys.REFRESHTOKEN: "", They don't exist on startup
        #RequestKeys.ACCESSTOKEN: "",
        RequestKeys.USERAGENT: 'How many contenders / howmanycontenders@gmail.com',
        RequestKeys.UBIAPPID: '86263886-327a-4328-ac69-527f0d20a237'
    }

    def __init__(self, name: str):
        super().__init__(name)

    def send_request(self, method: Methods, host: str, path: str, body: dict = None) -> dict:
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
        r = conn.getresponse().read().decode('utf-8')
        return json.loads(r)

    def authenticate(self, audience: Audiences) -> dict:
        """
        This method authenticates the server to nadeo services with the specified audience.

        Use the Audiences enumeration available at src/utils/Enums.py to specify the audience.
        """
        try:

            authorization = open("src/utils/authenticate.txt", 'r', encoding='utf-8').read()
            self.headers[RequestKeys.AUTHORIZATION] = 'Basic {}'.format(
                base64.b64encode(authorization.encode('ascii')).decode('ascii'))

            response = self.send_request(Methods.POST, 'public-ubiservices.ubi.com', '/v3/profiles/sessions')

            if response.get(NadeoResponsesKeys.TICKET) is None:
                if not response.get(NadeoResponsesKeys.ERRORCODE) is None:
                    print("API error : "+str(response), file=sys.stderr)
                    message = response.get(NadeoResponsesKeys.MESSAGE)
                else:
                    message = "Unknown error"
                return {RequestKeys.ERROR: message}

            body = {RequestKeys.AUDIENCE.value: audience.value}

            self.headers[RequestKeys.AUTHORIZATION] = 'ubi_v1 t={}'.format(response["ticket"])

            response = self.send_request(Methods.POST, "prod.trackmania.core.nadeo.online",
                                         "/v2/authentication/token/ubiservices", body)

            self.update_tokens(response)

            return response

        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            return {RequestKeys.ERROR.value: traceback.format_exc()}

    def refresh_token(self) -> None:
        """
        This method allows to get a new refresh token once the old one is not active anymore.
        """
        if self.headers.get(RequestKeys.REFRESHTOKEN) is None:
            raise ConnectionError("The server needs to be authenticated before refreshing it's tokens")

        self.headers[RequestKeys.AUTHORIZATION] = "nadeo_v1 t={}".format(self.headers.get(RequestKeys.REFRESHTOKEN))
        tokens = self.send_request(Methods.POST, "prod.trackmania.core.nadeo.online",
                                   "/v2/authentication/token/refresh")
        self.update_tokens(tokens)

    def get_player_count(self, mapuid: str):
        """
        This method gets the total count of players that played the specified map.

        This is got done by calling the Nadeo Live services route : https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/map?scores[<mapuid>]=<integerMaxValue>
        """
        host = "live-services.trackmania.nadeo.live"
        path = "/api/token/leaderboard/group/map?scores[{}]={}".format(mapuid, sys.maxsize)
        body = {
            "maps": [
                {
                    "mapUid": mapuid,
                    "groupUid": "Personal_Best"
                }
            ]
        }
        response = self.send_request(Methods.POST, host, path, body)

    def update_tokens(self, tokens: dict) -> None:
        self.headers[RequestKeys.ACCESSTOKEN] = tokens.get(RequestKeys.ACCESSTOKEN)
        self.headers[RequestKeys.REFRESHTOKEN] = tokens.get(RequestKeys.REFRESHTOKEN)
