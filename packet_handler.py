import numpy as np
import time
import logging

COLOR_TEAM_0_7  = (255, 0, 0)
COLOR_TEAM_8_15 = (255, 255, 0)


class Player:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.last_update = time.time()
        self.position_history = []

    def update_position(self, _time, x, y):
        if self.x == x and self.y == y or x == 0 and y == 0:
            return
        self.position_history.append((self.x, self.y, _time))
        self.last_update = _time
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

    def get_team(self):
        return 0 if self.id < 8 else 1

    def get_color(self):
        return COLOR_TEAM_0_7 if self.id < 8 else COLOR_TEAM_8_15


class PacketHandler(object):

    def __init__(self):
        self.players = {}

    def player_exists(self, id):
        return id in self.players

    def handle_packet(self, _time, packet):
        if packet.is_outbound:
            return packet

        packet = self.handle_game_update(_time, packet)  # 1

        return packet

    def handle_game_update(self, _time, packet):
        _payload = packet.payload
        _payload = list(bytes(_payload))
        if len(_payload) < 23:   # if len < 23, no udp game update packet
            return packet

        try:
            _x = int.from_bytes(_payload[22:25], "big")
        except Exception as e:
            logging.error(e)
            return packet

        try:
            _y = int.from_bytes(_payload[28:31], "big")
        except Exception as e:
            logging.error(e)
            return packet

        try:
            id = _payload[8]  # id
        except Exception as e:
            logging.error(e)
            return packet

        if _x == 0 and _y == 0 or not id:
            return packet

        if not self.player_exists(id):
            self.players[id] = Player(id, _x, _y)
        else:
            self.players[id].update_position(_time, _x, _y)

        return packet
