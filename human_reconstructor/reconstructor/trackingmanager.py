import numpy as np
import math

import logging
from reconstructor.utils import postprocessor as post

class TrackingManager:
    def __init__(self, args, person_num, max_person_num):
        self.__args = args
        self.__person_num = person_num
        self.__max_person_num = max_person_num
        self.__frame_buffer = np.ones((self.__person_num, 10, 25, 4)) # buffersize = 5
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
        data = []
        valid_arr = np.zeros((len(reconstruction_list)))
        idx = 0
        for person in reconstruction_list:
            person_id = person[0]
            person_keypoint = person[1]
            person_repro_err = person[2]
            dist = self.__check_repro_error(person_keypoint, person_repro_err, triangulate_param[person_id]['keypoint'], triangulate_param[person_id]['P'])
            person_keypoint[:, :3] /= 2
            logging.debug("Projection Error : {}".format(np.mean(dist)))
            if np.mean(dist) < 100:
                #data.append({'id' : person_id, 'keypoints3d' : person_keypoint})
                valid_arr[idx] = np.mean(dist)
            idx += 1

        need_to_skip = False
        a_idx = 0
        for person_A in reconstruction_list:
            if valid_arr[a_idx] <= 0:
                continue
            is_too_closed = False
            person_A_id = person_A[0]
            person_A_keypoint = person_A[1]
            person_A_center_position = post.get_center_position(person_A_keypoint)

            b_idx = 0
            for person_B in reconstruction_list:
                person_B_id = person_B[0]
                if person_A_id == person_B_id:
                    continue
                if valid_arr[b_idx] <= 0:
                    continue
                person_B_keypoint = person_B[1]
                person_B_center_position = post.get_center_position(person_B_keypoint)
                dist_between_A_and_B = np.linalg.norm(person_A_center_position - person_B_center_position)
                logging.debug("Dist between {} and {} : {}".format(person_A_id, person_B_id, dist_between_A_and_B))

                if dist_between_A_and_B <= 1.0:
                    logging.warning("SKIP THESE PERSON {} and PERSON {}, TOO CLOSE : {}".format(person_A_id, person_B_id, dist_between_A_and_B))
                    is_too_closed = True
                    continue
                b_idx += 1

            if is_too_closed is False:
                tracking_id = self.__find_tracking_id_from_distance(triangulate_param, person_A_id, person_A_keypoint)
            else:
                tracking_id = self.__find_tracking_id_from_cpid(triangulate_param, person_A_id)
                need_to_skip = True

            if tracking_id >= 0:
                logging.info("Assign person {} to {}".format(a_idx, tracking_id))

                self.__frame_buffer[tracking_id], ret = post.smooth_3d_pose(self.__frame_buffer[tracking_id], person_A_keypoint)
                # ret = person_A_keypoint
                self.__tracking_table[tracking_id]['keypoints3d'] = ret
                if valid_arr[a_idx] < 10:
                    self.__tracking_table[tracking_id]['cpid'] = triangulate_param[person_A_id]['cpid']
                data.append({'id' : tracking_id, 'keypoints3d' : ret})
            a_idx += 1

        return need_to_skip, data

    def __check_repro_error(self, keypoints3d, kpts_repro, keypoints2d, P):
        square_diff = (keypoints2d[:, :, :2] - kpts_repro[:, :, :2])**2
        conf = keypoints3d[None, :, -1:]
        conf = (keypoints3d[None, :, -1:] > 0) * (keypoints2d[:, :, -1:] > 0)
        dist = np.sqrt((((kpts_repro[..., :2] - keypoints2d[..., :2])*conf)**2).sum(axis=-1))
        return dist

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