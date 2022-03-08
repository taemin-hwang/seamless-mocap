
#from easymocap.dataset import CONFIG, MV1PMF
from easymocap.mytools.camera_utils import read_camera, get_fundamental_matrix, Undistort
from easymocap.mytools.reconstruction import simple_recon_person
from easymocap.pipeline import smpl_from_keypoints3d2d, smpl_from_keypoints3d
from easymocap.smplmodel import check_keypoints, load_model, select_nf

from visualizer import utils

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
        self.body_model = load_model(model_path='./easymocap/data/smplx')
        self.kp3ds = np.empty((0, 25, 4))
        self.frame_num_test = 0

    def clear_valid_index(self):
        self.valid_index = { i:False for i in range(self.cam_num) } # {0: False, 1: False, 2: False, 3: False}

    def set_2d_skeletons(self, _skeletons):
        '''collect 2d skeletons'''
        cam_id = _skeletons['id']
        timestamp = _skeletons['timestamp']

        annots = np.array(_skeletons['annots'][0]['keypoints'])
        annots_25 = utils.convert_25_from_34(annots)

        self.valid_index[cam_id] = True
        self.skeletons[cam_id] = {'timestamp' : timestamp, 'annots' : annots_25}
        #print(self.skeletons[cam_id])
        print('Received 2d skeleton from cam id : ', cam_id)

    def get_3d_skeletons(self):
        '''reconstruct 3d human from 2d skeletons'''
        valid_index = [v for v in self.valid_index.values() if v == True]
        if (len(valid_index) < 4):
            #print('cannot reconstruct, num of skeleton is less than 2')
            return []

        keypoints_use = np.stack([self.skeletons[id]['annots'] for id in self.skeletons ])
        p_use = self.cali.Pall

        keypoints3d, kpts_repro = simple_recon_person(keypoints_use, p_use)
        return keypoints3d

    def get_smpl_bunch(self, kp3ds):
        from datetime import datetime
        from easymocap.dataset import CONFIG
        from easymocap.pipeline.weight import load_weight_pose, load_weight_shape
        from easymocap.pyfitting import optimizeShape
        from easymocap.pipeline.basic import multi_stage_optimize
        from easymocap.pipeline.config import Config

        self.kp3ds = kp3ds

        print(self.kp3ds.shape)
        if self.kp3ds.shape[0] < 1:
            return

        model_type = self.body_model.model_type
        cfg = Config()
        cfg.device = self.body_model.device

        # optimize 3D pose
        params = self.body_model.init_params(nFrames=self.kp3ds.shape[0])
        params['shapes'] = np.array([[ 0.15387063, -0.19116399,  0.07848503,  0.18847144,  0.03092081,0.03787636, -0.01424125, -0.02344685,  0.014108  , -0.01093242]])
        weight_pose = load_weight_pose(model_type, opts={})

        # We divide this step to two functions, because we can have different initialization method
        params = multi_stage_optimize(self.body_model, params, self.kp3ds, None, None, None, weight_pose, cfg)

        self.kp3ds = np.empty((0, 25, 4))
        self.frame_num_test = 0

        return params

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
