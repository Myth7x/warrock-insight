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

    def update_position(self, _time, x, y) -> None:
        if self.x == x and self.y == y or x == 0 and y == 0:
            return
        self.position_history.append((self.x, self.y, _time))
        self.last_update = _time
        self.x = x
        self.y = y

    def get_id(self) -> int:
        return self.id

    def get_position(self) -> tuple:
        return self.x, self.y

    def get_position_history(self, num, order="desc") -> list:
        history = []
        if order == "desc":
            for i in range(min(num, len(self.position_history))):
                history.append(self.position_history[-i])
        else:
            for i in range(min(num, len(self.position_history))):
                history.append(self.position_history[i])
        return history

    def distance_to(self, x, y) -> float:
        return np.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def get_team(self) -> int:
        return 0 if self.id < 8 else 1

    def get_color(self) -> tuple:
        return COLOR_TEAM_0_7 if self.id < 8 else COLOR_TEAM_8_15


class PacketHandler(object):
    def __init__(self):
        self.players = {}

    def player_exists(self, _id) -> bool:
        return _id in self.players

    def handle(self, _time, _packet) -> object:
        if _packet.is_outbound:
            return _packet

        def _game_update(_self, _time, _packet) -> object:
            _payload = _packet.payload
            _payload = list(bytes(_payload))
            if len(_payload) < 23:  # if len < 23, no udp game update packet
                return _packet

            try:
                _x = int.from_bytes(_payload[22:25], "big")
            except Exception as e:
                logging.error(e)
                return _packet

            try:
                _y = int.from_bytes(_payload[28:31], "big")
            except Exception as e:
                logging.error(e)
                return _packet

            try:
                _id = _payload[8]
            except Exception as e:
                logging.error(e)
                return _packet

            if _x == 0 and _y == 0 or not _id:
                return _packet

            if not _self.player_exists(_id):
                _self.players[_id] = Player(_id, _x, _y)
            else:
                _self.players[_id].update_position(_time, _x, _y)
                
            return _packet
        packet = _game_update(self, _time, _packet)

        return packet


