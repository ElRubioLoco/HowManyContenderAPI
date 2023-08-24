from flask import Flask, request, Response, json
import werkzeug.exceptions
from src.utils.Enums import *
from src.server.Server import Server
from src.utils.Functions import prepare_to_send

app = Server("HMC_API")


@app.route("/authenticate", methods=[Methods.GET])
def authenticate():
    res = app.authenticate(Audiences.NADEOLIVESERVICES)
    if not res.get(RequestKeys.ERROR.value) is None:
        return handle_internal_server_error(res.get(RequestKeys.ERROR.value))
    return Response(prepare_to_send({RequestKeys.MESSAGE: "The server is now authenticated to Nadeo live services"}), 200)


@app.route("/refresh-tokens", methods=[Methods.GET])
def refresh_tokens():
    try:
        app.refresh_token()
        return Response(prepare_to_send({RequestKeys.MESSAGE: "The server refreshed is authentication tokens successfully"}), 200)
    except ConnectionError as err:
        return Response(prepare_to_send({RequestKeys.MESSAGE: str(err)}))


### Map ###

@app.route("/how-many-contenders", methods=[Methods.POST])
def get_map_player_count():
    mapuid = request.form[RequestKeys.MAPUID]
    player_count = app.get_player_count(mapuid)
    if RequestKeys.ERROR in player_count.keys():
        return Response(prepare_to_send(player_count), 500)
    print(request.origin, "asked for player count of", mapuid)
    return Response(prepare_to_send(player_count), 200)


### Campaign ###
# This one is for future implementations and improvements

### Error handlers ###

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'Bad request !\n' + str(e), 400


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found(e):
    return 'Route or file not found !\n' + str(e), 404


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    return 'Internal server error !\n' + str(e), 500


if __name__ == "__main__":
    app.run('localhost', 8001, False)
