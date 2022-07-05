import numpy as np
import datetime
import time
import json
import pause
import threading
from queue import Queue

from format import face_format, hand_format

from reconstructor import postprocessor as post
from reconstructor import preprocessor as pre

from config import file_storage as fs
from visualizer import utils
from visualizer import viewer_2d as v2d

class Reconstructor:
    def __init__(self, args):
        self.__args = args
        self.__calibration = fs.read_camera('./etc/intri.yml', './etc/extri.yml')
        self.viewer = v2d.Viewer2d()

    def initialize(self, config):
        self.__config = config
        self.__cam_num = self.__config["cam_num"]
        self.__min_cam = self.__config["min_cam"]
        self.__target_fps = self.__config["fps"]
        self.__system_interval = 1000/self.__target_fps # milli-seconds
        self.__buffer_size = self.__config["buffer_size"]
        self.__max_frame = self.__config["max_frame"]
        self.__min_confidence = self.__config["min_confidence"]
        self.__matching_table = self.__get_initial_matching_table(self.__calibration)
        self.__frame_buffer_2d = np.ones((self.__cam_num+1, self.__buffer_size, 25, 3))

    def run(self, func_recv_skeleton, func_recv_handface, func_send_skeleton_gui, func_send_skeleton_unity):
        self.__skeleton_mq, self.__skeleton_lk = func_recv_skeleton(self.__config["server_ip"], self.__config["skeleton_port"])
        if self.__args.face:
            hand_face_mq, hand_face_lk = func_recv_handface(self.__config["server_ip"], self.__config["facehand_port"])

        self.__send_skeleton_gui = func_send_skeleton_gui
        self.__send_skeleton_unity = func_send_skeleton_unity

        face_status = face_format.FACE_STATUS.CLOSED
        hand_status = hand_format.HAND_STATUS.OPEN

        t = (-1, -1, 0)
        frame_buffer = np.ones((self.__buffer_size, 25, 4))
        cnt = 0
        while(True):
            t_sleep = datetime.datetime.now()
            #     t = self.__sync_matching_table(t[0], t[1], t[2])
            #     self.__use_previous_frame(t[0], t[1])
            self.__use_latest_matching_table()

            if self.__args.face is True:
                # Read face hand status from clients
                face_status, hand_status = self.__get_facehand_status(hand_face_lk, hand_face_mq, face_status, hand_status)
                print("[FACE STATUS] ", face_status)
                print("[HAND STATUS] ", hand_status)

            valid_dlt_element = self.__get_valid_dlt_element()
            if valid_dlt_element['count'] >= self.__min_cam:
                valid_keypoint = np.stack(valid_dlt_element['valid_keypoint'], axis=0)
                valid_p = np.stack(valid_dlt_element['valid_P'], axis=0)
                out = self.__batch_triangulate(valid_keypoint, valid_p)
                frame_buffer, ret = post.smooth_3d_pose(frame_buffer, out)

                if self.__args.gui is True:
                    self.__send_skeleton_gui(ret)
                if self.__args.unity is True:
                    self.__send_skeleton_unity(ret)

                self.__reset_matching_table()
            else:
                print('Skip to restore 3D pose, number of valid data is ', valid_dlt_element['count'])
            self.__reset_matching_table()
            t = self.__reset_time(t)

            pause.until(t_sleep.timestamp() + self.__system_interval/1000)

    def __get_initial_matching_table(self, calibration):
        matching_table = {}
        for cam_id in range(1, self.__cam_num+1):
            matching_table[cam_id] = {}
            matching_table[cam_id]['is_valid'] = False
            matching_table[cam_id]['timestamp'] = 0
            matching_table[cam_id]['keypoint'] = np.zeros((25, 3))
            matching_table[cam_id]['P'] = calibration[str(cam_id)]['P']
        return matching_table

    def __reset_matching_table(self):
        for cam_id in range(1, self.__cam_num+1):
            self.__matching_table[cam_id]['is_valid'] = False

    def __reset_time(self, t):
        t_start = t[0]
        t_end = t[1]
        t_diff = t[2]
        if t_start != -1:
            t_start = t_end
            t_end = t_start + self.__system_interval/1000
        return (t_start, t_end, t_diff)

    def __get_valid_dlt_element(self):
        valid_dlt_element = {}
        valid_dlt_element['count'] = 0
        valid_dlt_element['valid_timestamp'] = []
        valid_dlt_element['valid_keypoint'] = []
        valid_dlt_element['valid_P'] = []
        for cam_id in range(1, self.__cam_num+1):
            if self.__matching_table[cam_id]['is_valid'] is True:
                valid_dlt_element['count'] += 1
                valid_dlt_element['valid_timestamp'].append(self.__matching_table[cam_id]['timestamp'])
                valid_dlt_element['valid_keypoint'].append(self.__matching_table[cam_id]['keypoint'])
                valid_dlt_element['valid_P'].append(self.__matching_table[cam_id]['P'])
        return valid_dlt_element

    def __sync_matching_table(self, t_start, t_end, t_diff):
        self.__skeleton_lk.acquire()
        qsize = self.__skeleton_mq.qsize()
        if qsize > self.__min_cam:
            for i in range(qsize):
                data = self.__skeleton_mq.get()
                data = json.loads(data)
                t = data[0]
                if t_start == -1:
                    t_start = data[0]
                    t_end = data[0] + self.__system_interval/1000
                    t_diff = datetime.datetime.now().timestamp() - t_start
                elif t < t_start:
                    continue
                elif t > t_end:
                    self.__skeleton_mq.put(data)
                else:
                    if self.__args.visual:
                        self.viewer.render_2d(data)
                    cam_id = data['id']
                    timestamp = data['timestamp']
                    person_id = len(data['annots'])-1 # TODO: check if it is correct
                    keypoints_34 = np.array(data['annots'][person_id]['keypoints'])
                    keypoints_25 = utils.convert_25_from_34(keypoints_34)
                    self.self.__frame_buffer_2d[cam_id], avg_keypoints_25 = pre.smooth_2d_pose(self.self.__frame_buffer_2d[cam_id], keypoints_25)
                    self.__matching_table[cam_id]['is_valid'] = True
                    self.__matching_table[cam_id]['timestamp'] = timestamp
                    self.__matching_table[cam_id]['keypoint'] = avg_keypoints_25.tolist()

        self.__skeleton_lk.release()
        return (t_start, t_end, t_diff)

    def __use_latest_matching_table(self):
        self.__skeleton_lk.acquire()
        qsize = self.__skeleton_mq.qsize()

        for i in range(qsize):
            data = self.__skeleton_mq.get()
            data = json.loads(data)
            if self.__args.visual:
                self.viewer.render_2d(data)

            print(data)

            cam_id = data['id']
            timestamp = data['timestamp']
            person_id = len(data['annots'])-1 # TODO: check if it is correct
            keypoints_34 = np.array(data['annots'][person_id]['keypoints'])
            keypoints_25 = utils.convert_25_from_34(keypoints_34)
            self.__frame_buffer_2d[cam_id], avg_keypoints_25 = pre.smooth_2d_pose(self.__frame_buffer_2d[cam_id], keypoints_25)
            self.__matching_table[cam_id]['is_valid'] = True
            self.__matching_table[cam_id]['timestamp'] = timestamp
            self.__matching_table[cam_id]['keypoint'] = avg_keypoints_25.tolist()
        self.__skeleton_lk.release()

    def __use_previous_frame(self, t_start, t_end):
        for cam_id in range(1, self.__cam_num+1):
            if self.__matching_table[cam_id]['is_valid'] is False:
                if t_start - self.__matching_table[cam_id]['timestamp'] < self.__system_interval*4:
                    self.__matching_table[cam_id]['is_valid'] = True

    def __batch_triangulate(self, keypoints_, Pall):
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
        return result

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
                #print("[{}], {}, {}".format(person['personID'], face_status, hand_status))

        lk_facehand.release()
        return face_status, hand_status