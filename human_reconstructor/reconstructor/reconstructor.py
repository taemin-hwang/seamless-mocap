
#from easymocap.dataset import CONFIG, MV1PMF
from easymocap.mytools.camera_utils import read_camera, get_fundamental_matrix, Undistort
from easymocap.mytools.reconstruction import simple_recon_person


import os
from os.path import join
import numpy as np

# MVBase
class CameraCalibration:
    def read_camera(self, num, path):
        intri_name = join(path, 'intri.yml')
        extri_name = join(path, 'extri.yml')
        if os.path.exists(intri_name) and os.path.exists(extri_name):
            self.cameras = read_camera(intri_name, extri_name)
            self.cameras.pop('basenames')
            cams = np.array(range(1, num+1)).astype(str)
            #cams = self.cams
            self.cameras_for_affinity = [[cam['invK'], cam['R'], cam['T']] for cam in [self.cameras[name] for name in cams]]
            self.Pall = np.stack([self.cameras[cam]['P'] for cam in cams])
            self.Fall = get_fundamental_matrix(self.cameras, cams)
        else:
            print('\n!!!\n!!!there is no camera parameters, maybe bug: \n', intri_name, extri_name, '\n')
            self.cameras = None

class Reconstructor:
    def __init__(self):
        self.cali = CameraCalibration()
        self.skeletons = {} # {cam_id : [], cam_id : []}
        self.skeletons_test = {} # {cam_id : [], cam_id : []}
        self.last_timestamp = 0.0

    def initialize(self, num, path):
        self.cali.read_camera(num, path)
        self.cam_num = num
        self.valid_index = { i:False for i in range(self.cam_num) } # {0: False, 1: False, 2: False, 3: False}

    def clear_valid_index(self):
        self.valid_index = { i:False for i in range(self.cam_num) } # {0: False, 1: False, 2: False, 3: False}

    def set_2d_skeletons(self, _skeletons):
        '''collect 2d skeletons'''
        cam_id = _skeletons['id']
        timestamp = _skeletons['timestamp']
        annots = np.array(_skeletons['annots'][0]['keypoints'])
        self.valid_index[cam_id] = True
        self.skeletons[cam_id] = {'timestamp' : timestamp, 'annots' : annots}
        print('Received 2d skeleton from cam id : ', cam_id)

    def get_3d_skeletons(self):
        '''reconstruct 3d human from 2d skeletons'''
        valid_index = [v for v in self.valid_index.values() if v == True]
        if (len(valid_index) < 4):
            #print('cannot reconstruct, num of skeleton is less than 2')
            return []

        #keypoints_use = np.stack([self.skeletons[id+1]['annots'] for id, item in enumerate(valid_index) if item == True ])
        ##p_use = self.cali.Pall
        #p_use = np.stack([self.cali.cameras[str(id+1)]['P'] for id, item in enumerate(valid_index) if item == True ])
        #keypoints3d, kpts_repro = simple_recon_person(keypoints_use, p_use)
        #self.clear_valid_index()


        keypoints_use = np.stack([self.skeletons[id]['annots'] for id in self.skeletons ])
        p_use = self.cali.Pall
        keypoints3d, kpts_repro = simple_recon_person(keypoints_use, p_use)

        return keypoints3d

    # NOTE: ONLY FOR INTERNAL TEST
    def set_2d_skeletons_test(self, _cam_id, _skeletons):
        '''collect 2d skeletons'''
        annots = np.array(_skeletons['people'][0]['pose_keypoints_2d'])
        annots_reshape = np.reshape(annots, (25, 3))
        self.skeletons_test[_cam_id] = {'annots' : annots_reshape}

    # NOTE: ONLY FOR INTERNAL TEST
    def get_3d_skeletons_test(self):
        '''reconstruct 3d human from 2d skeletons'''
        keypoints_use = np.stack([self.skeletons_test[id]['annots'] for id in self.skeletons_test ])
        p_use = self.cali.Pall
        keypoints3d, kpts_repro = simple_recon_person(keypoints_use, p_use)
        return keypoints3d
