from enum import StrEnum

class RequestKeys(StrEnum):
    MAPID = "mapuid"
    AUDIENCE = "audience"
    ERROR = "error"

class Audiences(StrEnum):
    NADEOSERVICES = "NadeoServices"
    NADEOLIVESERVICES = "NadeoLiveServices"
    NADEOCLUBSERVICES = "NadeoClubServices"

class Methods(StrEnum):
    POST = "POST"
    GET = "GET"