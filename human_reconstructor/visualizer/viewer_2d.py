#---------------------------------------------------
#        2D VIEWER FOR POSE ESTIMATION
#---------------------------------------------------

import cv2
import numpy as np
from visualizer.utils import *

cam_id_list = []

def set_background_color(display, r, g, b):
    display[:,:,0]=b # Blue
    display[:,:,1]=g # Green
    display[:,:,2]=r # Red

def merge_display(displaylist, width, height):
    resized_display_list = []

    i = 0
    for display in displaylist:
        cv2.rectangle(display, [0, 0], [width, height], color=(255, 255, 255), thickness=3)
        resized_display_list.append(cv2.resize(display, dsize=(0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
        i += 1

    top = np.hstack((resized_display_list[0], resized_display_list[1]))
    bottom = np.hstack((resized_display_list[2], resized_display_list[3]))
    merged_display = np.vstack((top, bottom))

    return merged_display


def render_2D(data):
    global cam_id_list
    cam_id = data['id']
    timestamp = data['timestamp']
    height = data['height']
    width = data['width']
    annots = data['annots']

    if cam_id_list.count(cam_id) == 0:
        cam_id_list.append(cam_id)

    display_id = cam_id_list.index(cam_id)
    display_num = 4
    display_list = np.zeros((display_num, height, width, 3), np.uint8)

    #display = np.zeros((height, width, 3), np.uint8)
    set_background_color(display_list[0], 51, 0, 25)
    set_background_color(display_list[1], 51, 0, 25)
    set_background_color(display_list[2], 51, 0, 25)
    set_background_color(display_list[3], 51, 0, 25)

    display = display_list[display_id]

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
            # Draw skeleton bones
            for part in BODY_BONES_POSE_34:
                kp_a = keypoints[part[0].value]
                kp_b = keypoints[part[1].value]
                # Check that the keypoints are inside the image
                if(kp_a[0] < display.shape[1] and kp_a[1] < display.shape[0] 
                and kp_b[0] < display.shape[1] and kp_b[1] < display.shape[0]
                and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                    cv2.line(display, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

        for kp in keypoints:
            if(kp[0] < display.shape[1] and kp[1] < display.shape[0]):
                cv2.circle(display, (int(kp[0]), int(kp[1])), 3, color, -1)

    merged_display = merge_display(display_list, width, height)

    cv2.imshow("2D Viewer", merged_display)
    cv2.waitKey(10)
