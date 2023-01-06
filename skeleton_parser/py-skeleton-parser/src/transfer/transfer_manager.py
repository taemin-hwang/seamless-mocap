import json
import logging
import socket

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

    def send_result(self, keypoint, depth):
        data = self.get_data_from_result(keypoint, depth)
        logging.debug(data)
        json_data = json.dumps(data)
        self.__socket.sendto(bytes(json_data, "utf-8"), (self.__addr, self.__port))

    def get_data_from_result(self, keypoint, depth):
        data = {}
        data['annots'] = []

        for kp in keypoint['annots']:
            annots = {}
            kp_id = kp['personID']
            for dp in depth['annots']:
                dp_id = dp['personID']
                if kp_id == dp_id:
                    annots['personID'] = kp_id
                    annots['keypoints'] = kp['keypoints']
                    annots['position'] = dp['position']
                    break
            data['annots'].append(annots)

        return data