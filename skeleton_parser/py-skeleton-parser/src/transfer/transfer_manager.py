import json
import logging
import socket
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class TransferManager:
    def __init__(self, args):
        with open('./etc/config.json', 'r') as f:
            config = json.load(f)
        self.__camid = config["camid"]
        self.__addr = config["addr"]
        self.__port = config["port"]
        self.__args = args

        logging.info("[CONFIG] cam id: {}, addr: {}, port: {}".format(self.__camid, self.__addr, self.__port))

    def initialize(self):
        self.__socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_result(self, keypoint, depth, color):
        if keypoint == None:
            return
        data = self.get_data_from_result(keypoint, depth, color)
        logging.debug(data)
        # print(data)
        json_data = json.dumps(data, cls=NpEncoder)
        self.__socket.sendto(bytes(json_data, "utf-8"), (self.__addr, self.__port))

    def get_data_from_result(self, keypoint, depth, color):
        data = {}
        data['id'] = self.__camid
        data['model'] = self.__args.model
        data['resolution'] = self.__args.resolution
        data['annots'] = []

        for kp in keypoint['annots']:
            annots = {}
            annots['personID'] = kp['personID']
            annots['keypoints'] = kp['keypoints']
            annots['bbox'] = kp['bbox']
            kp_id = annots['personID']

            if depth != None:
                for dp in depth['annots']:
                    dp_id = dp['personID']
                    if kp_id == dp_id:
                        annots['position'] = dp['position']
                        break
            if color != None:
                for cp in color['annots']:
                    cp_id = cp['personID']
                    if kp_id == cp_id:
                        annots['cloth'] = cp['cloth']
                        break
            data['annots'].append(annots)

        return data
