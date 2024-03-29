#---------------------------------------------------
#        2D VIEWER FOR POSE ESTIMATION
#---------------------------------------------------

import cv2
import numpy as np
import math
from visualizer.utils import *
from reconstructor.utils import postprocessor as post

class Viewer2d:
    def __init__(self, args):
        self.cam_id_list = []
        self.height = 1080
        self.width = 1920
        self.display_num = 4
        self.display_list = np.zeros((self.display_num, self.height, self.width, 3), np.uint8)
        self.frame_num = 0
        self.__args = args
        self.__markers = [
            "cv2.MARKER_TILTED_CROSS",
            "cv2.MARKER_SQUARE",
            "cv2.MARKER_TRIANGLE_UP",
            "cv2.MARKER_TRIANGLE_DOWN",
        ]

    def initialize(self, cam_num):
        self.display_num = cam_num
        self.display_list = np.zeros((self.display_num, self.height, self.width, 3), np.uint8)

    def set_background_color(self, display, r, g, b):
        display[:,:,0]=b # Blue
        display[:,:,1]=g # Green
        display[:,:,2]=r # Red

    def merge_display(self):
        resized_display_list = []

        i = 0
        for display in self.display_list:
            cv2.rectangle(display, [0, 0], [self.width, self.height], color=(255, 255, 255), thickness=3)
            resized_display_list.append(cv2.resize(display, dsize=(0,0), fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA))
            i += 1

        col_num = math.ceil(self.display_num / 2)
        top = np.hstack(resized_display_list[:col_num])
        bottom = np.hstack(resized_display_list[col_num:])

        merged_display = np.vstack((top, bottom))

        return merged_display

    def render_cluster_table(self, person_num, cluster_table, skeleton_manager):
        if self.__args.log:
            pass

        self.display_list = np.zeros((self.display_num, self.height, self.width, 3), np.uint8)
        for idx in range(person_num):
            if cluster_table[idx]['is_valid'] is False:
                continue

            for i in range(cluster_table[idx]['count']):
                cpid = cluster_table[idx]['cpid'][i]
                cam_id = post.get_cam_id(cpid)
                person_id = post.get_person_id(cpid)
                if skeleton_manager.is_skeleton_valid(cam_id, person_id) is False:
                    print("[2D RENDER] CPID {} is invalid".format(cpid))
                    continue
                keypoints = skeleton_manager.get_skeleton(cam_id, person_id)
                display = self.display_list[cam_id-1] # index of list startw with zero

                cv2.putText(display, "{}".format(cam_id), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, [255, 255, 255], 3)
                person_id = idx
                color = generate_color_id_u(person_id)

                for part in BODY_BONES_POSE_25:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < display.shape[1] and kp_a[1] < display.shape[0]
                    and kp_b[0] < display.shape[1] and kp_b[1] < display.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 5, cv2.LINE_AA)

                for part in BODY_PARTS_POSE_25:
                    if part is BODY_PARTS_POSE_25.LAST:
                        break
                    kp = keypoints[part.value]
                    if np.isnan(kp[0]) == False and np.isnan(kp[1]) == False:
                        cv2.circle(display, (int(kp[0]), int(kp[1])), 10, color, -1)

        merged_display = self.merge_display()

        cv2.imshow("2D Viewer", merged_display)
        cv2.waitKey(1)

    def render_position(self, person_num, cluster_table):
        #if self.__args.log or self.frame_num % 40 == 0:
        # if self.__args.log:
        room_size = 10 # 10m x 10m
        display = np.ones((600, 600, 3), np.uint8) * 255
        draw_grid(display)
        for cluster_id in range(0, person_num):
            if cluster_table[cluster_id]['is_valid'] is False:
                continue

            for i in range(cluster_table[cluster_id]['count']):
                cpid = cluster_table[cluster_id]['cpid'][i]
                x = cluster_table[cluster_id]['position'][i][0] + room_size/2
                y = cluster_table[cluster_id]['position'][i][1] + room_size/2
                x *= display.shape[0]/room_size*1.5
                y *= display.shape[1]/room_size*1.5
                color = generate_color_id_u(cluster_id)
                cv2.circle(display, (int(x), int(y)), 6, color, -1)
                cv2.putText(display, "({}, {})".format(int(post.get_cam_id(cpid)), int(post.get_person_id(cpid))), (int(x), int(y)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2   )

        cv2.imshow("Position", display)
        cv2.waitKey(1)

    def render_cloth_color(self, person_num, cluster_table, skeleton_manager):
        ratio = 2
        display = np.ones((255 * ratio, 255 * ratio, 3), np.uint8) * 255
        draw_grid(display)
        for cluster_id in range(0, person_num):
            if cluster_table[cluster_id]['is_valid'] is False:
                continue

            for i in range(cluster_table[cluster_id]['count']):
                cpid = cluster_table[cluster_id]['cpid'][i]
                cid = int(post.get_cam_id(cpid))
                pid = int(post.get_person_id(cpid))

                cloth_color = skeleton_manager.get_cloth(cid, pid)
                upper_color = cloth_color[0]

                x = int(upper_color[0]) * ratio
                y = int(upper_color[1]) * ratio

                cv2.drawMarker(display, (x, y), upper_color, eval(self.__markers[cluster_id % len(self.__markers)]), 10, 3)
                cv2.putText(display, "({}, {})".format(int(cid), int(pid)), (x, y+10), cv2.FONT_HERSHEY_SIMPLEX, 1, upper_color, 2)

        cv2.imshow("Color", display)
        cv2.waitKey(1)

    def render_2d(self, data):
        if self.__args.log:
            pass
        # else:
        #     if self.frame_num % 40 == 0:
        #         self.frame_num = 1
        #     else:
        #         self.frame_num += 1
        #         return

        cam_id = data['id']
        annots = data['annots']

        if self.cam_id_list.count(cam_id) == 0:
            self.cam_id_list.append(cam_id)

        display_id = self.cam_id_list.index(cam_id)
        self.display_list[display_id] = np.zeros((self.height, self.width, 3), np.uint8)
        display = self.display_list[display_id]

        cv2.putText(display, "{}".format(cam_id), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, [255, 255, 255], 3)
        for person in annots:
            bbox = person['bbox']
            person_id = person['personID']
            color = generate_color_id_u(person_id)

            cv2.rectangle(display, [int(bbox[0]), int(bbox[1])], [int(bbox[2]), int(bbox[3])], color)

            keypoints = person['keypoints']

            if len(keypoints) == 34:
                keypoints = convert_25_from_34(np.array(keypoints))

            if len(keypoints) == 18:
                #print('keypoint format: 18')
                # Draw skeleton bones
                for part in SKELETON_BONES:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < display.shape[1] and kp_a[1] < display.shape[0]
                    and kp_b[0] < display.shape[1] and kp_b[1] < display.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 3, cv2.LINE_AA)

                # Get spine base coordinates to create backbone
                left_hip = keypoints[BODY_PARTS.LEFT_HIP.value]
                right_hip = keypoints[BODY_PARTS.RIGHT_HIP.value]
                spine = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
                kp_spine = spine
                kp_neck = keypoints[BODY_PARTS.NECK.value]

                # Check that the keypoints are inside the image
                if(kp_spine[0] < display.shape[1] and kp_spine[1] < display.shape[0]
                and kp_neck[0] < display.shape[1] and kp_neck[1] < display.shape[0]
                and kp_spine[0] > 0 and kp_spine[1] > 0 and kp_neck[0] > 0 and kp_neck[1] > 0
                and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                    cv2.line(display, (int(kp_spine[0]), int(kp_spine[1])), (int(kp_neck[0]), int(kp_neck[1])), color, 3, cv2.LINE_AA)

                # Skeleton joints for spine
                if(kp_spine[0] < display.shape[1] and kp_spine[1] < display.shape[0]
                and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                    cv2.circle(display, (int(kp_spine[0]), int(kp_spine[1])), 6, color, -1)

            elif len(keypoints) == 25:
                #print('keypoint format: 25')
                # Draw skeleton bones
                for part in BODY_BONES_POSE_25:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < display.shape[1] and kp_a[1] < display.shape[0]
                    and kp_b[0] < display.shape[1] and kp_b[1] < display.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 5, cv2.LINE_AA)

                color_left = generate_color_id_u(person_id + 4)
                color_right = generate_color_id_u(person_id + 5)

                for part in BODY_PARTS_POSE_25:
                    if part is BODY_PARTS_POSE_25.LAST:
                        break
                    kp = keypoints[part.value]
                    cv2.circle(display, (int(kp[0]), int(kp[1])), 10, color, -1)


            elif len(keypoints) == 34:
                #print('keypoint format: 34')
                # Draw skeleton bones
                for part in BODY_BONES_POSE_34:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < display.shape[1] and kp_a[1] < display.shape[0]
                    and kp_b[0] < display.shape[1] and kp_b[1] < display.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

                color_left = generate_color_id_u(person_id + 4)
                color_right = generate_color_id_u(person_id + 5)

                for part in BODY_PARTS_POSE_34:
                    kp = keypoints[part.value]
                    # Check that the keypoints are inside the image
                    if(kp[0] < display.shape[1] and kp[1] < display.shape[0]):
                        if (part == BODY_PARTS_POSE_34.LEFT_CLAVICLE or
                                part == BODY_PARTS_POSE_34.LEFT_SHOULDER or
                                part == BODY_PARTS_POSE_34.LEFT_ELBOW or
                                part == BODY_PARTS_POSE_34.LEFT_WRIST or
                                part == BODY_PARTS_POSE_34.LEFT_HAND or
                                part == BODY_PARTS_POSE_34.LEFT_HANDTIP or
                                part == BODY_PARTS_POSE_34.LEFT_THUMB or
                                part == BODY_PARTS_POSE_34.LEFT_HIP or
                                part == BODY_PARTS_POSE_34.LEFT_KNEE or
                                part == BODY_PARTS_POSE_34.LEFT_ANKLE or
                                part == BODY_PARTS_POSE_34.LEFT_FOOT or
                                part == BODY_PARTS_POSE_34.LEFT_HEEL or
                                part == BODY_PARTS_POSE_34.LEFT_EYE or
                                part == BODY_PARTS_POSE_34.LEFT_EAR):
                            cv2.circle(display, (int(kp[0]), int(kp[1])), 3, color_left, -1)
                        elif (part == BODY_PARTS_POSE_34.RIGHT_CLAVICLE or
                                part == BODY_PARTS_POSE_34.RIGHT_SHOULDER or
                                part == BODY_PARTS_POSE_34.RIGHT_ELBOW or
                                part == BODY_PARTS_POSE_34.RIGHT_WRIST or
                                part == BODY_PARTS_POSE_34.RIGHT_HAND or
                                part == BODY_PARTS_POSE_34.RIGHT_HANDTIP or
                                part == BODY_PARTS_POSE_34.RIGHT_THUMB or
                                part == BODY_PARTS_POSE_34.RIGHT_HIP or
                                part == BODY_PARTS_POSE_34.RIGHT_KNEE or
                                part == BODY_PARTS_POSE_34.RIGHT_ANKLE or
                                part == BODY_PARTS_POSE_34.RIGHT_FOOT or
                                part == BODY_PARTS_POSE_34.RIGHT_HEEL or
                                part == BODY_PARTS_POSE_34.RIGHT_EYE or
                                part == BODY_PARTS_POSE_34.RIGHT_EAR):
                            cv2.circle(display, (int(kp[0]), int(kp[1])), 3, color_right, -1)
                        else:
                            cv2.circle(display, (int(kp[0]), int(kp[1])), 3, color, -1)

        merged_display = self.merge_display()

        cv2.imshow("2D Viewer: Skeleton", merged_display)
        cv2.waitKey(1)

