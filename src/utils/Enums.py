from enum import StrEnum

class RequestKeys(StrEnum):
    MAPUID = "mapuid"
    AUDIENCE = "audience"
    ERROR = "error"
    ACCESSTOKEN = "accessToken"
    REFRESHTOKEN = "refreshToken"
    CONTENTTYPE = 'Content-Type'
    AUTHORIZATION = 'Authorization'
    USERAGENT = 'User-Agent'
    UBIAPPID ='Ubi-AppId'
    MESSAGE = "message"


class NadeoResponsesKeys(StrEnum):
    ERRORCODE = "errorCode"
    MESSAGE = "message"
    TICKET = "ticket"

class Audiences(StrEnum):
    NADEOSERVICES = "NadeoServices"
    NADEOLIVESERVICES = "NadeoLiveServices"
    NADEOCLUBSERVICES = "NadeoClubServices"

class Methods(StrEnum):
    POST = "POST"
    GET = "GET"