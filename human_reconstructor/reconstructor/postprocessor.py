import numpy as np

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

        x_avg = np.average(xdata, weights=cdata * range(1, buffer_size+1))
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