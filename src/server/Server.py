from flask import Flask
import http.client, traceback
import json, sys, base64
from src.utils.Enums import *
from src.utils.Functions import prepare_to_send
from os.path import abspath




class Server(Flask):

    def __init__(self, name: str):
        super().__init__(name)

    def send_request(self, method: Methods, host: str, path: str, body: dict, headers: dict) -> dict:
        conn = http.client.HTTPSConnection(host, 443)
        body = prepare_to_send(body)
        conn.request(method, path, body=body, headers=headers)  # <---
        r = conn.getresponse().read().decode('utf-8')
        return json.loads(r)

    def authenticate(self, audience: Audiences) -> dict:
        try:
            authorization = open("src/utils/authenticate.txt", 'r', encoding='utf-8').read()
            req_headers = {
                'Content-Type': 'application/json',
                'Ubi-AppId': '86263886-327a-4328-ac69-527f0d20a237',
                'Authorization': 'Basic {}'.format(base64.b64encode(authorization.encode('ascii')).decode('ascii')),
                'User-Agent': 'How many contenders / martin2001.cornumansuy@gmail.com'
            }
            response = self.send_request(Methods.POST, 'public-ubiservices.ubi.com', '/v3/profiles/sessions', {}, req_headers)
            if response.get("ticket") is None:
                print("Bad token", file=sys.stderr)
                exit(1)
            print("Token ok")
            body = {
                RequestKeys.AUDIENCE.value: audience.value
            }
            req_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'ubi_v1 t={}'.format(response["ticket"])
            }
            response = self.send_request(Methods.POST, "prod.trackmania.core.nadeo.online", "/v2/authentication/token/ubiservices", body, req_headers)

            return response
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            return {RequestKeys.ERROR.value: traceback.format_exc()}

    def get_player_count(self, param):
        pass
