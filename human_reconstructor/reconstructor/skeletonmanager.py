import numpy as np
import math
import logging
import json

from visualizer import utils
from visualizer.utils import *
from reconstructor.utils import preprocessor as pre

class SkeletonManager:
    def __init__(self, args, cam_num, person_num, calibration, viewer):
        self.__args = args
        self.__cam_num = cam_num
        self.__person_num = person_num
        self.__buffer_size = 5
        self.__life_counter = np.zeros((self.__cam_num+1, self.__person_num))
        self.__max_life = 20
        self.__viewer = viewer
        if self.__args.log:
            pass
        else:
            self.__skeleton_table = self.__get_initial_skeleton_table(calibration)
        self.__frame_buffer_keypoint = np.zeros((self.__cam_num+1, self.__person_num, self.__buffer_size, 25, 3))
        self.__frame_buffer_position = np.zeros((self.__cam_num+1, self.__person_num, self.__buffer_size, 6, 4))
        self.__frame_buffer_cloth = np.zeros((self.__cam_num+1, self.__person_num, self.__buffer_size, 2, 3))

    def show_skeleton_keypoint(self, data):
        self.__viewer.render_2d(data)

    def get_skeleton_table(self):
        return self.__skeleton_table

    def is_skeleton_valid(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['is_valid']

    def get_skeleton(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['keypoint']

    def get_position(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['position']

    def get_cloth(self, cam_id, person_id):
        return self.__skeleton_table[cam_id][person_id]['cloth']

    def reset_skeleton_table(self):
        for cam_id in range(1, self.__cam_num+1):
            for person_id in range(0, self.__person_num):
                self.__skeleton_table[cam_id][person_id]['is_valid'] = False
                #self.__skeleton_table[cam_id][person_id]['keypoint'] = np.zeros((25, 3)).tolist()
                #self.__skeleton_table[cam_id][person_id]['position'] = np.zeros((6, 4)).tolist()
                if self.__life_counter[cam_id][person_id] > 0:
                    self.__life_counter[cam_id][person_id] -= 1

    def update_skeleton_table(self, json_data):
        logging.info(" SkeletonManager: Update skeleton table")

        bboxes = self.__update_keypoint(json_data)
        self.__update_position(json_data, bboxes)
        self.__update_cloth(json_data, bboxes)
        self.__update_validation(json_data)

    def __update_keypoint(self, json_data):
        bboxes = {}
        cam_id = json_data['id']
        for person_data in json_data['annots']:
            person_id = person_data['personID']
            bbox = person_data['bbox']

            bboxes[person_id] = np.array(bbox)
            self.__skeleton_table[cam_id][person_id]['keypoint'] = bbox
            if cam_id < 0 or cam_id > self.__cam_num or person_id < 0 or person_id >= self.__person_num:
                logging.debug('Invalid data : {}, {}'.format(cam_id, person_id))
                continue
            if len(person_data['keypoints']) == 34:
                keypoints_34 = np.array(person_data['keypoints'])
                keypoints_25 = utils.convert_25_from_34(keypoints_34)
            elif len(person_data['keypoints']) == 18:
                keypoints_18 = np.array(person_data['keypoints'])
                keypoints_25 = utils.convert_25_from_18(keypoints_18)
            self.__frame_buffer_keypoint[cam_id][person_id], avg_keypoints_25 = pre.smooth_2d_pose(self.__frame_buffer_keypoint[cam_id][person_id], keypoints_25)
            # self.__skeleton_table[cam_id][person_id]['is_valid'] = True
            self.__skeleton_table[cam_id][person_id]['keypoint'] = avg_keypoints_25.tolist()
        return bboxes

    def __update_position(self, json_data, bboxes):
        cam_id = json_data['id']
        for person_data in json_data['annots']:
            person_id = person_data['personID']

            if 'position' not in person_data:
                break

            person_position = person_data['position']
            if cam_id < 0 or cam_id > self.__cam_num or person_id < 0 or person_id >= self.__person_num:
                logging.warning('Invalid data : {}, {}'.format(cam_id, person_id))
                continue
            is_overlapped = False
            for prev_bbox in bboxes:
                if prev_bbox == person_id:
                    continue
                if pre.is_bbox_overlapped(bboxes[prev_bbox], bboxes[person_id]):
                    logging.warning("Bounding boxes overlapped : {} and {} from camera {} ".format(prev_bbox, person_id, cam_id))
                    is_overlapped = True
            if is_overlapped is False:
                self.__frame_buffer_position[cam_id][person_id], avg_position = pre.smooth_position(self.__frame_buffer_position[cam_id][person_id], person_position)
                self.__skeleton_table[cam_id][person_id]['position'] = avg_position.tolist()
            else:
                self.__skeleton_table[cam_id][person_id]['position'] = self.__frame_buffer_position[cam_id][person_id][self.__buffer_size-1].tolist()

    def __update_cloth(self, json_data, bboxes):
        cam_id = json_data['id']
        for person_data in json_data['annots']:
            person_id = person_data['personID']

            if 'cloth' not in person_data:
                print("ERROR: CLOTH NOT FOUND")
                break

            person_cloth = person_data['cloth']
            if cam_id < 0 or cam_id > self.__cam_num or person_id < 0 or person_id >= self.__person_num:
                logging.warning('Invalid data : {}, {}'.format(cam_id, person_id))
                continue

            is_overlapped = False
            for prev_bbox in bboxes:
                if prev_bbox == person_id:
                    continue
                if pre.is_bbox_overlapped(bboxes[prev_bbox], bboxes[person_id]):
                    logging.warning("Bounding boxes overlapped : {} and {} from camera {} ".format(prev_bbox, person_id, cam_id))
                    self.__skeleton_table[cam_id][person_id]['cloth'] = self.__frame_buffer_cloth[cam_id][person_id][self.__buffer_size-1].tolist()
                    is_overlapped = True
            if is_overlapped is False:
                self.__frame_buffer_cloth[cam_id][person_id], avg_cloth = pre.smooth_cloth(self.__frame_buffer_cloth[cam_id][person_id], person_cloth)
                self.__skeleton_table[cam_id][person_id]['cloth'] = avg_cloth.tolist()

    def __update_validation(self, json_data):
        cam_id = json_data['id']
        for person_data in json_data['annots']:
            person_id = person_data['personID']
            keypoint = self.__skeleton_table[cam_id][person_id]['keypoint']

            is_valid = self.__is_valid(keypoint)
            self.__skeleton_table[cam_id][person_id]['is_valid'] = is_valid

    def __is_valid(self, keypoint):
        ret = True
        ret = ret and (keypoint[BODY_PARTS_POSE_25.RIGHT_SHOULDER.value][2] > 0.2)
        ret = ret and (keypoint[BODY_PARTS_POSE_25.LEFT_SHOULDER.value][2] > 0.2)
        ret = ret and (keypoint[BODY_PARTS_POSE_25.RIGHT_HIP.value][2] > 0.2)
        ret = ret and (keypoint[BODY_PARTS_POSE_25.LEFT_HIP.value][2] > 0.2)
        ret = ret and (keypoint[BODY_PARTS_POSE_25.RIGHT_KNEE.value][2] > 0.2)
        ret = ret and (keypoint[BODY_PARTS_POSE_25.LEFT_KNEE.value][2] > 0.2)
        # ret = ret and (keypoint[BODY_PARTS_POSE_25.RIGHT_ANKLE.value][2] > 0.2)
        # ret = ret and (keypoint[BODY_PARTS_POSE_25.LEFT_ANKLE.value][2] > 0.2)
        return ret

    def read_skeleton_table(self, frame_number, log_dir):
        file_path = log_dir + str(frame_number).zfill(6) + ".json"
        logging.debug(file_path)
        with open(file_path, "r") as outfile:
            self.__skeleton_table = json.load(outfile, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})

    def show_skeleton_position(self):
        room_size = 10 # 10m x 10m
        display = np.ones((1200, 1200, 3), np.uint8) * 255
        draw_grid(display)
        for cam_id in range(1, self.__cam_num+1):
            for person_id in range(0, self.__person_num):
                if self.__skeleton_table[cam_id][person_id]['is_valid'] is False:
                    continue

                print("{}, {} is valid, life counter is {}".format(cam_id, person_id, self.__life_counter[cam_id][person_id]))
                position = self.__skeleton_table[cam_id][person_id]['position']
                for i in range(len(position)):
                    x = position[i][0] + room_size/2
                    y = position[i][1] + room_size/2
                    x *= display.shape[0]/room_size*1.5
                    y *= display.shape[1]/room_size*1.5
                    color = generate_color_id_u(cam_id)
                    cv2.circle(display, (int(x), int(y)), 6, color, -1)
                    cv2.putText(display, "({}, {})".format(int(cam_id), int(person_id)), (int(x), int(y)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            cv2.imshow("2D Viewer: Position", display)
            cv2.waitKey(1)

    def update_life_counter(self):
        for cam_id in range(1, self.__cam_num+1):
            for person_id in range(0, self.__person_num):
                if self.__skeleton_table[cam_id][person_id]['is_valid'] is True:
                    self.__life_counter[cam_id][person_id] = self.__max_life
                elif self.__life_counter[cam_id][person_id] > 0:
                    self.__skeleton_table[cam_id][person_id]['is_valid'] = True
                else:
                    self.__skeleton_table[cam_id][person_id]['is_valid'] = False

    def __get_initial_skeleton_table(self, calibration):
        skeleton_table = {}
        for cam_id in range(1, self.__cam_num+1):
            skeleton_table[cam_id] = {}
            skeleton_table[cam_id]['P'] = calibration[str(cam_id)]['P'].tolist()
            for person_id in range(0, self.__person_num):
                skeleton_table[cam_id][person_id] = {}
                skeleton_table[cam_id][person_id]['is_valid'] = False
                skeleton_table[cam_id][person_id]['bbox'] = np.zeros((2, 2)).tolist()
                skeleton_table[cam_id][person_id]['keypoint'] = np.zeros((25, 3)).tolist()
                skeleton_table[cam_id][person_id]['position'] = np.zeros((6, 4)).tolist()
                skeleton_table[cam_id][person_id]['cloth'] = np.zeros((2, 3)).tolist()
                self.__life_counter[cam_id][person_id] = 0
        return skeleton_table
