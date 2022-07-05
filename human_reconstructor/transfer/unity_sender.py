import numpy as np
import json
import socket

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class UnitySender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

    def initialize(self, ipaddr, port):
        self.ipaddr = ipaddr
        self.port = port

    def send_3d_skeletons(self, skeletons):
        data = []
        data.append({})
        data[0]['id'] = 0
        data[0]['keypoints3d'] = skeletons
        json_data = json.dumps(data, cls=NumpyEncoder)
        self.sock.sendto(bytes(json_data, "utf-8"), (self.ipaddr, self.port))
