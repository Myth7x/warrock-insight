import threading
import time
import pydivert
import logging
import ctypes

from packet_handler import PacketHandler
ph = None


def main():
    global ph
    logging.basicConfig(level=logging.DEBUG)
    ph = PacketHandler()
    logging.info("Starting..")
    while True:
        try:
            with pydivert.WinDivert("tcp.SrcPort == 10375") as w:
                for packet in w:
                    w.send(ph.handle(time.time(), packet))
        except KeyboardInterrupt: break
        except Exception as e:
            logging.error(e)
            time.sleep(1)
        logging.info("Restarting..")
    logging.info("Exiting..")


if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logging.error("Please run as administrator.")
        exit(1)
    main()
