import numpy as np
import copy
from visualizer import utils

FORWARD_KINEMATICS = {
    utils.BODY_PARTS_POSE_25.MID_HIP.value: [utils.BODY_PARTS_POSE_25.NECK.value, utils.BODY_PARTS_POSE_25.RIGHT_HIP.value, utils.BODY_PARTS_POSE_25.LEFT_HIP.value],
    utils.BODY_PARTS_POSE_25.NECK.value: [utils.BODY_PARTS_POSE_25.NOSE.value, utils.BODY_PARTS_POSE_25.RIGHT_SHOULDER.value, utils.BODY_PARTS_POSE_25.LEFT_SHOULDER.value],
    utils.BODY_PARTS_POSE_25.NOSE.value: [utils.BODY_PARTS_POSE_25.RIGHT_EYE.value, utils.BODY_PARTS_POSE_25.LEFT_EYE.value],
    utils.BODY_PARTS_POSE_25.LEFT_EYE.value : [utils.BODY_PARTS_POSE_25.LEFT_EAR.value],
    utils.BODY_PARTS_POSE_25.RIGHT_EYE.value : [utils.BODY_PARTS_POSE_25.RIGHT_EAR.value],
    utils.BODY_PARTS_POSE_25.RIGHT_SHOULDER.value : [utils.BODY_PARTS_POSE_25.RIGHT_ELBOW.value],
    utils.BODY_PARTS_POSE_25.RIGHT_ELBOW.value : [utils.BODY_PARTS_POSE_25.RIGHT_WRIST.value],
    utils.BODY_PARTS_POSE_25.LEFT_SHOULDER.value : [utils.BODY_PARTS_POSE_25.LEFT_ELBOW.value],
    utils.BODY_PARTS_POSE_25.LEFT_ELBOW.value : [utils.BODY_PARTS_POSE_25.LEFT_WRIST.value],
    utils.BODY_PARTS_POSE_25.RIGHT_HIP.value : [utils.BODY_PARTS_POSE_25.RIGHT_KNEE.value],
    utils.BODY_PARTS_POSE_25.RIGHT_KNEE.value : [utils.BODY_PARTS_POSE_25.RIGHT_ANKLE.value],
    utils.BODY_PARTS_POSE_25.RIGHT_ANKLE.value : [utils.BODY_PARTS_POSE_25.RIGHT_FOOT.value, utils.BODY_PARTS_POSE_25.RIGHT_HEEL.value],
    utils.BODY_PARTS_POSE_25.RIGHT_FOOT.value : [utils.BODY_PARTS_POSE_25.RIGHT_TOE.value],
    utils.BODY_PARTS_POSE_25.LEFT_HIP.value : [utils.BODY_PARTS_POSE_25.LEFT_KNEE.value],
    utils.BODY_PARTS_POSE_25.LEFT_KNEE.value : [utils.BODY_PARTS_POSE_25.LEFT_ANKLE.value],
    utils.BODY_PARTS_POSE_25.LEFT_ANKLE.value : [utils.BODY_PARTS_POSE_25.LEFT_FOOT.value, utils.BODY_PARTS_POSE_25.LEFT_HEEL.value],
    utils.BODY_PARTS_POSE_25.LEFT_FOOT.value : [utils.BODY_PARTS_POSE_25.LEFT_TOE.value]
}

SMALL_PARTS = [utils.BODY_PARTS_POSE_25.NOSE.value,
               utils.BODY_PARTS_POSE_25.RIGHT_EYE.value,
               utils.BODY_PARTS_POSE_25.LEFT_EYE.value,
               utils.BODY_PARTS_POSE_25.RIGHT_ANKLE.value,
               utils.BODY_PARTS_POSE_25.RIGHT_FOOT.value,
               utils.BODY_PARTS_POSE_25.LEFT_ANKLE.value,
               utils.BODY_PARTS_POSE_25.LEFT_FOOT.value]

MID_PARTS = [utils.BODY_PARTS_POSE_25.NECK.value,
               utils.BODY_PARTS_POSE_25.RIGHT_HIP.value,
               utils.BODY_PARTS_POSE_25.LEFT_HIP.value,
               utils.BODY_PARTS_POSE_25.RIGHT_ELBOW.value,
               utils.BODY_PARTS_POSE_25.RIGHT_ELBOW.value,
               utils.BODY_PARTS_POSE_25.RIGHT_KNEE.value,
               utils.BODY_PARTS_POSE_25.LEFT_KNEE.value]

def fix_wrong_3d_pose(keypoints3d):
    # param1: keypoints3d is 3D pose from current frame
    # return: ret is fixed 3D pose
    err_dist = fix_3d_pose_recursively(keypoints3d[:, :3], utils.BODY_PARTS_POSE_25.MID_HIP.value)
    mean_err_dist = err_dist/24
    return (mean_err_dist, keypoints3d)

def fix_3d_pose_recursively(keypoints3d, parents_part):
    if parents_part not in FORWARD_KINEMATICS:
        return 0

    connected_parts = FORWARD_KINEMATICS[parents_part]
    err_dist = 0
    for connected_part in connected_parts:
        dist = np.linalg.norm(keypoints3d[parents_part] - keypoints3d[connected_part])
        # print("{} -> {} : {}".format(parents_part, connected_part, dist))
        # TODO: update constant variable according to the human body size (+ rotation)
        if parents_part in SMALL_PARTS:
            if dist > 0.15:
                keypoints3d[connected_part] = keypoints3d[parents_part] + (keypoints3d[connected_part] - keypoints3d[parents_part])/dist*0.15
                err_dist += (dist - 0.15)
        elif parents_part in MID_PARTS:
            if dist > 0.5:
                keypoints3d[connected_part] = keypoints3d[parents_part] + (keypoints3d[connected_part] - keypoints3d[parents_part])/dist*0.5
                err_dist += (dist - 0.5)
        else:
            if dist > 1.0:
                keypoints3d[connected_part] = keypoints3d[parents_part] + (keypoints3d[connected_part] - keypoints3d[parents_part])/dist*1.0
                err_dist += (dist - 1.0)

        err_dist += fix_3d_pose_recursively(keypoints3d, connected_part)
    return err_dist

def smooth_3d_pose(frame_buffer_3d, keypoints3d):
    # Smooth estimated 3D pose
    # - Store 3D pose data to frame_buffer_3d
    # - Apply average filter by using weight, which is confidence
    # param1: frame buffer is a buffer to store 3D poses
    # param2: keypoints3d is 3D pose from current frame
    # return: ret is averaged 3D pose
    avg_keypoints3d = np.zeros((25, 4))
    # moving average
    frame_buffer_3d = np.roll(frame_buffer_3d, -1, axis=0)
    buffer_size = frame_buffer_3d.shape[0]
    frame_buffer_3d[buffer_size-1] = keypoints3d

    for i in range(keypoints3d.shape[0]):
        parts = frame_buffer_3d[:, i, :]
        xdata = parts[:, 0]
        ydata = parts[:, 1]
        zdata = parts[:, 2]
        cdata = parts[:, 3]

        if np.sum(cdata) < 0.01:
            break

        x_avg = np.average(xdata, weights=cdata)
        y_avg = np.average(ydata, weights=cdata)
        z_avg = np.average(zdata, weights=cdata)
        c_avg = np.average(cdata, weights=cdata)
        avg_keypoints3d[i] = [x_avg, y_avg, z_avg, c_avg]

    return frame_buffer_3d, avg_keypoints3d

def xyz_to_xzy(keypoints3d):
    tmp = keypoints3d[:, 0]
    keypoints3d[:, 0] = keypoints3d[:, 1]
    keypoints3d[:, 1] = tmp
    keypoints3d[:, 2] = -1*keypoints3d[:, 2]
    #ret[:, 2] += 1.1
    #ret[:, 3][ret[:, 3] < self.min_confidence] = 0
    return keypoints3d
