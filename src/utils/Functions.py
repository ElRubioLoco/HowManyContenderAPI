import json


def prepare_to_send(senddict: dict) -> bytes:
    return json.dumps(senddict).encode("utf-8")
