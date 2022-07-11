import numpy as np
import datetime
import time
import json
import pause
import asyncio

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
        self.__transformation = fs.read_transformation('./etc/transformation.json')
        self.viewer = v2d.Viewer2d()
        self.__frame_number = 0

    def initialize(self, config):
        self.__config = config
        self.__person_num = 30
        self.__cam_num = self.__config["cam_num"]
        self.__min_cam = self.__config["min_cam"]
        self.__target_fps = self.__config["fps"]
        self.__system_interval = 1000/self.__target_fps # milli-seconds
        self.__buffer_size = self.__config["buffer_size"]
        self.__max_frame = self.__config["max_frame"]
        self.__min_confidence = self.__config["min_confidence"]
        self.__skeleton_table = self.__get_initial_skeleton_table(self.__calibration)
        self.__person_table = self.__get_initial_person_table()
        self.__frame_buffer_2d = np.ones((self.__cam_num+1, self.__person_num, self.__buffer_size, 25, 3))
        self.__frame_buffer_pos = np.ones((self.__cam_num+1, self.__person_num, self.__buffer_size, 6, 4))

    def run(self, func_recv_skeleton, func_recv_handface, func_send_skeleton_gui, func_send_skeleton_unity):
        self.__skeleton_mq, self.__skeleton_lk = func_recv_skeleton(self.__config["server_ip"], self.__config["skeleton_port"])
        if self.__args.face:
            hand_face_mq, hand_face_lk = func_recv_handface(self.__config["server_ip"], self.__config["facehand_port"])

        self.__send_skeleton_gui = func_send_skeleton_gui
        self.__send_skeleton_unity = func_send_skeleton_unity

        face_status = face_format.FACE_STATUS.CLOSED
        hand_status = hand_format.HAND_STATUS.OPEN

        frame_buffer = np.ones((self.__person_num, self.__buffer_size, 25, 4))
        while(True):
            t_sleep = datetime.datetime.now()
            self.__update_skeleton_table()
            self.__update_person_table()

            data = []
            triangulate_param = {}
            valid_dlt_element = self.__get_valid_dlt_element()
            for person_id in range(0, self.__person_num):
                if valid_dlt_element[person_id]['count'] >= self.__min_cam:
                    valid_keypoint = np.stack(valid_dlt_element[person_id]['valid_keypoint'], axis=0)
                    valid_p = np.stack(valid_dlt_element[person_id]['valid_P'], axis=0)
                    triangulate_param[person_id] = {}
                    triangulate_param[person_id]['keypoint'] = valid_keypoint
                    triangulate_param[person_id]['P'] = valid_p

            reconstruction_list = asyncio.run(self.__reconstruct_3d_pose(triangulate_param))

            for reconstruction in reconstruction_list:
                person_id = reconstruction[0]
                keypoint_3d = reconstruction[1]
                frame_buffer[person_id], ret = post.smooth_3d_pose(frame_buffer[person_id], keypoint_3d)
                data.append({'id' : person_id, 'keypoints3d' : ret})

            if self.__args.face is True:
                # Read face hand status from clients
                face_status, hand_status = self.__get_facehand_status(hand_face_lk, hand_face_mq, face_status, hand_status)
                print("[FACE STATUS] ", face_status)
                print("[HAND STATUS] ", hand_status)

            if len(data) > 0:
                if self.__args.gui is True:
                    self.__send_skeleton_gui(data)
                if self.__args.unity is True:
                    self.__send_skeleton_unity(data)

            self.__reset_skeleton_table()
            self.__reset_person_table()

            self.__frame_number += 1

            pause.until(t_sleep.timestamp() + self.__system_interval/1000)

    def __get_initial_skeleton_table(self, calibration):
        skeleton_table = {}
        for cam_id in range(1, self.__cam_num+1):
            skeleton_table[cam_id] = {}
            skeleton_table[cam_id]['P'] = calibration[str(cam_id)]['P'].tolist()
            for person_id in range(0, self.__person_num):
                skeleton_table[cam_id][person_id] = {}
                skeleton_table[cam_id][person_id]['is_valid'] = False
                skeleton_table[cam_id][person_id]['keypoint'] = np.zeros((25, 3)).tolist()
                skeleton_table[cam_id][person_id]['position'] = np.zeros((6, 4)).tolist()
        return skeleton_table

    def __reset_skeleton_table(self):
        for cam_id in range(1, self.__cam_num+1):
            for person_id in range(0, self.__person_num):
                self.__skeleton_table[cam_id][person_id]['is_valid'] = False

    def __get_initial_person_table(self):
        person_table = {}
        for person_id in range(0, self.__person_num):
            person_table[person_id] = {}
            person_table[person_id]['is_valid'] = False
            person_table[person_id]['count'] = 0
            person_table[person_id]['cam_person'] = []
            person_table[person_id]['position'] = []
            person_table[person_id]['prev_position'] = (0, 0)
        return person_table

    def __reset_person_table(self):
        for person_id in range(0, self.__person_num):
            if self.__person_table[person_id]['is_valid'] is True:
                cnt = 0
                avg_x = 0.0
                avg_y = 0.0
                for j in range(self.__person_table[person_id]['count']):
                    avg_x += self.__person_table[person_id]['position'][j][0]
                    avg_y += self.__person_table[person_id]['position'][j][1]
                    cnt += 1
                avg_x /= cnt
                avg_y /= cnt

                self.__person_table[person_id]['prev_position']=(avg_x, avg_y)
            self.__person_table[person_id]['is_valid'] = False
            self.__person_table[person_id]['count'] = 0
            self.__person_table[person_id]['cam_person'] = []
            self.__person_table[person_id]['position'] = []

    def __update_person_table(self):
        max_person_num = 0
        position_idx = np.empty((0, 2)) # cam_id, person_id
        position_arr = np.empty((0, 2)) # X, Y

        for cam_id in range(1, self.__cam_num+1):
            transform = self.__transformation['T'+str(cam_id)+'1']
            person_num = 0
            for person_id in range(0, self.__person_num):
                if self.__skeleton_table[cam_id][person_id]['is_valid'] is True:
                    person_num += 1
                    average_position = self.__get_average_position(cam_id, person_id, transform)
                    position_arr = np.append(position_arr, np.array([[average_position[0], average_position[1]]]), axis=0)
                    position_idx = np.append(position_idx, np.array([[cam_id, person_id]]), axis=0)

            if max_person_num < person_num:
                max_person_num = person_num

        if max_person_num > 0:
            cluster_arr = self.__get_cluster_arr(position_arr, max_person_num)
            for i in range(len(cluster_arr)):
                cluster_id = cluster_arr[i]
                self.__person_table[cluster_id]['is_valid'] = True
                self.__person_table[cluster_id]['count'] += 1
                self.__person_table[cluster_id]['cam_person'].append(position_idx[i]) # cam_id, person_id
                self.__person_table[cluster_id]['position'].append(position_arr[cluster_id]) # X, Y

    def __get_average_position(self, cam_id, person_id, transform):
        position = self.__skeleton_table[cam_id][person_id]['position']
        c = []
        position = np.array(position)
        transform = np.array(transform)
        for kp in position:
            k = (transform[:-1, :-1]@kp[:3] + transform[:-1, -1]).tolist()
            k.extend([kp[3]])
            c.append(k)
        c = np.array(c)
        avg_x = np.average(c[:, 0])
        avg_y = np.average(c[:, 1])
        return (avg_x, avg_y)

    def __get_cluster_arr(self, position_arr, max_person_num):
        print("[INFO] Clustering... {} people".format(max_person_num))
        print(position_arr)
        if len(position_arr) <= max_person_num:
            return []

        from sklearn.cluster import AgglomerativeClustering

        cluster = AgglomerativeClustering(n_clusters=max_person_num, affinity='euclidean', linkage='ward')
        ret = cluster.fit_predict(position_arr)
        return ret

    def __get_valid_dlt_element(self):
        # print(self.__person_table)
        valid_dlt_element = {}
        for person_id in range(0, self.__person_num):
            valid_dlt_element[person_id] = {}
            valid_dlt_element[person_id]['count'] = 0
            valid_dlt_element[person_id]['valid_keypoint'] = []
            valid_dlt_element[person_id]['valid_P'] = []

        for person_id in range(0, self.__person_num):
            if self.__person_table[person_id]['is_valid'] is True:
                valid_dlt_element[person_id]['count'] = self.__person_table[person_id]['count']
                for i in range(self.__person_table[person_id]['count']):
                    cid = self.__person_table[person_id]['cam_person'][i][0]
                    pid = self.__person_table[person_id]['cam_person'][i][1]
                    valid_dlt_element[person_id]['valid_keypoint'].append(self.__skeleton_table[cid][pid]['keypoint'])
                    valid_dlt_element[person_id]['valid_P'].append(self.__skeleton_table[cid]['P'])

        return valid_dlt_element

    def __update_skeleton_table(self):
        self.__skeleton_lk.acquire()
        qsize = self.__skeleton_mq.qsize()

        for i in range(qsize):
            data = self.__skeleton_mq.get()
            data = json.loads(data)
            if self.__args.visual:
                self.viewer.render_2d(data)

            cam_id = data['id']
            for person_data in data['annots']:
                person_id = person_data['personID']
                if cam_id < 0 or cam_id > self.__cam_num or person_id < 0 or person_id >= self.__person_num:
                    print('Invalid data : {}, {}'.format(cam_id, person_id))
                    continue
                keypoints_34 = np.array(person_data['keypoints'])
                keypoints_25 = utils.convert_25_from_34(keypoints_34)
                self.__frame_buffer_2d[cam_id][person_id], avg_keypoints_25 = pre.smooth_2d_pose(self.__frame_buffer_2d[cam_id][person_id], keypoints_25)
                self.__skeleton_table[cam_id][person_id]['is_valid'] = True
                self.__skeleton_table[cam_id][person_id]['keypoint'] = avg_keypoints_25.tolist()
                self.__frame_buffer_pos[cam_id][person_id], avg_position = pre.smooth_position(self.__frame_buffer_pos[cam_id][person_id], person_data['position'])
                self.__skeleton_table[cam_id][person_id]['position'] = avg_position

        self.__skeleton_lk.release()

        if self.__args.log is True:
            file_path = "./log/" + str(self.__frame_number).zfill(6) + ".json"
            with open(file_path, "w") as outfile:
                json.dump(self.__skeleton_table, outfile)

    async def __reconstruct_3d_pose(self, triangulate_param):
        task = []
        for person_id in triangulate_param:
            task.append(self.__batch_triangulate(person_id, triangulate_param[person_id]['keypoint'], triangulate_param[person_id]['P']))
        out = await asyncio.gather(*task)
        return out

    async def __batch_triangulate(self, person_id, keypoints_, Pall):
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