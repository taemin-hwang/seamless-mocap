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

    def send_3d_skeletons(self, skeletons):
        data = []
        data.append({})
        data[0]['id'] = 0
        data[0]['keypoints3d'] = skeletons
        self.client.send(data)