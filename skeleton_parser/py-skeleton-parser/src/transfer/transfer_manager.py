import json
import logging

class TransferManager:
    def __init__(self):
        with open('./etc/config.json', 'r') as f:
            config = json.load(f)
        self.__camid = config["camid"]
        self.__addr = config["addr"]
        self.__port = config["port"]

        logging.info("[CONFIG] cam id: {}, addr: {}, port: {}".format(self.__camid, self.__addr, self.__port))

    def initialize(self):
        self.__socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_keypoint(self, keypoint):
        data = {}
        data['annots'] = []
        json_data = json.dump(data)
        self.__socket.sendto(bytes(json_data, "utf-8"), (self.__addr, self.__port))