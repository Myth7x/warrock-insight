import pydivert
import logging
import threading
import time
import random

import cv2
import numpy as np

logging.basicConfig(level=logging.DEBUG)


from enum import Enum
class PacketHeader(Enum):
    UNKNOWN = 0

    CHAT_RECV = 116

    PING_1 = 100

    UPDATE_1 = 49

    SPAWN = 12405


class PacketHandler:

    @staticmethod
    def recv_12405(packet):
        """
        Packet 12405 (Player Spawn)
        :param packet:
        :return packet, state:
        """
        _payload = packet.payload
        _rest = _payload[12:]
        edit_pos = [35]#[35, 36, 37, 38, 39, 40, 41, 42, 43]
        for c in edit_pos:
            at_pos = _rest[c]
            end = 0 if at_pos == 2 else 2
            if at_pos != 2 and at_pos != 0 and _rest[c+1] != 0:
                print("Invalid value")
                return packet, True

            print(c, at_pos)
            _rest = _rest[:c] + bytes([end]) + _rest[c + 1:]
        #print(_rest)
        _payload = _payload[:12] + _rest
        packet.payload = bytes(_payload)
        return packet, True


ph = PacketHandler()


positions = {}
position_history = {}

def handle_packet(packet):
    global positions

    _payload = packet.payload
    _payload = list(bytes(_payload))
    if len(_payload) < 23: # if smaller then 23, no udp game update packet (scuffed but works)
        return packet, True

    _x = int.from_bytes(_payload[22:25], "big")
    _y = int.from_bytes(_payload[28:31], "big")


    pid = _payload[8] # player id from update packet

    if _x == 0 and _y == 0:
        return packet, True

    positions[pid] = (_x, _y)


    return packet, True


def main():
    logging.basicConfig(level=logging.DEBUG)
    with pydivert.WinDivert("tcp.SrcPort == 10375") as w:
        for packet in w:
            packet, state = handle_packet(packet)
            if state:
                w.send(packet)
    logging.debug("Exiting")



def draw_positions():
    global positions
    while True:
        img = np.zeros((800, 800, 3), np.uint8)
        for pid in position_history:
            if position_history[pid] is None:
                continue

            for i in range(1, len(position_history[pid])):
                _t, _x, _y = position_history[pid][i]
                if _t < time.time() - 1:
                    continue
                if _x == 0 and _y == 0 and len(position_history[pid]) < 2:
                    continue
                _t2, _x2, _y2 = position_history[pid][i-1]
                cv2.line(img, (_x, _y), (_x2, _y2), (255, 255, 255), 1)

        for pid, pos in positions.items():
            _x, _y = pos

            # translate to 250, 250
            _x = int(_x / 10000000 * 800)
            _y = int(_y / 10000000 * 800)


            if pid == 8:
                print(_x, _y)
            cv2.circle(img, (_x, _y), 5, (255, 255, 255), -1)

            if not pid in position_history:
                position_history[pid] = []
            position_history[pid].append((time.time(), _x, _y))





        cv2.imshow("positions", img)
        cv2.waitKey(1)
        time.sleep(0.1)

import threading

if __name__ == "__main__":
    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=draw_positions)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
