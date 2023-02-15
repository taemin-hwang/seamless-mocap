import cv2
import numpy as np
import pyzed.sl as sl
import utils

ID_COLORS = [(232, 176, 59)
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

# Slightly differs from sl.BODY_BONES in order to draw the spine
SKELETON_BONES = [ (sl.BODY_PARTS.NOSE, sl.BODY_PARTS.NECK),
                (sl.BODY_PARTS.NECK, sl.BODY_PARTS.RIGHT_SHOULDER),
                (sl.BODY_PARTS.RIGHT_SHOULDER, sl.BODY_PARTS.RIGHT_ELBOW),
                (sl.BODY_PARTS.RIGHT_ELBOW, sl.BODY_PARTS.RIGHT_WRIST),
                (sl.BODY_PARTS.NECK, sl.BODY_PARTS.LEFT_SHOULDER),
                (sl.BODY_PARTS.LEFT_SHOULDER, sl.BODY_PARTS.LEFT_ELBOW),
                (sl.BODY_PARTS.LEFT_ELBOW, sl.BODY_PARTS.LEFT_WRIST),
                (sl.BODY_PARTS.RIGHT_HIP, sl.BODY_PARTS.RIGHT_KNEE),
                (sl.BODY_PARTS.RIGHT_KNEE, sl.BODY_PARTS.RIGHT_ANKLE),
                (sl.BODY_PARTS.LEFT_HIP, sl.BODY_PARTS.LEFT_KNEE),
                (sl.BODY_PARTS.LEFT_KNEE, sl.BODY_PARTS.LEFT_ANKLE),
                (sl.BODY_PARTS.RIGHT_SHOULDER, sl.BODY_PARTS.LEFT_SHOULDER),
                (sl.BODY_PARTS.RIGHT_HIP, sl.BODY_PARTS.LEFT_HIP),
                (sl.BODY_PARTS.NOSE, sl.BODY_PARTS.RIGHT_EYE),
                (sl.BODY_PARTS.RIGHT_EYE, sl.BODY_PARTS.RIGHT_EAR),
                (sl.BODY_PARTS.NOSE, sl.BODY_PARTS.LEFT_EYE),
                (sl.BODY_PARTS.LEFT_EYE, sl.BODY_PARTS.LEFT_EAR) ]

def render_object(object_data, is_tracking_on):
    if is_tracking_on:
        return (object_data.tracking_state == sl.OBJECT_TRACKING_STATE.OK)
    else:
        return ((object_data.tracking_state == sl.OBJECT_TRACKING_STATE.OK) or (object_data.tracking_state == sl.OBJECT_TRACKING_STATE.OFF))


def generate_color_id_u(idx):
    arr = []
    if(idx < 0):
        arr = [236,184,36,255]
    else:
        color_idx = idx % 16
        arr = [ID_COLORS[color_idx][0], ID_COLORS[color_idx][1], ID_COLORS[color_idx][2], 255]
    return arr

#----------------------------------------------------------------------
#       2D VIEW
#----------------------------------------------------------------------
def cvt(pt, scale):
    '''
    Function that scales point coordinates
    '''
    out = [pt[0]*scale[0], pt[1]*scale[1]]
    return out

def render_2D(left_display, objects, is_tracking_on, body_format):
    '''
    Parameters
        left_display (np.array): numpy array containing image data
        objects (list[sl.ObjectData])
    '''
    overlay = left_display.copy()

    # Render skeleton joints and bones
    for obj in objects:
        if render_object(obj, is_tracking_on):
            if len(obj.keypoint_2d) > 0:
                color = generate_color_id_u(obj.id)
                # POSE_18
                if body_format == sl.BODY_FORMAT.POSE_18:
                    # Draw skeleton bones
                    for part in SKELETON_BONES:
                        kp_a = obj.keypoint_2d[part[0].value]
                        kp_b = obj.keypoint_2d[part[1].value]
                        # Check that the keypoints are inside the image
                        if(kp_a[0] < left_display.shape[1] and kp_a[1] < left_display.shape[0]
                        and kp_b[0] < left_display.shape[1] and kp_b[1] < left_display.shape[0]
                        and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                            cv2.line(overlay, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

                    # Get spine base coordinates to create backbone
                    left_hip = obj.keypoint_2d[sl.BODY_PARTS.LEFT_HIP.value]
                    right_hip = obj.keypoint_2d[sl.BODY_PARTS.RIGHT_HIP.value]
                    spine = (left_hip + right_hip) / 2
                    kp_spine = spine
                    kp_neck = obj.keypoint_2d[sl.BODY_PARTS.NECK.value]
                    # Check that the keypoints are inside the image
                    if(kp_spine[0] < left_display.shape[1] and kp_spine[1] < left_display.shape[0]
                    and kp_neck[0] < left_display.shape[1] and kp_neck[1] < left_display.shape[0]
                    and kp_spine[0] > 0 and kp_spine[1] > 0 and kp_neck[0] > 0 and kp_neck[1] > 0
                    and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                        cv2.line(overlay, (int(kp_spine[0]), int(kp_spine[1])), (int(kp_neck[0]), int(kp_neck[1])), color, 1, cv2.LINE_AA)

                    # Skeleton joints for spine
                    if(kp_spine[0] < left_display.shape[1] and kp_spine[1] < left_display.shape[0]
                    and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                        cv2.circle(left_display, (int(kp_spine[0]), int(kp_spine[1])), 3, color, -1)

                elif body_format == sl.BODY_FORMAT.POSE_34:
                    # Draw skeleton bones
                    for part in sl.BODY_BONES_POSE_34:
                        kp_a = obj.keypoint_2d[part[0].value]
                        kp_b = obj.keypoint_2d[part[1].value]
                        # Check that the keypoints are inside the image
                        if(kp_a[0] < left_display.shape[1] and kp_a[1] < left_display.shape[0]
                        and kp_b[0] < left_display.shape[1] and kp_b[1] < left_display.shape[0]
                        and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                            cv2.line(overlay, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

                # Skeleton joints
                for kp in obj.keypoint_2d:
                    cv_kp = kp
                    if(cv_kp[0] < left_display.shape[1] and cv_kp[1] < left_display.shape[0]):
                        cv2.circle(overlay, (int(cv_kp[0]), int(cv_kp[1])), 3, color, -1)

    return overlay
    #cv2.addWeighted(left_display, 0.9, overlay, 0.1, 0.0, left_display)


def draw_3d_skeleton(ax, skeletons):
    clr = generate_color_id_u(0)
    plt_clr = [clr[0]/255, clr[1]/255, clr[2]/255]

    for bone in utils.BODY_BONES_POSE_25:
        kp_1 = skeletons[bone[0].value]
        kp_2 = skeletons[bone[1].value]
        if(kp_1[3] > 0.2 and kp_2[3] > 0.2):
            ax.plot([kp_1[0], kp_2[0]], [kp_1[1], kp_2[1]], [kp_1[2], kp_2[2]], color=plt_clr)

    for part in utils.BODY_PARTS_POSE_25:
        if part.value < 25:
            kp = skeletons[part.value]
        if kp[3] > 0.2:
            circle_color = generate_color_id_u(part.value)
            plt_circle_clr = [circle_color[0]/255, circle_color[1]/255, circle_color[2]/255]
            ax.scatter(kp[0], kp[1], kp[2], color=plt_circle_clr)