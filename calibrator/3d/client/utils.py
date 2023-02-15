import numpy as np
import pyzed.sl as sl
from enum import Enum
import os

class BODY_PARTS_POSE_25(Enum):
    NOSE = 0
    NECK = 1
    RIGHT_SHOULDER = 2
    RIGHT_ELBOW = 3
    RIGHT_WRIST = 4
    LEFT_SHOULDER = 5
    LEFT_ELBOW = 6
    LEFT_WRIST = 7
    MID_HIP = 8
    RIGHT_HIP = 9
    RIGHT_KNEE = 10
    RIGHT_ANKLE = 11
    LEFT_HIP = 12
    LEFT_KNEE = 13
    LEFT_ANKLE = 14
    RIGHT_EYE = 15
    LEFT_EYE = 16
    RIGHT_EAR = 17
    LEFT_EAR = 18
    LEFT_FOOT = 19
    LEFT_TOE = 20
    LEFT_HEEL = 21
    RIGHT_FOOT = 22
    RIGHT_TOE = 23
    RIGHT_HEEL = 24
    LAST = 25

class BODY_PARTS_POSE_34(Enum):
    PELVIS = 0
    NAVAL_SPINE = 1
    CHEST_SPINE = 2
    NECK = 3
    LEFT_CLAVICLE = 4
    LEFT_SHOULDER = 5
    LEFT_ELBOW = 6
    LEFT_WRIST = 7
    LEFT_HAND = 8
    LEFT_HANDTIP = 9
    LEFT_THUMB = 10
    RIGHT_CLAVICLE = 11
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 13
    RIGHT_WRIST = 14
    RIGHT_HAND = 15
    RIGHT_HANDTIP = 16
    RIGHT_THUMB = 17
    LEFT_HIP = 18
    LEFT_KNEE = 19
    LEFT_ANKLE = 20
    LEFT_FOOT = 21
    RIGHT_HIP = 22
    RIGHT_KNEE = 23
    RIGHT_ANKLE = 24
    RIGHT_FOOT = 25
    HEAD = 26
    NOSE = 27
    LEFT_EYE = 28
    LEFT_EAR = 29
    RIGHT_EYE = 30
    RIGHT_EAR = 31
    LEFT_HEEL = 32
    RIGHT_HEEL = 33
    LAST = 34

BODY_BONES_POSE_25 = [ (BODY_PARTS_POSE_25.NOSE, BODY_PARTS_POSE_25.NECK),
                (BODY_PARTS_POSE_25.NECK, BODY_PARTS_POSE_25.RIGHT_SHOULDER),
                (BODY_PARTS_POSE_25.RIGHT_SHOULDER, BODY_PARTS_POSE_25.RIGHT_ELBOW),
                (BODY_PARTS_POSE_25.RIGHT_ELBOW, BODY_PARTS_POSE_25.RIGHT_WRIST),
                (BODY_PARTS_POSE_25.NECK, BODY_PARTS_POSE_25.LEFT_SHOULDER),
                (BODY_PARTS_POSE_25.NECK, BODY_PARTS_POSE_25.RIGHT_HIP),
                (BODY_PARTS_POSE_25.NECK, BODY_PARTS_POSE_25.LEFT_HIP),
                (BODY_PARTS_POSE_25.LEFT_SHOULDER, BODY_PARTS_POSE_25.LEFT_ELBOW),
                (BODY_PARTS_POSE_25.LEFT_ELBOW, BODY_PARTS_POSE_25.LEFT_WRIST),
                (BODY_PARTS_POSE_25.RIGHT_HIP, BODY_PARTS_POSE_25.RIGHT_KNEE),
                (BODY_PARTS_POSE_25.RIGHT_KNEE, BODY_PARTS_POSE_25.RIGHT_ANKLE),
                (BODY_PARTS_POSE_25.LEFT_HIP, BODY_PARTS_POSE_25.LEFT_KNEE),
                (BODY_PARTS_POSE_25.LEFT_KNEE, BODY_PARTS_POSE_25.LEFT_ANKLE),
                (BODY_PARTS_POSE_25.RIGHT_SHOULDER, BODY_PARTS_POSE_25.LEFT_SHOULDER),
                (BODY_PARTS_POSE_25.RIGHT_HIP, BODY_PARTS_POSE_25.LEFT_HIP),
                (BODY_PARTS_POSE_25.NOSE, BODY_PARTS_POSE_25.RIGHT_EYE),
                (BODY_PARTS_POSE_25.RIGHT_EYE, BODY_PARTS_POSE_25.RIGHT_EAR),
                (BODY_PARTS_POSE_25.NOSE, BODY_PARTS_POSE_25.LEFT_EYE),
                (BODY_PARTS_POSE_25.LEFT_EYE, BODY_PARTS_POSE_25.LEFT_EAR),
                (BODY_PARTS_POSE_25.LEFT_ANKLE, BODY_PARTS_POSE_25.LEFT_HEEL),
                (BODY_PARTS_POSE_25.RIGHT_ANKLE, BODY_PARTS_POSE_25.RIGHT_HEEL),
                (BODY_PARTS_POSE_25.LEFT_ANKLE, BODY_PARTS_POSE_25.LEFT_FOOT),
                (BODY_PARTS_POSE_25.RIGHT_ANKLE, BODY_PARTS_POSE_25.RIGHT_FOOT),
                (BODY_PARTS_POSE_25.RIGHT_FOOT, BODY_PARTS_POSE_25.RIGHT_TOE), #NOTE
                (BODY_PARTS_POSE_25.LEFT_FOOT, BODY_PARTS_POSE_25.LEFT_TOE), #NOTE
                (BODY_PARTS_POSE_25.RIGHT_ANKLE, BODY_PARTS_POSE_25.RIGHT_TOE), #NOTE
                (BODY_PARTS_POSE_25.LEFT_ANKLE, BODY_PARTS_POSE_25.LEFT_TOE) #NOTE
]

def convert_25_from_34(parts_34):
    parts_25 = np.zeros((25, 4))
    parts_25[BODY_PARTS_POSE_25.NOSE.value] = parts_34[BODY_PARTS_POSE_34.NOSE.value]
    parts_25[BODY_PARTS_POSE_25.NECK.value] = parts_34[BODY_PARTS_POSE_34.NECK.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_SHOULDER.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_SHOULDER.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_ELBOW.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_ELBOW.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_WRIST.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_HAND.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_SHOULDER.value] = parts_34[BODY_PARTS_POSE_34.LEFT_SHOULDER.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_ELBOW.value] = parts_34[BODY_PARTS_POSE_34.LEFT_ELBOW.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_WRIST.value] = parts_34[BODY_PARTS_POSE_34.LEFT_HAND.value]
    parts_25[BODY_PARTS_POSE_25.MID_HIP.value] = (parts_34[BODY_PARTS_POSE_34.RIGHT_HIP.value] + parts_34[BODY_PARTS_POSE_34.LEFT_HIP.value])/2
    parts_25[BODY_PARTS_POSE_25.RIGHT_HIP.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_HIP.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_KNEE.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_KNEE.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_ANKLE.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_ANKLE.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_HIP.value] = parts_34[BODY_PARTS_POSE_34.LEFT_HIP.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_KNEE.value] = parts_34[BODY_PARTS_POSE_34.LEFT_KNEE.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_ANKLE.value] = parts_34[BODY_PARTS_POSE_34.LEFT_ANKLE.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_EYE.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_EYE.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_EYE.value] = parts_34[BODY_PARTS_POSE_34.LEFT_EYE.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_EAR.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_EAR.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_EAR.value] = parts_34[BODY_PARTS_POSE_34.LEFT_EAR.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_FOOT.value] = parts_34[BODY_PARTS_POSE_34.LEFT_FOOT.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_TOE.value] = parts_34[BODY_PARTS_POSE_34.LEFT_FOOT.value]
    parts_25[BODY_PARTS_POSE_25.LEFT_HEEL.value] = parts_34[BODY_PARTS_POSE_34.LEFT_HEEL.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_FOOT.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_FOOT.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_TOE.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_FOOT.value]
    parts_25[BODY_PARTS_POSE_25.RIGHT_HEEL.value] = parts_34[BODY_PARTS_POSE_34.RIGHT_HEEL.value]
    return parts_25

def get_keypoint_3d(keypoint, keypoint_confidence, width, height, depth_map, cx, cy, fx, fy):

    keypoint_3d = np.empty((len(keypoint), 4)) # (x, y, z, c)
    #print(keypoint_3d)

    idx = 0
    for kp_2d in keypoint:
        x_pixel = kp_2d[0] # pelvis-x
        y_pixel = kp_2d[1] # pelvis-y

        depth_value = 0.0
        cnt = 0
        for i in range(-2, 3):
            for j in range(-2, 3):
                if x_pixel + i > 0 and x_pixel + i < width and y_pixel + j > 0 and y_pixel + j < height:
                    (result, depth) = depth_map.get_value(x_pixel + i, y_pixel + j) # (result, m)
                    if result == sl.ERROR_CODE.SUCCESS:
                        depth_value += depth
                        cnt += 1
        if cnt > 0:
            depth_value = depth_value/cnt
        else:
            depth_value = 0.0

        x = float(x_pixel - cx) * float(depth_value) / fx # meter
        y = float(y_pixel - cy) * float(depth_value) / fy # meter
        z = float(depth_value) # meter

        #print("[{}], ({}, {}, {})".format(idx, x, y, z))

        if np.isnan(x) or np.isinf(x):
            x = 0.0
        if np.isnan(y) or np.isinf(y):
            y = 0.0
        if np.isnan(z) or np.isinf(z):
            z = 0.0

        keypoint_3d[idx][0] = -z
        keypoint_3d[idx][1] = x
        keypoint_3d[idx][2] = -y
        if x == 0.0 or y == 0.0 or z == 0.0:
            keypoint_3d[idx][3] = 0
        else:
            keypoint_3d[idx][3] = keypoint_confidence[idx]
        idx += 1

    return keypoint_3d

def smooth_3d_pose(frame_buffer_3d, keypoint_3d):
    avg_keypoint_3d = np.zeros((25, 4))
    frame_buffer_3d = np.roll(frame_buffer_3d, -1, axis=0)
    buffer_size = frame_buffer_3d.shape[0]
    frame_buffer_3d[buffer_size-1] = keypoint_3d

    for i in range(keypoint_3d.shape[0]):
        parts = frame_buffer_3d[:, i, :]
        xdata = parts[:, 0]
        ydata = parts[:, 1]
        zdata = parts[:, 2]
        cdata = parts[:, 3]

        if np.sum(cdata) < 0.01:
            break

        x_avg = np.average(xdata, weights=cdata * range(1, buffer_size+1))
        y_avg = np.average(ydata, weights=cdata)
        z_avg = np.average(zdata, weights=cdata)
        c_avg = np.average(cdata, weights=cdata)
        avg_keypoint_3d[i] = [x_avg, y_avg, z_avg, c_avg]

    return frame_buffer_3d, avg_keypoint_3d

def append_udp_data(data, i, id, keypoint_3d):
    data.append({})
    data[i]['id'] = id
    data[i]['keypoints3d'] = keypoint_3d
    return data

def append_json_data(data, i, id, keypoint_3d):
    data.append({})
    data[i]['id'] = id
    data[i]['keypoints3d'] = keypoint_3d.tolist()
    return data

def create_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")