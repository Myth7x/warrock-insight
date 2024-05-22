from enum import Enum


class PacketHeader(Enum):
    UNKNOWN = 0

    CHAT_RECV = 116

    PING_1 = 100

    UPDATE_1 = 49

    SPAWN = 12405
