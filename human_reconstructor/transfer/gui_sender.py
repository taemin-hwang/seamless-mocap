from easymocap.socket.base_client import BaseSocketClient
import numpy as np
import json
import time
import threading
from queue import Queue

class GuiSender:
    def __init__(self):
        self.lock = threading.Lock()
        self.mq = Queue()

    def initialize(self, host, port):
        print("[GUI    IP  ] : ", host)
        print("[GUI    PORT] : ", port)
        self.client = BaseSocketClient(host, port)

    def send_3d_skeletons(self, data):
        # print(data)
        self.client.send(data)