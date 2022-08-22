import numpy as np
import math
import logging
import cv2
import copy

from reconstructor.utils import postprocessor as post
from visualizer import utils
from visualizer import viewer_2d as v2d

class ClusterManager:
    def __init__(self, args, cam_num, person_num, transformation):
        self.__args = args
        self.__cam_num = cam_num
        self.__person_num = person_num
        self.__transformation = transformation
        self.__cluster_table = self.__get_initial_cluster_table()
        self.__is_too_closed = False
        self.viewer = v2d.Viewer2d(self.__args)

    def initialize(self):
        self.viewer.initialize(self.__cam_num)

    def __get_initial_cluster_table(self):
        cluster_table = {}
        for cluster_id in range(0, self.__person_num):
            cluster_table[cluster_id] = {}
            cluster_table[cluster_id]['is_valid'] = False
            cluster_table[cluster_id]['count'] = 0
            cluster_table[cluster_id]['position'] = []
            cluster_table[cluster_id]['cpid'] = []
            cluster_table[cluster_id]['prev_position'] = (0, 0)
        return cluster_table

    def is_cluster_valid(self, cluster_id):
        return self.__cluster_table[cluster_id]['is_valid']

    def get_count(self, cluster_id):
        return self.__cluster_table[cluster_id]['count']

    def get_cpid(self, cluster_id):
        return self.__cluster_table[cluster_id]['cpid']

    def get_position(self, cluster_id):
        return self.__cluster_table[cluster_id]['position']

    def get_prev_position(self, cluster_id):
        return self.__cluster_table[cluster_id]['prev_position']

    def set_skip_to_make_cluster(self, is_too_closed):
        self.__is_too_closed = is_too_closed

    def update_person_table(self, skeleton_manager, cluster_num, frame_number):
        if self.__is_too_closed:
            return

        max_person_num = 0
        position_idx = np.empty((0, 2)) # cam_id, person_id
        position_arr = np.empty((0, 2)) # X, Y

        for cam_id in range(1, self.__cam_num+1):
            transform = self.__transformation['T'+str(cam_id)+'1']
            person_num = 0
            for person_id in range(0, self.__person_num):
                is_skeleton_valid = skeleton_manager.is_skeleton_valid(cam_id, person_id)
                skeleton = skeleton_manager.get_skeleton(cam_id, person_id)
                if is_skeleton_valid is True:
                    average_position = self.__get_average_position(skeleton_manager, cam_id, person_id, transform)
                    dist_from_cam1 = np.linalg.norm(np.array([average_position[0], average_position[1]]) - self.__transformation['C1'][:2])
                    logging.debug("[DISTANCE] cam {}, person {} : {}".format(cam_id, person_id, dist_from_cam1))
                    if dist_from_cam1 < 5:
                        position_arr = np.append(position_arr, np.array([[average_position[0], average_position[1]]]), axis=0)
                        position_idx = np.append(position_idx, np.array([[cam_id, person_id]]), axis=0)
                        person_num += 1

            if max_person_num < person_num:
                max_person_num = person_num
            if max_person_num >= cluster_num:
                max_person_num = cluster_num

        if max_person_num > 0:
            cluster_arr = self.__get_cluster_arr(position_arr, position_idx, max_person_num, skeleton_manager, frame_number)
            for i in range(len(cluster_arr)):
                cluster_id = cluster_arr[i]
                if cluster_id >= 0:
                    self.__cluster_table[cluster_id]['is_valid'] = True
                    self.__cluster_table[cluster_id]['count'] += 1
                    self.__cluster_table[cluster_id]['cpid'].append(post.get_cpid(position_idx[i][0], position_idx[i][1])) # cam_id, person_id
                    self.__cluster_table[cluster_id]['position'].append(position_arr[cluster_id]) # X, Y

    def __get_average_position(self, skeleton_manager, cam_id, person_id, transform):
        position = skeleton_manager.get_position(cam_id, person_id)
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

    def __get_cluster_arr(self, position_arr, position_idx, max_person_num, skeleton_manager, frame_number):
        from sklearn.cluster import AgglomerativeClustering

        logging.info("[INFO] Clustering... {} people".format(max_person_num))
        if len(position_arr) <= max_person_num:
            return []

        cluster = AgglomerativeClustering(n_clusters=max_person_num, affinity='euclidean', linkage='ward')
        ret = cluster.fit_predict(position_arr)

        vis_arr = {}
        data = {}
        data['annots'] = []
        for i in range(len(ret)):
            logging.debug("... ({}, {}) : {} --> {}".format(int(position_idx[i][0]), int(position_idx[i][1]), position_arr[i], ret[i]))

        ret = self.__remove_duplicated_person(position_idx, position_arr, max_person_num, ret)

        # matched_person_position = np.zeros((max_person_num, 2))
        # for i in range(max_person_num):
        #     matched_idx = np.where(ret == i)
        #     matched_person_position[i] = np.average(position_arr[matched_idx], axis=0)
        #     print(self.__find_near_elements(position_arr[matched_idx], matched_person_position[i], 3))

        for i in range(len(ret)):
            if self.__args.visual:
                cam_id = int(position_idx[i][0])
                person_id = int(position_idx[i][1])
                fixed_person_id = int(ret[i])

                if cam_id not in vis_arr:
                    vis_arr[cam_id] = {}
                    vis_arr[cam_id]['annots'] = []

                vis_arr[cam_id]['annots'].append({
                    'personID' : fixed_person_id,
                    'bbox' : [1,1,2,2],
                    'keypoints' : skeleton_manager.get_skeleton(cam_id, person_id)
                })

        if self.__args.visual:
            for cam_id in vis_arr.keys():
                data = {}
                data['id'] = cam_id
                data['annots'] = vis_arr[cam_id]['annots']
                self.viewer.render_2d(data)

        if self.__args.visual:
            if self.__args.log or frame_number % 40 == 0:
                room_size = 10 # 10m x 10m
                display = np.ones((600, 600, 3), np.uint8) * 255
                utils.draw_grid(display)
                for i in range(len(ret)):
                    x = position_arr[i][0] + room_size/2
                    y = position_arr[i][1] + room_size/2
                    x *= display.shape[0]/room_size*1.5
                    y *= display.shape[1]/room_size*1.5
                    color = utils.generate_color_id_u(ret[i])
                    cv2.circle(display, (int(x), int(y)), 6, color, -1)
                    cv2.putText(display, "({}, {})".format(int(position_idx[i][0]), int(position_idx[i][1])), (int(x), int(y)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2   )

                cv2.imshow("Position", display)
                cv2.waitKey(1)

        return ret

    def __remove_duplicated_person(self, position_idx, position_arr, max_person_num, cluster_ret):
        ret = np.array(copy.deepcopy(cluster_ret))

        matched_person_position = np.zeros((max_person_num, 2))
        for i in range(max_person_num):
            matched_idx = np.where(ret == i)
            matched_person_position[i] = np.average(position_arr[matched_idx], axis=0)
            # print("average position of {} : {}".format(i, matched_person_position[i]))

        person_group = {}
        for i in range(self.__cam_num+1):
            person_group[i] = {}
            for j in range(self.__person_num):
                person_group[i][j] = {}
                person_group[i][j]['count'] = 0
                person_group[i][j]['id'] = []

        for i in range(len(cluster_ret)):
            person_group[int(position_idx[i][0])][cluster_ret[i]]['count'] += 1
            person_group[int(position_idx[i][0])][cluster_ret[i]]['id'].append(i)

        # for cam_id in range(self.__cam_num+1):
        for i in range(len(cluster_ret)):
            cnt = person_group[int(position_idx[i][0])][cluster_ret[i]]['count']
            if cnt > 1 and cnt < 10:
                cache = np.zeros((cnt, max_person_num))
                id = 0
                for duplicated_id in person_group[int(position_idx[i][0])][cluster_ret[i]]['id']:
                    for matched_idx in range(len(matched_person_position)):
                        cache[id][matched_idx] = np.linalg.norm(position_arr[duplicated_id] - matched_person_position[matched_idx])
                    id += 1

                is_valid_cam = np.ones(max_person_num)
                min_dist, min_arr = self.__get_minimum_dist(cache, cnt, is_valid_cam, max_person_num)
                print("[{}] : {}".format(int(position_idx[i][0]), min_arr))
                id = 0
                # print("person group : {}".format(person_group[int(position_idx[i][0])][cluster_ret[i]]['id']))
                # print("min_arr : {}".format(min_arr))
                for duplicated_id in person_group[int(position_idx[i][0])][cluster_ret[i]]['id']:
                    if len(person_group[int(position_idx[i][0])][cluster_ret[i]]['id']) == len(min_arr):
                        ret[duplicated_id] = min_arr[id]
                        id += 1
                    else:
                        print("size mismatched")
            elif cnt > 10:
                ret[i] = -1
            else:
                pass

        person_group = {}
        for i in range(self.__cam_num+1):
            person_group[i] = {}
            for j in range(self.__person_num):
                person_group[i][j] = {}
                person_group[i][j]['count'] = 0
                person_group[i][j]['id'] = []

        for i in range(len(ret)):
            person_group[int(position_idx[i][0])][ret[i]]['count'] += 1
            person_group[int(position_idx[i][0])][ret[i]]['id'].append(i)

        for i in range(len(ret)):
            if person_group[int(position_idx[i][0])][ret[i]]['count'] > 1:
                ret[i] = -1

        return ret

    # def __find_near_elements(self, array, value, n):
    #     lst = copy.deepcopy(array)
    #     ret = []
    #     if len(lst) < n:
    #         return lst

    #     for i in range(n):
    #         lst = np.asarray(lst)
    #         idx = (np.abs(lst - value)).argmin()
    #         ret.append(lst[idx])
    #         lst = np.delete(lst, idx)
    #     return ret

    def __get_minimum_dist(self, cache, cnt, is_valid_cam, max_person_num):
        cnt -= 1
        if cnt < 0:
            return (0, [])
        min_dist = np.inf
        min_idx = -1
        min_arr = np.array([], dtype='int32')
        for i in range(max_person_num):
            if is_valid_cam[i]:
                is_valid_cam[i] = False
                ret = self.__get_minimum_dist(cache, cnt, is_valid_cam, max_person_num)
                dist = cache[cnt][i] + ret[0]
                arr = ret[1]
                is_valid_cam[i] = True
                if dist < min_dist:
                    min_dist = dist
                    min_idx = i
                    min_arr = arr
        return (min_dist, np.append(min_arr, min_idx))

    def reset_cluster_table(self):
        if self.__is_too_closed:
            return

        for cluster_id in range(0, self.__person_num):
            if self.__cluster_table[cluster_id]['is_valid'] is True:
                cnt = 0
                avg_x = 0.0
                avg_y = 0.0
                for j in range(self.__cluster_table[cluster_id]['count']):
                    avg_x += self.__cluster_table[cluster_id]['position'][j][0]
                    avg_y += self.__cluster_table[cluster_id]['position'][j][1]
                    cnt += 1
                avg_x /= cnt
                avg_y /= cnt
                self.__cluster_table[cluster_id]['prev_position']=(avg_x, avg_y)
            self.__cluster_table[cluster_id]['is_valid'] = False
            self.__cluster_table[cluster_id]['count'] = 0
            self.__cluster_table[cluster_id]['cpid'] = []
            self.__cluster_table[cluster_id]['position'] = []