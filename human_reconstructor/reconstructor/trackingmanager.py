import numpy as np
import math

import logging
import copy
from reconstructor.utils import postprocessor as post

class TrackingManager:
    def __init__(self, args, person_num, max_person_num):
        self.__args = args
        self.__person_num = person_num
        self.__max_person_num = max_person_num
        self.__frame_buffer = np.ones((self.__person_num, 3, 25, 4)) # buffersize = 5
        self.__tracking_table = self.__get_initial_tracking_table()

    def get_tracking_table(self):
        return self.__tracking_table

    def is_tracking_valid(self, cluster_id):
        return self.__tracking_table[cluster_id]['is_valid']

    def get_cpid(self, cluster_id):
        return self.__tracking_table[cluster_id]['cpid']

    def get_keypoints3d(self, cluster_id):
        return self.__tracking_table[cluster_id]['keypoints3d']

    def get_tracking_keypoints(self, reconstruction_list, triangulate_param):
        logging.info(" TrackingManager: Get tracking keypoints")
        is_too_closed = False
        is_valid_cluster = False
        data = []

        # Rescale keypoint to 0.5
        self.__rescale_keypoint(reconstruction_list, 0.5)

        if len(reconstruction_list) == 0:
            return False, False, []
        elif self.__max_person_num == 1 or len(reconstruction_list) == 1:
            logging.info(" TrackingManager: Skip to keep tracking keypoints, assign id 1")
            person_keypoint = reconstruction_list[0][1]
            self.__frame_buffer[0], ret = post.smooth_3d_pose(self.__frame_buffer[0], person_keypoint)
            is_valid_cluster = self.__is_valid_cluster(reconstruction_list, triangulate_param, self.__max_person_num)
            data.append({'id' : 0, 'keypoints3d' : ret})
            return False, is_valid_cluster, data

        is_valid_cluster, valid_person = self.__is_valid_cluster(reconstruction_list, triangulate_param, self.__max_person_num)
        is_too_closed = self.__is_too_closed(reconstruction_list, valid_person)

        for idx, person in enumerate(reconstruction_list):
            person_id = person[0]
            person_keypoint = person[1]
            if valid_person[idx] <= 0:
                continue
            # data.append({'id' : person_id, 'keypoints3d' : person_keypoint})
            else:
                tracking_id = self.__get_tracking_id(is_too_closed, triangulate_param, person_id, person_keypoint)
                if tracking_id >= 0:
                    self.__frame_buffer[tracking_id], ret = post.smooth_3d_pose(self.__frame_buffer[tracking_id], person_keypoint)
                    self.__tracking_table[tracking_id]['cpid'] = triangulate_param[person_id]['cpid']
                    self.__tracking_table[tracking_id]['keypoints3d'] = ret
                    data.append({'id' : tracking_id, 'keypoints3d' : ret})

        if is_too_closed is True:
            logging.info(" TrackingManager: People are too closed")
        if is_valid_cluster is True:
            logging.info(" TrackingManager: Cluster is valid")

        return is_too_closed, is_valid_cluster, data

    def __is_valid_cluster(self, reconstruction_list, triangulate_param, max_person_num):
        is_valid_cluster = False
        valid_person_cnt = 0
        sum_repro_err = 0
        valid_person = np.zeros((len(reconstruction_list)))
        for id, person in enumerate(reconstruction_list):
            person_id = person[0]
            person_keypoint = copy.deepcopy(person[1])
            person_keypoint[:, 3] *= 2
            person_repro_err = person[2]
            average_repro_err = np.mean(self.__check_repro_error(person_keypoint, person_repro_err, triangulate_param[person_id]['keypoint'], triangulate_param[person_id]['P']))
            logging.debug(" TrackingManager: Average Reprojection Error is {}".format(average_repro_err))
            sum_repro_err += average_repro_err
            if average_repro_err < 15:
                valid_person_cnt += 1
            if average_repro_err < 100:
                valid_person[id] = 1
        if valid_person_cnt == max_person_num and (sum_repro_err / max_person_num) < 10:
            is_valid_cluster = True
        return is_valid_cluster, valid_person

    def __check_repro_error(self, keypoints3d, kpts_repro, keypoints2d, P):
        square_diff = (keypoints2d[:, :, :2] - kpts_repro[:, :, :2])**2
        conf = keypoints3d[None, :, -1:]
        conf = (keypoints3d[None, :, -1:] > 0) * (keypoints2d[:, :, -1:] > 0)
        dist = np.sqrt((((kpts_repro[..., :2] - keypoints2d[..., :2])*conf)**2).sum(axis=-1))
        return dist

    def __is_too_closed(self, reconstruction_list, valid_person):
        is_too_closed = False
        min_distance_from_person = np.inf
        for idx, person in enumerate(reconstruction_list):
            person_id = person[0]
            person_keypoint = person[1]
            if valid_person[idx] <= 0:
                continue
            else:
                distance_between_person = self.__get_min_distance_between_person(person_id, person_keypoint, reconstruction_list, valid_person)
                if min_distance_from_person > distance_between_person:
                    min_distance_from_person = distance_between_person

        if min_distance_from_person < 1.0:
            is_too_closed = True
        return is_too_closed

    def __rescale_keypoint(self, reconstruction_list, scale):
        for person in reconstruction_list:
            person_keypoint = person[1]
            person_keypoint[:, :3] *= scale

    def __get_min_distance_between_person(self, from_id, from_keypoint, reconstruction_list, valid_person):
        from_position = post.get_center_position(from_keypoint)
        min_distance = np.inf
        for idx, person in enumerate(reconstruction_list):
            to_id = person[0]
            to_keypoint = person[1]
            to_position = post.get_center_position(to_keypoint)

            if valid_person[idx] <= 0:
                continue
            if from_id == to_id:
                continue

            distance = np.linalg.norm(to_position - from_position)
            logging.debug("Dist between {} and {} : {}".format(from_id, to_id, distance))
            if distance < min_distance:
                min_distance = distance
        return min_distance

    def __get_tracking_id(self, is_too_closed, triangulate_param, person_id, person_keypoint):
        tracking_id = -1
        print("Try to assign tracking id of {}".format(person_id))
        if is_too_closed is False:
            tracking_id = self.__find_tracking_id_from_distance(triangulate_param, person_id, person_keypoint)
        else:
            # tracking_id = self.__find_tracking_id_from_cpid(triangulate_param, person_id)
            tracking_id = self.__find_tracking_id_from_distance(triangulate_param, person_id, person_keypoint)

        if tracking_id >= 0:
            logging.info("Assign person {} to {}".format(person_id, tracking_id))
        else:
            logging.error("Tracking ID is less then 0: {} to {}".format(person_id, tracking_id))
        return tracking_id

    def __find_tracking_id_from_distance(self, triangulate_param, person_id, person_keypoint):
        min_err = np.inf
        min_id = -1
        for tracking_id in range(self.__max_person_num):
            tracking_keypoints = self.__tracking_table[tracking_id]['keypoints3d']
            if tracking_keypoints is None:
                self.__tracking_table[tracking_id]['is_valid'] = True
                self.__tracking_table[tracking_id]['keypoints3d'] = person_keypoint
                self.__tracking_table[tracking_id]['cpid'] = triangulate_param[person_id]['cpid']
                break

            err = self.__get_distance_from_keypoints(person_keypoint[:, :3], self.__tracking_table[tracking_id]['keypoints3d'][:, :3])
            logging.debug("ERR : {}".format(err))
            if err < min_err:
                min_err = err
                min_id = tracking_id
        return min_id

    def __find_tracking_id_from_cpid(self, trianguldate_param, person_id):
        max_cnt = 0
        max_id = -1
        for tracking_id in range(self.__max_person_num):
            if self.__tracking_table[tracking_id]['is_valid'] is False:
                continue
            # Count same element between two list
            cnt = self.__count_same_element_in_list(trianguldate_param[person_id]['cpid'], self.__tracking_table[tracking_id]['cpid'])
            if cnt > max_cnt:
                max_cnt = cnt
                max_id = tracking_id
        return max_id

    def __get_distance_from_keypoints(self, keypoints3d1, keypoints3d2):
        # param1: keypoints3d1 is 3D pose from current frame
        # param2: keypoints3d2 is 3D pose from previous frame
        # return: ret is distance between keypoints3d1 and keypoints3d2
        dist = 0
        for i in range(keypoints3d1.shape[0]):
            dist += np.linalg.norm(keypoints3d1[i] - keypoints3d2[i])
        return dist / keypoints3d1.shape[0]

    def __count_same_element_in_list(self, list1, list2):
        logging.debug("list A : \n {}".format(list1))
        logging.debug("list B : \n {}".format(list2))
        return len(set(list1) & set(list2))

    def __get_initial_tracking_table(self):
        tracking_table = {}
        for cluster_id in range(self.__max_person_num):
            tracking_table[cluster_id] = {}
            tracking_table[cluster_id]['is_valid'] = False
            tracking_table[cluster_id]['cpid'] = []
            tracking_table[cluster_id]['keypoints3d'] = None
        return tracking_table