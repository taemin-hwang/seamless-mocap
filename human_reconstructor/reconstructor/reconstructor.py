
#from easymocap.dataset import CONFIG, MV1PMF
from easymocap.mytools.camera_utils import read_camera, get_fundamental_matrix, Undistort
from easymocap.mytools.reconstruction import simple_recon_person


import os
from os.path import join
import numpy as np

# MVBase
class CameraCalibration:
    def read_camera_test(self, num, path):
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

    def set_2d_skeletons(self, _skeletons):
        '''collect 2d skeletons'''
        cam_id = _skeletons['id']
        timestamp = _skeletons['timestamp']
        annots = _skeletons['annots']
        self.skeletons[cam_id] = {'timestamp' : timestamp, 'annots' : annots}
        self.last_timestamp = timestamp

    def get_3d_skeletons(self):
        '''reconstruct 3d human from 2d skeletons'''
        for skeleton in self.skeletons:
            if self.last_timestamp - skeleton['timestamp'] > 300: # exceed 300ms
                del skeleton
        
        if len(self.skeletons) < 3:
            print("number of 2d skeletons is less than 3 : ", len(self.skeletons))
            return

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