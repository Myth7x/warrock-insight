import threading, time

import cv2
import numpy as np
import pydivert

from .packet_handler    import PacketHandler
from .types             import PacketHeader


import logging
logging.basicConfig(level=logging.DEBUG)


ph = PacketHandler()


positions = {}
position_history = {}


def main():
    global ph

    logging.basicConfig(level=logging.DEBUG)
    with pydivert.WinDivert("tcp.SrcPort == 10375") as w:
        for packet in w:
            packet, state = ph.handle_packet(packet)
            if state:
                w.send(packet)

    logging.debug("Exiting")


def draw_positions():  # deprecated, will be replaced in the future
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


if __name__ == "__main__":
    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=draw_positions)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
