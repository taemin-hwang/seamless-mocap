import numpy as np
import math
from reconstructor.utils import postprocessor as post

class TrackingManager:
    def __init__(self, cluster_num):
        self.__cluster_num = cluster_num
        self.__tracking_table = self.__get_initial_tracking_table()

    def is_tracking_valid(self, cluster_id):
        return self.__tracking_table[cluster_id]['is_valid']

    def get_cpid(self, cluster_id):
        return self.__tracking_table[cluster_id]['cpid']

    def get_keypoints3d(self, cluster_id):
        return self.__tracking_table[cluster_id]['keypoints3d']

    def __find_tracking_id_from_distance(self, triangulate_param, person_id, person_keypoint):
        min_err = np.inf
        min_id = -1
        for tracking_id in range(self.__max_person_num):
            tracking_keypoints = self.__tracking_table[tracking_id]['keypoints3d']
            if tracking_keypoints is None:
                self.__tracking_table[tracking_id]['is_valid'] = True
                self.__tracking_table[tracking_id]['keypoints3d'] = person_keypoint
                self.__tracking_table[tracking_id]['cpid'] = triangulate_param[person_id]['cpid']
                continue

            err = post.get_distance_from_keypoints(person_keypoint[:, :3], self.__tracking_table[tracking_id]['keypoints3d'][:, :3])
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
            cnt = post.count_same_element_in_list(trianguldate_param[person_id]['cpid'], self.__tracking_table[tracking_id]['cpid'])
            if cnt > max_cnt:
                max_cnt = cnt
                max_id = tracking_id
        return max_id

    def __get_initial_tracking_table(self):
        tracking_table = {}
        for cluster_id in range(self.__cluster_num):
            tracking_table[cluster_id] = {}
            tracking_table[cluster_id]['is_valid'] = False
            tracking_table[cluster_id]['cpid'] = []
            tracking_table[cluster_id]['keypoints3d'] = None
        return tracking_table