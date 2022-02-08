from easymocap.socket.base_client import BaseSocketClient
import numpy as np
import json
import time

class SkeletonSender:
    def __init__(self):
        self.client = BaseSocketClient('127.0.0.1', 9999)

    def send_3d_skeletons(self, skeletons):
        data = []
        data.append({})
        data[0]['id'] = 0
        data[0]['keypoints3d'] = skeletons
        self.client.send(data)

    def send_smpl(self, smpl):
        #print(smpl)
        data = []
        data.append({})
        data[0]['id'] = 0
        data[0]['Rh'] = np.round(smpl['Rh'].astype(np.float64),3)
        data[0]['Th'] = np.round(smpl['Th'].astype(np.float64),3)
        data[0]['poses'] = np.round(smpl['poses'].astype(np.float64),3)
        data[0]['shapes'] = np.round(smpl['shapes'].astype(np.float64),3)

        self.client.send_smpl(data)

    def send_smpl_bunch(self, smpl):
        for i in range(smpl['Rh'].shape[0]):
            data = []
            data.append({})
            data[0]['id'] = 0
            data[0]['Rh'] = np.round(smpl['Rh'][i].astype(np.float64),3).reshape(1, smpl['Rh'].shape[1])
            data[0]['Th'] = np.round(smpl['Th'][i].astype(np.float64),3).reshape(1, smpl['Th'].shape[1])
            data[0]['poses'] = np.round(smpl['poses'][i].astype(np.float64),3).reshape(1, smpl['poses'].shape[1])
            data[0]['shapes'] = np.round(smpl['shapes'].astype(np.float64),3)
            #print('------')
            #print(data)
            self.client.send_smpl(data)
            time.sleep(0.06)