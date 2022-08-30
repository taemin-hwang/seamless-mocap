import numpy as np
import math
import logging
import json

from visualizer import utils
from reconstructor.utils import preprocessor as pre

class SkeletonManager:
    def __init__(self, args, cam_num, person_num, calibration):
        self.__args = args
        self.__cam_num = cam_num
        self.__person_num = person_num
        self.__buffer_size = 5
        self.__life_counter = np.zeros((self.__cam_num+1, self.__person_num))
        self.__max_life = 5
        if self.__args.log:
            pass
        else:
            self.__skeleton_table = self.__get_initial_skeleton_table(calibration)
        self.__frame_buffer_keypoint = np.ones((self.__cam_num+1, self.__person_num, self.__buffer_size, 25, 3))
        self.__frame_buffer_position = np.ones((self.__cam_num+1, self.__person_num, self.__buffer_size, 6, 4))

    def get_skeleton_table(self):
        return self.__skeleton_table

    def is_skeleton_valid(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['is_valid']

    def get_skeleton(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['keypoint']

    def get_position(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['position']

    def reset_skeleton_table(self):
        for cam_id in range(1, self.__cam_num+1):
            for person_id in range(0, self.__person_num):
                if self.__life_counter[cam_id][person_id] <= 0:
                    self.__skeleton_table[cam_id][person_id]['is_valid'] = False
                    self.__skeleton_table[cam_id][person_id]['keypoint'] = np.zeros((25, 3)).tolist()
                    self.__skeleton_table[cam_id][person_id]['position'] = np.zeros((6, 4)).tolist()
                else:
                    self.__life_counter[cam_id][person_id] -= 1

    def update_skeleton_table(self, json_data):
        logging.info(" SkeletonManager: Update skeleton table")
        bboxes = {}
        cam_id = json_data['id']
        for person_data in json_data['annots']:
            person_id = person_data['personID']
            bbox = person_data['bbox']
            bboxes[person_id] = np.array(bbox)
            if cam_id < 0 or cam_id > self.__cam_num or person_id < 0 or person_id >= self.__person_num:
                logging.debug('Invalid data : {}, {}'.format(cam_id, person_id))
                continue
            keypoints_34 = np.array(person_data['keypoints'])
            keypoints_25 = utils.convert_25_from_34(keypoints_34)
            self.__frame_buffer_keypoint[cam_id][person_id], avg_keypoints_25 = pre.smooth_2d_pose(self.__frame_buffer_keypoint[cam_id][person_id], keypoints_25)
            self.__life_counter[cam_id][person_id] = self.__max_life
            self.__skeleton_table[cam_id][person_id]['is_valid'] = True
            self.__skeleton_table[cam_id][person_id]['keypoint'] = avg_keypoints_25.tolist()

        for person_data in json_data['annots']:
            person_id = person_data['personID']
            if cam_id < 0 or cam_id > self.__cam_num or person_id < 0 or person_id >= self.__person_num:
                logging.debug('Invalid data : {}, {}'.format(cam_id, person_id))
                continue
            for prev_bbox in bboxes:
                if prev_bbox == person_id:
                    continue
                if pre.is_bbox_overlapped(bboxes[prev_bbox], bboxes[person_id]):
                    self.__skeleton_table[cam_id][person_id]['position'] = self.__frame_buffer_position[cam_id][person_id][self.__buffer_size-1].tolist()
                    logging.warning("Bounding boxes overlapped : {} and {} from camera {} ".format(prev_bbox, person_id, cam_id))
                else:
                    self.__frame_buffer_position[cam_id][person_id], avg_position = pre.smooth_position(self.__frame_buffer_position[cam_id][person_id], person_data['position'])
                    self.__skeleton_table[cam_id][person_id]['position'] = avg_position.tolist()

    def read_skeleton_table(self, frame_number, log_dir):
        file_path = log_dir + str(frame_number).zfill(6) + ".json"
        logging.debug(file_path)
        with open(file_path, "r") as outfile:
            self.__skeleton_table = json.load(outfile, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
            for cam_id in range(1, self.__cam_num+1):
                for person_id in range(0, self.__person_num):
                    if self.__skeleton_table[cam_id][person_id]['is_valid'] is True:
                        self.__life_counter[cam_id][person_id] = self.__max_life
                    else:
                        if self.__life_counter[cam_id][person_id] > 0:
                            self.__skeleton_table[cam_id][person_id]['is_valid'] = True

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
                self.__life_counter[cam_id][person_id] = 0
        return skeleton_table
