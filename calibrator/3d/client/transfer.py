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

    def send_3d_skeleton(self, data):
        json_data = json.dumps(data, cls=NumpyEncoder)
        self.sock.sendto(bytes(json_data, "utf-8"), (self.ipaddr, self.port))


#from easymocap.socket.base_client import BaseSocketClient
#
#class GuiSender:
#    def __init__(self):
#        pass
#
#    def initialize(self, ipaddr, port):
#        self.client = BaseSocketClient(ipaddr, port)
#
#    def send_3d_skeleton(self, data):
#        self.client.send(data)
