#---------------------------------------------------
#        2D VIEWER FOR POSE ESTIMATION
#---------------------------------------------------

import cv2
import numpy as np
from visualizer.utils import *

def render_2D(data):
    id = data['id']
    timestamp = data['timestamp']
    height = data['height']
    width = data['width']
    annots = data['annots']

    display = np.zeros((height, width, 3), np.uint8)

    for person in annots:
        bbox = person['bbox']
        person_id = person['personID']
        color = generate_color_id_u(person_id)

        cv2.rectangle(display, [bbox[0], bbox[1]], [bbox[2], bbox[3]], color)

        keypoints = person['keypoints']
        if len(keypoints) == 18:
            print('keypoint format: 18')
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

        elif len(keypoints) == 34:
            print('keypoint format: 34')

        for kp in keypoints:
            if(kp[0] < display.shape[1] and kp[1] < display.shape[0]):
                cv2.circle(display, (int(kp[0]), int(kp[1])), 3, color, -1)

    cv2.imshow("2D Viewer", display)
    cv2.waitKey(10)
