# ================================================================================
# Redefinition of enumeration in ZED Camera.hpp for systme's expandibility
# url: https://www.stereolabs.com/developers/release/
# ================================================================================

import numpy as np
from enum import Enum

# Enumerate of 18 body parts same as openpose

class BODY_PARTS(Enum):
    NOSE = 0
    NECK = 1
    RIGHT_SHOULDER = 2
    RIGHT_ELBOW = 3
    RIGHT_WRIST = 4
    LEFT_SHOULDER = 5
    LEFT_ELBOW = 6
    LEFT_WRIST = 7
    RIGHT_HIP = 8
    RIGHT_KNEE = 9
    RIGHT_ANKLE = 10
    LEFT_HIP = 11
    LEFT_KNEE = 12
    LEFT_ANKLE = 13
    RIGHT_EYE = 14
    LEFT_EYE = 15
    RIGHT_EAR = 16
    LEFT_EAR = 17
    LAST = 18

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

# Connection between each body part
SKELETON_BONES = [ (BODY_PARTS.NOSE, BODY_PARTS.NECK),
                (BODY_PARTS.NECK, BODY_PARTS.RIGHT_SHOULDER),
                (BODY_PARTS.RIGHT_SHOULDER, BODY_PARTS.RIGHT_ELBOW),
                (BODY_PARTS.RIGHT_ELBOW, BODY_PARTS.RIGHT_WRIST),
                (BODY_PARTS.NECK, BODY_PARTS.LEFT_SHOULDER),
                (BODY_PARTS.LEFT_SHOULDER, BODY_PARTS.LEFT_ELBOW),
                (BODY_PARTS.LEFT_ELBOW, BODY_PARTS.LEFT_WRIST),
                (BODY_PARTS.RIGHT_HIP, BODY_PARTS.RIGHT_KNEE),
                (BODY_PARTS.RIGHT_KNEE, BODY_PARTS.RIGHT_ANKLE),
                (BODY_PARTS.LEFT_HIP, BODY_PARTS.LEFT_KNEE),
                (BODY_PARTS.LEFT_KNEE, BODY_PARTS.LEFT_ANKLE),
                (BODY_PARTS.RIGHT_SHOULDER, BODY_PARTS.LEFT_SHOULDER),
                (BODY_PARTS.RIGHT_HIP, BODY_PARTS.LEFT_HIP),
                (BODY_PARTS.NOSE, BODY_PARTS.RIGHT_EYE),
                (BODY_PARTS.RIGHT_EYE, BODY_PARTS.RIGHT_EAR),
                (BODY_PARTS.NOSE, BODY_PARTS.LEFT_EYE),
                (BODY_PARTS.LEFT_EYE, BODY_PARTS.LEFT_EAR) ]

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

BODY_BONES_POSE_34 = [
                (BODY_PARTS_POSE_34.PELVIS, BODY_PARTS_POSE_34.NAVAL_SPINE),
                (BODY_PARTS_POSE_34.NAVAL_SPINE, BODY_PARTS_POSE_34.CHEST_SPINE),
                (BODY_PARTS_POSE_34.CHEST_SPINE, BODY_PARTS_POSE_34.LEFT_CLAVICLE),
                (BODY_PARTS_POSE_34.LEFT_CLAVICLE, BODY_PARTS_POSE_34.LEFT_SHOULDER),
                (BODY_PARTS_POSE_34.LEFT_SHOULDER, BODY_PARTS_POSE_34.LEFT_ELBOW),
                (BODY_PARTS_POSE_34.LEFT_ELBOW, BODY_PARTS_POSE_34.LEFT_WRIST),
                (BODY_PARTS_POSE_34.LEFT_WRIST, BODY_PARTS_POSE_34.LEFT_HAND),
                (BODY_PARTS_POSE_34.LEFT_HAND, BODY_PARTS_POSE_34.LEFT_HANDTIP),
                (BODY_PARTS_POSE_34.LEFT_WRIST, BODY_PARTS_POSE_34.LEFT_THUMB),
                (BODY_PARTS_POSE_34.CHEST_SPINE, BODY_PARTS_POSE_34.RIGHT_CLAVICLE),
                (BODY_PARTS_POSE_34.RIGHT_CLAVICLE, BODY_PARTS_POSE_34.RIGHT_SHOULDER),
                (BODY_PARTS_POSE_34.RIGHT_SHOULDER, BODY_PARTS_POSE_34.RIGHT_ELBOW),
                (BODY_PARTS_POSE_34.RIGHT_ELBOW, BODY_PARTS_POSE_34.RIGHT_WRIST),
                (BODY_PARTS_POSE_34.RIGHT_WRIST, BODY_PARTS_POSE_34.RIGHT_HAND),
                (BODY_PARTS_POSE_34.RIGHT_HAND, BODY_PARTS_POSE_34.RIGHT_HANDTIP),
                (BODY_PARTS_POSE_34.RIGHT_WRIST, BODY_PARTS_POSE_34.RIGHT_THUMB),
                (BODY_PARTS_POSE_34.PELVIS, BODY_PARTS_POSE_34.LEFT_HIP),
                (BODY_PARTS_POSE_34.LEFT_HIP, BODY_PARTS_POSE_34.LEFT_KNEE),
                (BODY_PARTS_POSE_34.LEFT_KNEE, BODY_PARTS_POSE_34.LEFT_ANKLE),
                (BODY_PARTS_POSE_34.LEFT_ANKLE, BODY_PARTS_POSE_34.LEFT_FOOT),
                (BODY_PARTS_POSE_34.PELVIS, BODY_PARTS_POSE_34.RIGHT_HIP),
                (BODY_PARTS_POSE_34.RIGHT_HIP, BODY_PARTS_POSE_34.RIGHT_KNEE),
                (BODY_PARTS_POSE_34.RIGHT_KNEE, BODY_PARTS_POSE_34.RIGHT_ANKLE),
                (BODY_PARTS_POSE_34.RIGHT_ANKLE, BODY_PARTS_POSE_34.RIGHT_FOOT),
                (BODY_PARTS_POSE_34.CHEST_SPINE, BODY_PARTS_POSE_34.NECK),
                (BODY_PARTS_POSE_34.NECK, BODY_PARTS_POSE_34.HEAD),
                (BODY_PARTS_POSE_34.HEAD, BODY_PARTS_POSE_34.NOSE),
                (BODY_PARTS_POSE_34.NOSE, BODY_PARTS_POSE_34.LEFT_EYE),
                (BODY_PARTS_POSE_34.LEFT_EYE, BODY_PARTS_POSE_34.LEFT_EAR),
                (BODY_PARTS_POSE_34.NOSE, BODY_PARTS_POSE_34.RIGHT_EYE),
                (BODY_PARTS_POSE_34.RIGHT_EYE, BODY_PARTS_POSE_34.RIGHT_EAR),
                (BODY_PARTS_POSE_34.LEFT_ANKLE, BODY_PARTS_POSE_34.LEFT_HEEL),
                (BODY_PARTS_POSE_34.RIGHT_ANKLE, BODY_PARTS_POSE_34.RIGHT_HEEL),
                (BODY_PARTS_POSE_34.LEFT_HEEL, BODY_PARTS_POSE_34.LEFT_FOOT),
                (BODY_PARTS_POSE_34.RIGHT_HEEL, BODY_PARTS_POSE_34.RIGHT_FOOT)]

ID_COLORS = [(232, 176,59)
            ,(175, 208,25)
            ,(102, 205,105)
            ,(185, 0,255)
            ,(99, 107,252)]

def generate_color_id_u(idx):
    arr = []
    if(idx < 0):
        arr = [236,184,36,255]
    else:
        color_idx = idx % 5
        arr = [ID_COLORS[color_idx][0], ID_COLORS[color_idx][1], ID_COLORS[color_idx][2], 255]
    return arr

def convert_25_from_34(parts_34):
    parts_25 = np.zeros((25, 3))
    parts_25[BODY_PARTS_POSE_25.NOSE] = parts_34[BODY_PARTS_POSE_34.NOSE]
    parts_25[BODY_PARTS_POSE_25.NECK] = parts_34[BODY_PARTS_POSE_34.NECK]
    parts_25[BODY_PARTS_POSE_25.RIGHT_SHOULDER] = parts_34[BODY_PARTS_POSE_34.RIGHT_SHOULDER]
    parts_25[BODY_PARTS_POSE_25.RIGHT_ELBOW] = parts_34[BODY_PARTS_POSE_34.RIGHT_ELBOW]
    parts_25[BODY_PARTS_POSE_25.RIGHT_WRIST] = parts_34[BODY_PARTS_POSE_34.RIGHT_WRIST]
    parts_25[BODY_PARTS_POSE_25.LEFT_SHOULDER] = parts_34[BODY_PARTS_POSE_34.LEFT_SHOULDER]
    parts_25[BODY_PARTS_POSE_25.LEFT_ELBOW] = parts_34[BODY_PARTS_POSE_34.LEFT_ELBOW]
    parts_25[BODY_PARTS_POSE_25.LEFT_WRIST] = parts_34[BODY_PARTS_POSE_34.LEFT_WRIST]
    #parts_25[BODY_PARTS_POSE_25.MID_HIP] = parts_34[BODY_PARTS_POSE_34.MID_HIP]
    parts_25[BODY_PARTS_POSE_25.RIGHT_HIP] = parts_34[BODY_PARTS_POSE_34.RIGHT_HIP]
    parts_25[BODY_PARTS_POSE_25.RIGHT_KNEE] = parts_34[BODY_PARTS_POSE_34.RIGHT_KNEE]
    parts_25[BODY_PARTS_POSE_25.RIGHT_ANKLE] = parts_34[BODY_PARTS_POSE_34.RIGHT_ANKLE]
    parts_25[BODY_PARTS_POSE_25.LEFT_HIP] = parts_34[BODY_PARTS_POSE_34.LEFT_HIP]
    parts_25[BODY_PARTS_POSE_25.LEFT_KNEE] = parts_34[BODY_PARTS_POSE_34.LEFT_KNEE]
    parts_25[BODY_PARTS_POSE_25.LEFT_ANKLE] = parts_34[BODY_PARTS_POSE_34.LEFT_ANKLE]
    parts_25[BODY_PARTS_POSE_25.RIGHT_EYE] = parts_34[BODY_PARTS_POSE_34.RIGHT_EYE]
    parts_25[BODY_PARTS_POSE_25.LEFT_EYE] = parts_34[BODY_PARTS_POSE_34.LEFT_EYE]
    parts_25[BODY_PARTS_POSE_25.RIGHT_EAR] = parts_34[BODY_PARTS_POSE_34.RIGHT_EAR]
    parts_25[BODY_PARTS_POSE_25.LEFT_EAR] = parts_34[BODY_PARTS_POSE_34.LEFT_EAR]
    parts_25[BODY_PARTS_POSE_25.LEFT_FOOT] = parts_34[BODY_PARTS_POSE_34.LEFT_FOOT]
    #parts_25[BODY_PARTS_POSE_25.LEFT_TOE] = parts_34[BODY_PARTS_POSE_34.LEFT_TOE]
    parts_25[BODY_PARTS_POSE_25.LEFT_HEEL] = parts_34[BODY_PARTS_POSE_34.LEFT_HEEL]
    parts_25[BODY_PARTS_POSE_25.RIGHT_FOOT] = parts_34[BODY_PARTS_POSE_34.RIGHT_FOOT]
    #parts_25[BODY_PARTS_POSE_25.RIGHT_TOE] = parts_34[BODY_PARTS_POSE_34.RIGHT_TOE]
    parts_25[BODY_PARTS_POSE_25.RIGHT_HEEL] = parts_34[BODY_PARTS_POSE_34.RIGHT_HEEL]
    return parts_25.tolist()
