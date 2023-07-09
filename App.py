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
    return Response(prepare_to_send(res), 200)


### Map ###

@app.route("/map/playerCount", methods=[Methods.POST])
def get_map_player_count():
    return Response(app.get_player_count(request.form[RequestKeys.MAPID]))


### Campaign ###
# This one is for future implementations and improvements

### Error handlers ###

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'Bad request !\n'+str(e), 400

@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found(e):
    return 'Route or file not found !\n'+str(e), 404

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    return 'Internal server error !\n'+str(e), 500


if __name__ == "__main__":
    app.run('localhost', 8001, False)
