import numpy as np
import time

COLOR_TEAM_0_7  = (255, 0, 0)
COLOR_TEAM_8_15 = (255, 255, 0)

class Player:

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.position_history = []

    def update_position(self, x, y):
        if self.x == x and self.y == y or x == 0 and y == 0:
            return
        self.position_history.append((self.x, self.y, time.time()))
        self.x = x
        self.y = y

    def get_id(self):
        return self.id

    def get_position(self):
        return self.x, self.y

    def get_position_history(self, num, order="desc"):
        history = []
        if order == "desc":
            for i in range(min(num, len(self.position_history))):
                history.append(self.position_history[-i])
        else:
            for i in range(min(num, len(self.position_history))):
                history.append(self.position_history[i])
        return history

    def distance_to(self, x, y):
        return np.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def get_color(self):
        return COLOR_TEAM_0_7 if self.id < 8 else COLOR_TEAM_8_15


class PacketHandler(object):

    def __init__(self):
        self.players = {}

    def player_exists(self, pid):
        return pid in self.players

    def handle_packet(self, packet):
        if packet.is_outbound:
            return packet

        # 1. handle game update packet
        packet = self.handle_game_update(packet)

        return packet

    def handle_game_update(self, packet):
        _payload = packet.payload
        _payload = list(bytes(_payload))
        if len(_payload) < 23:  # if smaller then 23, no udp game update packet (scuffed but works)
            return packet

        _x = int.from_bytes(_payload[22:25], "big")
        _y = int.from_bytes(_payload[28:31], "big")

        pid = _payload[8]  # player id from update packet

        if _x == 0 and _y == 0 or not pid:
            return packet

        if not self.player_exists(pid):
            self.players[pid] = Player(pid, _x, _y)
        else:
            self.players[pid].update_position(_x, _y)

        return packet
