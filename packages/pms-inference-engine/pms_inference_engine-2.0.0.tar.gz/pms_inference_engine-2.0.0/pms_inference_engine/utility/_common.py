from .._dependency import *


def create_uuid() -> str:
    return str(uuid.uuid1())
