
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

    def clear_valid_index(self):
        self.valid_index = { i:False for i in range(self.cam_num) } # {0: False, 1: False, 2: False, 3: False}

    def set_2d_skeletons(self, _skeletons):
        '''collect 2d skeletons'''
        cam_id = _skeletons['id']
        timestamp = _skeletons['timestamp']

        annots = np.array(_skeletons['annots'][0]['keypoints'])
        annots_25 = utils.convert_25_from_34(annots)

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

        #print('-------------------------keypoints 2d--------------------------')
        #print(keypoints_use)
        #print('-------------------------Pall----------------------------------')
        #print(p_use)
        #print('-------------------------keypoints 3d--------------------------')
        #print(keypoints3d)
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
        #print('-------------------------keypoints 2d--------------------------')
        #print(keypoints_use)
        #print('-------------------------Pall----------------------------------')
        #print(p_use)
        #print('-------------------------keypoints 3d--------------------------')
        #print(keypoints3d)

        return keypoints3d


    # NOTE: ONLY FOR INTERNAL TEST
    def get_smpl_init_test(self):
        self.body_model = load_model(model_path='./easymocap/data/smplx')
        self.frame_num_test = 0
        self.kp3ds = np.empty((0, 25, 4))

    def get_smpl_test(self, keypoints3d):
        from datetime import datetime
        from easymocap.dataset import CONFIG
        from easymocap.pipeline.weight import load_weight_pose, load_weight_shape
        from easymocap.pyfitting import optimizeShape
        from easymocap.pipeline.basic import multi_stage_optimize
        from easymocap.pipeline.config import Config

        if(self.frame_num_test < 100):
            self.kp3ds = np.append(self.kp3ds, keypoints3d.reshape(1, 25, 4), axis=0)
            #self.kp3ds = np.array(self.kp3ds)
            #print(self.kp3ds.shape)
            self.frame_num_test += 1
            return {}
        else:
            print(self.kp3ds.shape)

            time1 = datetime.now()
            #params = smpl_from_keypoints3d2d(body_model, kp3ds, keypoints2d, bboxes, dataset.Pall, config=dataset.config, args=args, weight_shape=None, weight_pose=None)
            #body_model = load_model(model_path='./easymocap/data/smplx')
            model_type = self.body_model.model_type
            params_init = self.body_model.init_params(nFrames=1)
            weight_shape = load_weight_shape(model_type, opts={})
            if model_type in ['smpl', 'smplh', 'smplx']:
                # when use SMPL model, optimize the shape only with first 1-14 limbs,
                # don't use (nose, neck)
                params_shape = optimizeShape(self.body_model, params_init, self.kp3ds,
                    weight_loss=weight_shape, kintree=CONFIG['body15']['kintree'][1:])
            else:
                print('cannot find model type')
            time2 = datetime.now()

            cfg = Config()
            cfg.device = self.body_model.device

            # optimize 3D pose
            params = self.body_model.init_params(nFrames=self.kp3ds.shape[0])
            params['shapes'] = params_shape['shapes'].copy()
            weight_pose = load_weight_pose(model_type, opts={})
            time3 = datetime.now()

            # We divide this step to two functions, because we can have different initialization method
            params = multi_stage_optimize(self.body_model, params, self.kp3ds, None, None, None, weight_pose, cfg)
            time4 = datetime.now()

            print("- Load model : ", time2-time1)
            print("- Init param : ", time3-time2)
            print("- Optimize 3D pose : ", time4-time3)

            self.kp3ds = np.empty((0, 25, 4))
            self.frame_num_test = 0

            return params
