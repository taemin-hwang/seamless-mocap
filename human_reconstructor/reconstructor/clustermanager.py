import numpy as np
import math
import logging
import cv2
import copy

from sklearn.cluster import AgglomerativeClustering
from reconstructor.utils import postprocessor as post
from visualizer import utils

class ClusterManager:
    def __init__(self, args, cam_num, person_num, transformation, viewer):
        self.__args = args
        self.__cam_num = cam_num
        self.__person_num = person_num
        self.__transformation = transformation
        self.__cluster_table = self.__get_initial_cluster_table()
        self.__is_too_closed = False
        self.__viewer = viewer
        self.__valid_cluster = None

    def initialize(self):
        self.__viewer.initialize(self.__cam_num)

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

    def show_cluster_result(self, skeleton_manager, frame_number):
        if self.__args.visual is False:
            return

        # Render 2D Keypoints
        self.__viewer.render_cluster_table(self.__person_num, self.__cluster_table, skeleton_manager)

        # Render Position
        # self.__viewer.render_position(self.__person_num, self.__cluster_table)
        self.__viewer.render_cloth_color(self.__person_num, self.__cluster_table, skeleton_manager)


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

    def save_valid_cluster(self, is_valid_cluster, frame_number):
        if is_valid_cluster is True:
            logging.info(" ClusterManager: Save valid cluster table : {}".format(frame_number))
            self.__valid_cluster = copy.deepcopy(self.__cluster_table)

    def update_person_table_with_cloth(self, skeleton_manager, cluster_num):
        if self.__is_too_closed is True and self.__valid_cluster is not None:
            logging.info(" ClusterManager: Skip to update person table and reuse valid cluster table")
            self.reuse_valid_cluster(skeleton_manager)
            return

        self.__assign_cluster_with_cloth(skeleton_manager, cluster_num)
        # for matched_id in range(cluster_num):
        #     self.__check_consistency_of_cluster(skeleton_manager, matched_id)

    def __assign_cluster_with_cloth(self, skeleton_manager, cluster_num):
        remove_cpid = []
        #print(cloth_arr.shape)

        while True:
            max_person_num = 0
            cloth_idx = np.empty((0, 2))
            cloth_arr = np.empty((0, 6))

            for cid in range(1, self.__cam_num+1):
                person_num = 0
                for pid in range(0, self.__person_num):
                    if skeleton_manager.is_skeleton_valid(cid, pid) == True:
                        if (cid, pid) not in remove_cpid:
                            cloth = skeleton_manager.get_cloth(cid, pid)
                            cloth_arr = np.vstack((cloth_arr, np.hstack([cloth[0], cloth[1]]))) #upper, lower
                            cloth_idx = np.vstack((cloth_idx, np.array([cid, pid])))
                            person_num += 1

                if max_person_num < person_num:
                    max_person_num = person_num
                if max_person_num >= cluster_num:
                    max_person_num = cluster_num

            if cloth_arr.shape[0] <= max_person_num or max_person_num < 1:
                break

            logging.info(" ClusterManager: Try to make {} clusters with {} clothes".format(cluster_num, cloth_arr.shape[0]))
            assign = self.__apply_agglomerative_clustering(cloth_idx, cloth_arr, max_person_num)

            if assign is None:
                break

            val, num = np.unique(assign, return_counts=True)
            std = np.std(num)

            if std > 1:
                min_idx = np.argmin(num)
                remove_val = val[min_idx]
                remove_idx = np.where((assign == remove_val))
                for idx in remove_idx:
                    remove_cid = cloth_idx[idx[0]][0]
                    remove_pid = cloth_idx[idx[0]][1]
                    remove_cpid.append((remove_cid, remove_pid))
            else:
                for i, matched_id in enumerate(assign):
                    logging.info("[CLOTH] cam {}, person {} : {}".format(int(cloth_idx[i][0]), int(cloth_idx[i][1]), int(matched_id)))
                    self.__cluster_table[matched_id]['is_valid'] = True
                    self.__cluster_table[matched_id]['count'] += 1
                    self.__cluster_table[matched_id]['cpid'].append(post.get_cpid(cloth_idx[i][0], cloth_idx[i][1])) # cam_id, person_id
                break

    def __apply_agglomerative_clustering(self, cloth_idx, cloth_arr, person_num):
        if cloth_arr.shape[0] <= person_num:
            logging.warning(" ClusterManager: Cannot make {} clusters with {} features".format(person_num, cloth_arr.shape[0]))
            return None
        agg = AgglomerativeClustering(n_clusters=person_num)

        if self.__args.cloth == 'upper':
            assign = agg.fit_predict(cloth_arr[:, :3])
        else:
            assign = agg.fit_predict(cloth_arr)

        return assign

    def __check_consistency_of_cluster(self, skeleton_manager, matched_id):
        if self.__cluster_table[matched_id]['is_valid'] is False:
            return

        max_cam = 0
        max_person = 0
        cpids = []
        for i in range(self.__cluster_table[matched_id]['count']):
            cpid = self.__cluster_table[matched_id]['cpid'][i]
            cid = post.get_cam_id(cpid)
            pid = post.get_person_id(cpid)

            cpids.append(cpid)
            if cid >= max_cam:
                max_cam = cid
            if pid >= max_person:
                max_person = pid

        color_map = {}
        for cpid in cpids:
            cid = post.get_cam_id(cpid)
            pid = post.get_person_id(cpid)
            color = skeleton_manager.get_cloth(cid, pid)
            color_map[cpid] = color

        cpids = np.array(cpids)
        np.sort(cpids)
        print("[PREV] ", cpids)

        consistent_cluster, _, _ = self.__get_minimum_cluster(-1, -1, cpids, color_map, 0)
        consistent_cluster = np.array(consistent_cluster)

        print("CONSISTENT CLUSTER")
        for i in range(consistent_cluster.shape[0]):
            cpid = consistent_cluster[i]
            cid = post.get_cam_id(cpid)
            pid = post.get_person_id(cpid)
            print("[{}] ({}, {})".format(matched_id, cid, pid))

        for cpid in self.__cluster_table[matched_id]['cpid']:
            if cpid not in consistent_cluster:
                self.__cluster_table[matched_id]['cpid'].remove(cpid)
                self.__cluster_table[matched_id]['count'] -= 1

    def __get_minimum_cluster(self, start_cpid, prev_cpid, cpids, color_map, depth):
        ret_cpid = []
        tmp_cpid = []
        max_depth = 0
        tmp_depth = 0
        min_dist = np.inf
        tmp_dist = np.inf

        #print("[{}] CALL MINIMUM CLUSTER ({}) and ({})".format(depth, start_cpid, prev_cpid))

        if start_cpid == -1 and prev_cpid == -1:
            for cpid in cpids:
                tmp_cpid, tmp_depth, tmp_dist = self.__get_minimum_cluster(cpid, cpid, cpids, color_map, depth+1)
                if max_depth < len(tmp_cpid):
                    max_depth = len(tmp_cpid)
                    ret_cpid = tmp_cpid
                elif max_depth == len(tmp_cpid):
                    if min_dist > tmp_dist:
                        min_dist = tmp_dist
                        ret_cpid = tmp_cpid
        else:
            start_cid = post.get_cam_id(start_cpid)
            start_pid = post.get_person_id(start_cpid)

            prev_cid = post.get_cam_id(prev_cpid)
            prev_pid = post.get_person_id(prev_cpid)

            if prev_cid == start_cid and prev_pid == start_pid and depth > 1:
                # print("EXIT")
                return [], depth, 0

            for cpid in cpids:
                cid = post.get_cam_id(cpid)
                pid = post.get_person_id(cpid)

                if prev_cpid == cpid:
                    continue

                # print("[{}] TRY TO MATCH ({}, {}) and ({}, {})".format(depth, prev_cid, prev_pid, cid ,pid))

                if cid <= prev_cid:
                    cpid = start_cpid
                    tmp_cpid, tmp_depth, tmp_dist = self.__get_minimum_cluster(start_cpid, start_cpid, cpids, color_map, depth+1)
                else:
                    tmp_cpid, tmp_depth, tmp_dist = self.__get_minimum_cluster(start_cpid, cpid, cpids, color_map, depth+1)

                tmp_cpid.append(cpid)
                tmp_depth += 1
                tmp_dist += self.__get_diff_between_color(color_map[prev_cpid], color_map[cpid])

                # print("RET ", tmp_cpid)

                if max_depth < len(tmp_cpid):
                    max_depth = len(tmp_cpid)
                    ret_cpid = tmp_cpid
                elif max_depth == len(tmp_cpid):
                    if min_dist > tmp_dist:
                        min_dist = tmp_dist
                        ret_cpid = tmp_cpid

        # print("FIN RET : {} SIZE ({})".format(ret_cpid, len(ret_cpid)))
        return ret_cpid, max_depth, min_dist

    def __get_diff_between_color(self, color1, color2):
        color1 = np.array(color1)
        color2 = np.array(color2)
        return np.linalg.norm(color1 - color2)

    def update_person_table_with_position(self, skeleton_manager, cluster_num):
        if self.__is_too_closed is True and self.__valid_cluster is not None:
            logging.info(" ClusterManager: Skip to update person table and reuse valid cluster table")
            self.reuse_valid_cluster(skeleton_manager)
            return

        logging.info(" ClusterManager: Update person table with position")
        max_person_num = 0
        position_idx = np.empty((0, 2)) # cam_id, person_id
        position_arr = np.empty((0, 2)) # X, Y

        for cam_id in range(1, self.__cam_num+1):
            transform = self.__transformation['T'+str(cam_id)+'1']
            person_num = 0
            for person_id in range(0, self.__person_num):
                is_skeleton_valid = skeleton_manager.is_skeleton_valid(cam_id, person_id)
                # skeleton = skeleton_manager.get_skeleton(cam_id, person_id)
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
            num_of_modified, cluster_arr = self.__get_cluster_arr(position_arr, position_idx, max_person_num)
            logging.debug("[DISTANCE] Number of modified elements in clustering {}".format(num_of_modified))

            if num_of_modified >= 2:
                logging.info(" ClusterManager: Skip to update person table and reuse valid cluster table")
                self.reuse_valid_cluster(skeleton_manager)
                return

            for i in range(len(cluster_arr)):
                cluster_id = cluster_arr[i]
                if cluster_id >= 0:
                    self.__cluster_table[cluster_id]['is_valid'] = True
                    self.__cluster_table[cluster_id]['count'] += 1
                    self.__cluster_table[cluster_id]['cpid'].append(post.get_cpid(position_idx[i][0], position_idx[i][1])) # cam_id, person_id
                    self.__cluster_table[cluster_id]['position'].append(position_arr[i]) # X, Y

    def reuse_valid_cluster(self, skeleton_manager):
        if self.__valid_cluster is not None:
            logging.info(" ClusterManager: Reuse valid cluster table")
            self.__cluster_table = copy.deepcopy(self.__valid_cluster)

            for cluster_id in range(0, self.__person_num):
                for idx, cpid in enumerate(self.__cluster_table[cluster_id]['cpid']):
                    cam_id = post.get_cam_id(cpid)
                    person_id = post.get_person_id(cpid)
                    if skeleton_manager.is_skeleton_valid(cam_id, person_id) is True:
                        transform = self.__transformation['T'+str(cam_id)+'1']
                        self.__cluster_table[cluster_id]['position'][idx] = self.__get_average_position(skeleton_manager, cam_id, person_id, transform)

            #print("Reuse valid cluster \n\n")
            #print(self.__cluster_table)
            #print("\n\n")

    def update_person_table_with_hint(self, tracking_table, max_person_num):
        if self.__is_too_closed is False:
            return

        logging.info(" ClusterManager: Update person table with hint")
        for cluster_id in range(self.__person_num):
            if self.__cluster_table[cluster_id]['is_valid'] is False:
                continue
            cpid_from_cluster_table = self.__cluster_table[cluster_id]['cpid']

            for tracking_id in range(max_person_num):
                if tracking_table[tracking_id]['is_valid'] is False:
                    continue

                diff_between_tables = 0
                same_element = []
                cpid_from_tracking_table = tracking_table[tracking_id]['cpid']
                if len(cpid_from_cluster_table) > 0:
                    same_element = self.__get_same_element_in_list(cpid_from_cluster_table, cpid_from_tracking_table)
                    diff_between_tables = len(same_element) / len(cpid_from_cluster_table)
                    logging.debug("Diff between tables {}".format(diff_between_tables))

                if diff_between_tables < 1 and diff_between_tables > 0.7:
                    if len(same_element) < 3:
                        logging.info(" ClusterManager: Change cluster result with tracking table")
                        self.__cluster_table[cluster_id]['cpid'] = cpid_from_tracking_table
                        self.__cluster_table[cluster_id]['count'] = len(cpid_from_tracking_table)
                    else:
                        logging.info(" ClusterManager: Change cluster result with overlapped table *********")
                        self.__cluster_table[cluster_id]['cpid'] = list(same_element)
                        self.__cluster_table[cluster_id]['count'] = len(same_element)

    def __get_same_element_in_list(self, list1, list2):
        return set(list1) & set(list2)

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

    def __get_cluster_arr(self, position_arr, position_idx, max_person_num):
        num_of_modified = 0
        ret = []

        logging.info(" ClusterManager: Clustering... {} people".format(max_person_num))
        if len(position_arr) <= max_person_num:
            return num_of_modified, ret

        cluster = AgglomerativeClustering(n_clusters=max_person_num, affinity='euclidean', linkage='ward')
        ret = cluster.fit_predict(position_arr)

        for i in range(len(ret)):
            logging.debug("... ({}, {}) : {} --> {}".format(int(position_idx[i][0]), int(position_idx[i][1]), position_arr[i], ret[i]))

        num_of_modified, ret = self.__remove_duplicated_person(position_idx, position_arr, max_person_num, ret)

        return num_of_modified, ret

    def __remove_duplicated_person(self, position_idx, position_arr, max_person_num, cluster_ret):
        ret = np.array(copy.deepcopy(cluster_ret))
        original_cluster = copy.deepcopy(ret)

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
                # print("[{}] : {}".format(int(position_idx[i][0]), min_arr))
                id = 0
                # print("person group : {}".format(person_group[int(position_idx[i][0])][cluster_ret[i]]['id']))
                # print("min_arr : {}".format(min_arr))
                for duplicated_id in person_group[int(position_idx[i][0])][cluster_ret[i]]['id']:
                    if len(person_group[int(position_idx[i][0])][cluster_ret[i]]['id']) == len(min_arr):
                        ret[duplicated_id] = min_arr[id]
                        id += 1
                    else:
                        logging.error(" ClusterManager: Size mismatched")
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

        modified_cluster = ret

        # print("ORIGINAL : ", original_cluster)
        # print("MODIFIED : ", modified_cluster)
        # print("SAME_ELEMENT : ", self.__get_same_element_in_list(original_cluster, modified_cluster))
        num_of_modified = len(original_cluster) - self.__count_diff_element(original_cluster, modified_cluster)

        return num_of_modified, ret

    def __count_diff_element(self, original_cluster, modified_cluster):
        cnt = 0
        for i in range(len(original_cluster)):
            if original_cluster[i] == modified_cluster[i]:
                cnt += 1
        return cnt

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
        # if self.__is_too_closed is True:
        #     logging.info(" ClusterManager: Skip to reset person table")
        #     return

        for cluster_id in range(0, self.__person_num):
            if self.__cluster_table[cluster_id]['is_valid'] is True:
                cnt = 0
                avg_x = 0.0
                avg_y = 0.0
                for j in range(len(self.__cluster_table[cluster_id]['position'])):
                    avg_x += self.__cluster_table[cluster_id]['position'][j][0]
                    avg_y += self.__cluster_table[cluster_id]['position'][j][1]
                    cnt += 1
                if cnt > 0:
                    avg_x /= cnt
                    avg_y /= cnt
                self.__cluster_table[cluster_id]['prev_position']=(avg_x, avg_y)
            self.__cluster_table[cluster_id]['is_valid'] = False
            self.__cluster_table[cluster_id]['count'] = 0
            self.__cluster_table[cluster_id]['cpid'] = []
            self.__cluster_table[cluster_id]['position'] = []
