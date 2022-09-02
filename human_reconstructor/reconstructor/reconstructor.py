import numpy as np
import datetime
import time
import json
import pause
import asyncio
import os
import shutil
import copy

from format import face_format, hand_format

from reconstructor.utils import postprocessor as post
from reconstructor import skeletonmanager as sm
from reconstructor import clustermanager as cm
from reconstructor import trackingmanager as tm

from config import file_storage as fs
from visualizer import viewer_2d as v2d

import logging

class Reconstructor:
    def __init__(self, args):
        self.__args = args
        self.__calibration = fs.read_camera('./etc/intri.yml', './etc/extri.yml')
        self.__frame_number = 0
        self.__max_frame_number = 0
        if self.__args.log:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def initialize(self, config):
        self.__config = config
        self.__person_num = 30
        self.__max_person_num = int(self.__args.number)
        self.__cam_num = self.__config["cam_num"]
        self.__min_cam = self.__config["min_cam"]
        self.__target_fps = self.__config["fps"]
        self.__system_interval = 1000/self.__target_fps # milli-seconds
        self.__buffer_size = self.__config["buffer_size"]
        if self.__args.log:
            self.__transformation = fs.read_transformation(self.__args.log + 'transformation.json')
        else:
            self.__transformation = fs.read_transformation('./etc/transformation.json')

        self.__viewer = v2d.Viewer2d(self.__args)
        self.__skeleton_manager = sm.SkeletonManager(self.__args, self.__cam_num, self.__person_num, self.__calibration, self.__viewer)
        self.__cluster_manager = cm.ClusterManager(self.__args, self.__cam_num, self.__person_num, self.__transformation, self.__viewer)
        self.__cluster_manager.initialize()
        self.__tracking_manager = tm.TrackingManager(self.__args, self.__person_num, self.__max_person_num)

        self.__log_dir = "./log"

    def run(self, func_recv_skeleton, func_recv_handface, func_send_skeleton_gui, func_send_skeleton_unity):
        self.__skeleton_mq, self.__skeleton_lk = func_recv_skeleton(self.__config["server_ip"], self.__config["skeleton_port"])
        if self.__args.face:
            hand_face_mq, hand_face_lk = func_recv_handface(self.__config["server_ip"], self.__config["facehand_port"])

        self.__send_skeleton_gui = func_send_skeleton_gui
        self.__send_skeleton_unity = func_send_skeleton_unity

        face_status = face_format.FACE_STATUS.CLOSED
        hand_status = hand_format.HAND_STATUS.RIGHT_CLOSED

        if self.__args.write is True:
            self.__copy_config()

        if self.__args.log:
            self.__max_frame_number = self.__count_log_frames(self.__args.log)

        need_to_skip = False

        while(True):
            t_sleep = datetime.datetime.now()
            # Get 2D skeletons
            if self.__args.log:
                if self.__frame_number >= self.__max_frame_number:
                    self.__frame_number = 0
                # if self.__frame_number >= 430:
                # comm = input(str(self.__frame_number).zfill(6) + "> ")
                self.__skeleton_manager.read_skeleton_table(self.__frame_number, self.__args.log)
                self.__skeleton_manager.update_life_counter()
            else:
                self.__update_skeleton_table()

            # Make clusters
            self.__cluster_manager.update_person_table(self.__skeleton_manager, self.__max_person_num)
            # self.__cluster_manager.update_person_table_with_hint(self.__tracking_manager.get_tracking_table(), self.__max_person_num)
            self.__cluster_manager.show_cluster_result(self.__skeleton_manager, self.__frame_number)

            # Reconstruct 3D skeletons
            triangulate_param = self.__get_triangulate_param()
            reconstruction_list = asyncio.run(self.__reconstruct_3d_pose(triangulate_param))

            # Keep tracking 3D skeletons
            need_to_skip, is_valid_cluster, data = self.__assign_tracking_id(reconstruction_list, triangulate_param)
            self.__cluster_manager.set_skip_to_make_cluster(need_to_skip)
            self.__cluster_manager.save_valid_cluster(is_valid_cluster, self.__frame_number)

            # Assign Hand/Face status
            if self.__args.face is True:
                face_status, hand_status = self.__get_facehand_status(hand_face_lk, hand_face_mq, face_status, hand_status)
                logging.debug("[FACE STATUS] {}".format(face_status.value))
                logging.debug("[HAND STATUS] {}".format(hand_status.value))
                for element in data:
                    element['face'] = face_status.value
                    element['hand'] = hand_status.value

            # Send data if needed
            if len(data) > 0:
                if self.__args.gui is True:
                    self.__send_skeleton_gui(data)
                if self.__args.unity is True:
                    self.__send_skeleton_unity(data)

            # Save data if needed
            if self.__args.write is True:
                self.__save_skeleton_table(face_status.value, hand_status.value)

            self.__skeleton_manager.reset_skeleton_table()
            self.__cluster_manager.reset_cluster_table()

            self.__frame_number += 1

            pause.until(t_sleep.timestamp() + self.__system_interval/1000)

    def __copy_config(self):
        # Read current time
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        # Create log directory
        self.__log_dir = "./log/" + current_time
        try:
            if not os.path.exists(self.__log_dir):
                os.makedirs(self.__log_dir)
        except OSError:
            logging.error("Error: Failed to create the directory.")

        shutil.copyfile('./etc/transformation.json', self.__log_dir + '/transformation.json')
        shutil.copyfile('./etc/config.json', self.__log_dir + '/config.json')

    def __count_log_frames(self, dir):
        count = 0
        for path in os.scandir(dir):
            if path.is_file():
                count += 1
        return count - 2 # transformation.json and config.json

    def __get_triangulate_param(self):
        triangulate_param = {}
        valid_dlt_element = self.__get_valid_dlt_element()
        for person_id in range(0, self.__person_num):
            if valid_dlt_element[person_id]['count'] >= self.__min_cam:
                valid_keypoint = np.stack(valid_dlt_element[person_id]['valid_keypoint'], axis=0)
                valid_p = np.stack(valid_dlt_element[person_id]['valid_P'], axis=0)
                triangulate_param[person_id] = {}
                triangulate_param[person_id]['keypoint'] = valid_keypoint
                triangulate_param[person_id]['P'] = valid_p
                triangulate_param[person_id]['cpid'] = valid_dlt_element[person_id]['cpid']
        return triangulate_param

    def __get_valid_dlt_element(self):
        valid_dlt_element = {}
        for person_id in range(0, self.__person_num):
            valid_dlt_element[person_id] = {}
            valid_dlt_element[person_id]['count'] = 0
            valid_dlt_element[person_id]['valid_keypoint'] = []
            valid_dlt_element[person_id]['valid_P'] = []
            valid_dlt_element[person_id]['cpid'] = []

        for person_id in range(0, self.__person_num):
            if self.__cluster_manager.is_cluster_valid(person_id) is True:
                valid_dlt_element[person_id]['count'] = self.__cluster_manager.get_count(person_id)
                for i in range(valid_dlt_element[person_id]['count']):
                    cpid = self.__cluster_manager.get_cpid(person_id)[i]
                    cid = post.get_cam_id(cpid)
                    pid = post.get_person_id(cpid)
                    if self.__skeleton_manager.is_skeleton_valid(cid, pid) is True:
                        valid_dlt_element[person_id]['cpid'].append(cpid)
                        valid_dlt_element[person_id]['valid_keypoint'].append(self.__skeleton_manager.get_skeleton(cid, pid))
                        valid_dlt_element[person_id]['valid_P'].append(self.__skeleton_manager.get_skeleton_table()[cid]['P'])

        return valid_dlt_element

    def __update_skeleton_table(self):
        self.__skeleton_lk.acquire()
        qsize = self.__skeleton_mq.qsize()

        for i in range(qsize):
            data = self.__skeleton_mq.get()
            data = json.loads(data)
            self.__skeleton_manager.update_skeleton_table(data)
            # self.__skeleton_manager.show_skeleton_keypoint(data)

        self.__skeleton_manager.update_life_counter()
        # self.__skeleton_manager.show_skeleton_position()
        self.__skeleton_lk.release()

    def __save_skeleton_table(self, face_status, hand_status):
        file_path = self.__log_dir + "/" + str(self.__frame_number).zfill(6) + ".json"
        with open(file_path, "w") as outfile:
            skeleton_table = self.__skeleton_manager.get_skeleton_table()
            skeleton_table['hand'] = hand_status
            skeleton_table['face'] = face_status
            json.dump(skeleton_table, outfile)

    def __assign_tracking_id(self, reconstruction_list, triangulate_param):
        return self.__tracking_manager.get_tracking_keypoints(reconstruction_list, triangulate_param)

    async def __reconstruct_3d_pose(self, triangulate_param):
        task = []
        for person_id in triangulate_param:
            task.append(self.__simple_recon_person(person_id, triangulate_param[person_id]['keypoint'], triangulate_param[person_id]['P']))
        out = await asyncio.gather(*task)
        return out

    async def __simple_recon_person(self, person_id, keypoints_use, Puse):
        (person_id, out) = self.__batch_triangulate(person_id, keypoints_use, Puse)
        # compute reprojection error
        kpts_repro = self.__projectN3(out, Puse)
        square_diff = (keypoints_use[:, :, :2] - kpts_repro[:, :, :2])**2
        conf = np.repeat(out[None, :, -1:], len(Puse), 0)
        kpts_repro = np.concatenate((kpts_repro, conf), axis=2)
        return person_id, out, kpts_repro

    def __batch_triangulate(self, person_id, keypoints_, Pall):
        v = (keypoints_[:, :, -1]>0).sum(axis=0)
        valid_joint = np.where(v > 1)[0]
        keypoints = keypoints_[:, valid_joint]
        conf3d = keypoints[:, :, -1].sum(axis=0)/v[valid_joint]
        # P2: last row of matrix：(1, nViews, 1, 4)
        P0 = Pall[None, :, 0, :]
        P1 = Pall[None, :, 1, :]
        P2 = Pall[None, :, 2, :]

        # uP2: The x coordinate is multiplied by P2: (nJoints, nViews, 1, 4)
        uP2 = keypoints[:, :, 0].T[:, :, None] * P2
        vP2 = keypoints[:, :, 1].T[:, :, None] * P2
        conf = keypoints[:, :, 2].T[:, :, None]
        Au = conf * (P0 - uP2)
        Av = conf * (vP2 - P1)
        A = np.hstack([Au, Av])

        u, s, v = np.linalg.svd(A)
        X = v[:, -1, :]
        X = X / X[:, 3:]
        # out: (nJoints, 4)
        result = np.zeros((keypoints_.shape[1], 4))
        result[valid_joint, :3] = X[:, :3]
        result[valid_joint, 3] = conf3d
        return (person_id, result)

    def __projectN3(self, kpts3d, Pall):
        # kpts3d: (N, 3)
        nViews = len(Pall)
        kp3d = np.hstack((kpts3d[:, :3], np.ones((kpts3d.shape[0], 1))))
        kp2ds = []
        for nv in range(nViews):
            kp2d = Pall[nv] @ kp3d.T
            kp2d[:2, :] /= kp2d[2:, :]
            kp2ds.append(kp2d.T[None, :, :])
        kp2ds = np.vstack(kp2ds)
        kp2ds[..., -1] = kp2ds[..., -1] * (kpts3d[None, :, -1] > 0.)
        return kp2ds

    def __get_facehand_status(self, lk_facehand, mq_facehand, face_status, hand_status):
        lk_facehand.acquire()
        qsize = mq_facehand.qsize()

        for i in range(qsize):
            json_data = mq_facehand.get()
            data = json.loads(json_data)
            for person in data["annots"]:
                face_status_idx = person['faceStatus']
                hand_status_idx = person['handStatus']
                face_status = face_format.get_status_from_idx(face_status_idx)
                hand_status = hand_format.get_status_from_idx(hand_status_idx)

        lk_facehand.release()
        return face_status, hand_status
