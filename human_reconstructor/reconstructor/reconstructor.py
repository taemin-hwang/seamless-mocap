
#from easymocap.dataset import CONFIG, MV1PMF
from easymocap.mytools.camera_utils import read_camera, get_fundamental_matrix, Undistort
from easymocap.mytools.reconstruction import simple_recon_person, batch_triangulate
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
        self.skeletons_test = {} # {cam_id : [], cam_id : []}
        self.last_timestamp = 0.0

    def initialize(self, args, config):
        if args.test1 is True:
            self.cam_num = 23
            self.cali.read_camera(self.cam_num, './etc/mv1p_data')
        elif args.test2 is True:
            self.cam_num = 4
            self.cali.read_camera(self.cam_num, './etc/keti_mv1p_data')
        elif args.test3 is True:
            self.cam_num = 4
            self.cali.read_camera(self.cam_num, './etc/sgu_mv1p_data')
        else:
            self.cam_num = config["cam_num"]
            self.cali.read_camera(self.cam_num, args.path)

        self.body_model = load_model(model_path='./easymocap/data/smplx')

    def get_cameras(self):
        return self.cali.cameras

    def check_repro_error(self, keypoints3d, kpts_repro, keypoints2d, P, MAX_REPRO_ERROR=100):
        #square_diff = (keypoints2d[:, :, :2] - kpts_repro[:, :, :2])**2
        conf = keypoints3d[None, :, -1:]
        conf = (keypoints3d[None, :, -1:] > 0) * (keypoints2d[:, :, -1:] > 0)
        dist = np.sqrt((((kpts_repro[..., :2] - keypoints2d[..., :2])*conf)**2).sum(axis=-1))
        vv, jj = np.where(dist > MAX_REPRO_ERROR)
        if vv.shape[0] > 0:
            keypoints2d[vv, jj, -1] = 0.
            keypoints3d, kpts_repro = simple_recon_person(keypoints2d, P)
        return keypoints3d, kpts_repro

    def get_3d_skeletons(self, keypoints_use, p_use):
        '''reconstruct 3d human from 2d skeletons'''
        keypoints3d, kpts_repro = simple_recon_person(keypoints_use, p_use)
        #keypoints3d, kpts_repro = self.check_repro_error(keypoints3d, kpts_repro, keypoints_use, p_use, 100)
        #keypoints3d = batch_triangulate(keypoints_use, p_use)
        return keypoints3d

    # NOTE: ONLY FOR INTERNAL TEST
    def set_2d_skeletons_test(self, _cam_id, _skeletons):
        '''collect 2d skeletons'''
        annots = np.array(_skeletons['people'][0]['pose_keypoints_2d'])
        annots_reshape = np.reshape(annots, (25, 3))
        self.skeletons_test[_cam_id] = {'annots' : annots_reshape}

    # NOTE: ONLY FOR INTERNAL TEST
    def set_2d_skeletons_test2(self, _cam_id, _skeletons):
        '''collect 2d skeletons'''
        annots_reshape = np.reshape(_skeletons, (25, 3))
        self.skeletons_test[_cam_id] = {'annots' : annots_reshape}

    # NOTE: ONLY FOR INTERNAL TEST
    def set_2d_skeletons_test3(self, _cam_id, _skeletons):
        '''collect 2d skeletons'''
        annots_reshape = np.reshape(_skeletons, (25, 3))
        self.skeletons_test[_cam_id] = {'annots' : annots_reshape}

    # NOTE: ONLY FOR INTERNAL TEST
    def get_3d_skeletons_test(self):
        '''reconstruct 3d human from 2d skeletons'''
        keypoints_use = np.stack([self.skeletons_test[id]['annots'] for id in self.skeletons_test ])
        p_use = self.cali.Pall
        #keypoints3d, kpts_repro = simple_recon_person(keypoints_use, p_use)
        keypoints3d = batch_triangulate(keypoints_use, p_use)
        return keypoints3d
