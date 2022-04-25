#---------------------------------------------------
#        2D VIEWER FOR POSE ESTIMATION
#---------------------------------------------------

import cv2
import numpy as np
from visualizer.utils import *

class Viewer2d:
    def __init__(self):
        self.cam_id_list = []
        self.height = 720
        self.width = 1280
        self.display_num = 4
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
            resized_display_list.append(cv2.resize(display, dsize=(0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
            i += 1

        top = np.hstack((resized_display_list[0], resized_display_list[1]))
        bottom = np.hstack((resized_display_list[2], resized_display_list[3]))
        merged_display = np.vstack((top, bottom))

        return merged_display


    def render_2d(self, data):
        cam_id = data['id']
        timestamp = data['timestamp']
        annots = data['annots']

        if self.cam_id_list.count(cam_id) == 0:
            self.cam_id_list.append(cam_id)

        display_id = self.cam_id_list.index(cam_id)
        self.display_list[display_id] = np.zeros((self.height, self.width, 3), np.uint8)
        display = self.display_list[display_id]
        for person in annots:
            bbox = person['bbox']
            person_id = person['personID']
            color = generate_color_id_u(person_id)

            cv2.rectangle(display, [bbox[0], bbox[1]], [bbox[2], bbox[3]], color)

            keypoints = person['keypoints']

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
                        cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

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
                    cv2.line(display, (int(kp_spine[0]), int(kp_spine[1])), (int(kp_neck[0]), int(kp_neck[1])), color, 1, cv2.LINE_AA)

                # Skeleton joints for spine
                if(kp_spine[0] < display.shape[1] and kp_spine[1] < display.shape[0]
                and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                    cv2.circle(display, (int(kp_spine[0]), int(kp_spine[1])), 3, color, -1)

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
                        cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

                color_left = generate_color_id_u(person_id + 4)
                color_right = generate_color_id_u(person_id + 5)

                for part in BODY_PARTS_POSE_25:
                    if part is BODY_PARTS_POSE_25.LAST:
                        break
                    kp = keypoints[part.value]
                    # Check that the keypoints are inside the image
                    if(kp[0] < display.shape[1] and kp[1] < display.shape[0]):
                        if (part == BODY_PARTS_POSE_25.LEFT_SHOULDER or
                                part == BODY_PARTS_POSE_25.LEFT_ELBOW or
                                part == BODY_PARTS_POSE_25.LEFT_WRIST or
                                part == BODY_PARTS_POSE_25.LEFT_HIP or
                                part == BODY_PARTS_POSE_25.LEFT_KNEE or
                                part == BODY_PARTS_POSE_25.LEFT_ANKLE or
                                part == BODY_PARTS_POSE_25.LEFT_FOOT or
                                part == BODY_PARTS_POSE_25.LEFT_HEEL or
                                part == BODY_PARTS_POSE_25.LEFT_EYE or
                                part == BODY_PARTS_POSE_25.LEFT_EAR):
                            cv2.circle(display, (int(kp[0]), int(kp[1])), 5, color_left, -1)
                        elif (part == BODY_PARTS_POSE_25.RIGHT_SHOULDER or
                                part == BODY_PARTS_POSE_25.RIGHT_ELBOW or
                                part == BODY_PARTS_POSE_25.RIGHT_WRIST or
                                part == BODY_PARTS_POSE_25.RIGHT_HIP or
                                part == BODY_PARTS_POSE_25.RIGHT_KNEE or
                                part == BODY_PARTS_POSE_25.RIGHT_ANKLE or
                                part == BODY_PARTS_POSE_25.RIGHT_FOOT or
                                part == BODY_PARTS_POSE_25.RIGHT_HEEL or
                                part == BODY_PARTS_POSE_25.RIGHT_EYE or
                                part == BODY_PARTS_POSE_25.RIGHT_EAR):
                            cv2.circle(display, (int(kp[0]), int(kp[1])), 5, color_right, -1)
                        else:
                            cv2.circle(display, (int(kp[0]), int(kp[1])), 5, color, -1)


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

        cv2.imshow("2D Viewer", merged_display)
        cv2.waitKey(5)

