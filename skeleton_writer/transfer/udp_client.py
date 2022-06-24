import socket
import json
import numpy as np

class UdpClient:
    def __init__(self, ipaddr, port):
        self.__server_addr_port   = (ipaddr, port)
        self.__socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def __append_annot(self, annots, person_id, face_status, hand_status):
        annot = {}
        annot['personID'] = person_id
        annot['faceStatus'] = face_status
        annot['handStatus'] = hand_status
        annots.append(annot)
        return annots

    def send_data(self, face_status, hand_status):
        data = {}
        data['annots'] = []
        data['annots'] = self.__append_annot(data['annots'], 0, face_status, hand_status)
        json_data = json.dump(data)
        self.__socket.sendto(bytes(json_data, "utf-8"), self.__server_addr_port)