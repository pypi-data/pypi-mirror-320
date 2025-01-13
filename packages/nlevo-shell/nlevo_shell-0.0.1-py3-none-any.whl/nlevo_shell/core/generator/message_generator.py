from time import time
from nlevoutils.constant import ServiceType, MessageType


def setup_message(service=ServiceType.SVC_DEVCTRL, e=None) -> dict:
    if e is not None:
        return {
            "msg": MessageType.SETUP_REQ,
            "service": service,
            "level": "error",
            "time": time(),
            "data": {"exception": {e}},
        }
    else:
        return {
            "msg": MessageType.SETUP_REQ,
            "service": service,
            "level": "info",
            "time": time(),
            "data": {"type": "all"},
        }
