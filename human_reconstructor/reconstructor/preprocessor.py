import numpy as np
import copy

def smooth_2d_pose(frame_buffer_2d, keypoints2d):
    # Smooth estimated 2D pose
    # - Store 2D pose data to frame_buffer
    # - Apply average filter by using weight, which is confidence
    # param1: frame buffer is a buffer to store 2D poses
    # param2: keypoints2d is 2D pose from current frame
    # return: ret is averaged 2D pose
    avg_keypoints2d = np.zeros((25, 3))
    # moving average
    frame_buffer_2d = np.roll(frame_buffer_2d, -1, axis=0)
    buffer_size = frame_buffer_2d.shape[0]
    frame_buffer_2d[buffer_size-1] = keypoints2d

    for i in range(keypoints2d.shape[0]):
        parts = frame_buffer_2d[:, i, :]
        xdata = parts[:, 0]
        ydata = parts[:, 1]
        cdata = parts[:, 2]

        if np.sum(cdata) < 0.01:
            break

        x_avg = np.average(xdata, weights=cdata)
        y_avg = np.average(ydata, weights=cdata)
        c_avg = np.average(cdata, weights=cdata)
        avg_keypoints2d[i] = [x_avg, y_avg, c_avg]

    return frame_buffer_2d, avg_keypoints2d

def smooth_position(frame_buffer_pos, position):
    position = np.array(position)
    avg_position = np.zeros(position.shape)
    # moving average
    frame_buffer_pos = np.roll(frame_buffer_pos, -1, axis=0)
    buffer_size = frame_buffer_pos.shape[0]
    frame_buffer_pos[buffer_size-1] = position

    for i in range(position.shape[0]):
        parts = frame_buffer_pos[:, i, :]
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
        avg_position[i] = [x_avg, y_avg, z_avg, c_avg]

    return frame_buffer_pos, avg_position

def is_bbox_overlapped(bbox1, bbox2):
    if bbox1[0] < bbox2[0] and bbox2[0] < bbox1[2] and bbox1[1] < bbox2[1] and bbox2[1] < bbox1[3]:
        return True
    elif bbox1[0] < bbox2[2] and bbox2[2] < bbox1[2] and bbox1[1] < bbox2[3] and bbox2[3] < bbox1[3]:
        return True
    else:
        return False

def reverse_skeleton(keypoints3d):
    swap_skeleton(2, 5, keypoints3d)
    swap_skeleton(3, 6, keypoints3d)
    swap_skeleton(4, 7, keypoints3d)
    swap_skeleton(9, 12, keypoints3d)
    swap_skeleton(10, 13, keypoints3d)
    swap_skeleton(11, 14, keypoints3d)
    swap_skeleton(21, 24, keypoints3d)
    swap_skeleton(22, 19, keypoints3d)
    swap_skeleton(23, 20, keypoints3d)
    swap_skeleton(15, 16, keypoints3d)
    swap_skeleton(17, 18, keypoints3d)
    return keypoints3d

def swap_skeleton(id1, id2, keypoints3d):
    tmp = copy.deepcopy(keypoints3d[id1, :])
    keypoints3d[id1, :] = keypoints3d[id2, :]
    keypoints3d[id2, :] = tmp
    return keypoints3d
