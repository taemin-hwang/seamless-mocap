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

ID_COLORS = [(143, 126, 19)
            ,(84, 204, 255)
            ,(118, 87, 255)
            ,(76, 24, 56)
            ,(167, 227, 77)
            ,(59, 176, 232)
            ,(175, 208, 25)
            ,(102, 205, 105)
            ,(185, 0, 255)
            ,(99, 107, 252)
            ,(1, 146, 103)
            ,(0, 200, 151)
            ,(255, 211, 101)
            ,(83, 62, 133)
            ,(72, 143, 177)
            ,(79, 211, 196)
            ,(193, 248, 207)
            ,(25, 25, 25)
            ,(45, 66, 99)
            ,(200, 75, 49)
            ,(236, 219, 186)
            ]

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

import cv2
def draw_grid(img, line_color=(125, 125, 125), thickness=1, type_= cv2.LINE_AA, pxstep=50):
    '''(ndarray, 3-tuple, int, int) -> void
    draw gridlines on img
    line_color:
        BGR representation of colour
    thickness:
        line thickness
    type:
        8, 4 or cv2.LINE_AA
    pxstep:
        grid line frequency in pixels
    '''
    x = pxstep
    y = pxstep
    while x < img.shape[1]:
        cv2.line(img, (x, 0), (x, img.shape[0]), color=line_color, lineType=type_, thickness=thickness)
        x += pxstep

    while y < img.shape[0]:
        cv2.line(img, (0, y), (img.shape[1], y), color=line_color, lineType=type_, thickness=thickness)
        y += pxstep