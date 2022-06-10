import numpy as np
import pyzed.sl as sl

def get_keypoint_3d(keypoint, confidence, width, height, depth_map, cx, cy, fx, fy):

    keypoint_3d = np.empty((len(keypoint), 4)) # (x, y, z, c)
    print(keypoint_3d)

    idx = 0
    for kp_2d in keypoint:
        x_pixel = kp_2d[0] # pelvis-x
        y_pixel = kp_2d[1] # pelvis-y

        depth_value = 0
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
            depth_value = 0

        x = float(x_pixel - cx) * float(depth_value) / fx # meter
        y = float(y_pixel - cy) * float(depth_value) / fy # meter
        z = float(depth_value) # meter

        keypoint_3d[idx][0] = x
        keypoint_3d[idx][1] = y
        keypoint_3d[idx][2] = z
        keypoint_3d[idx][3] = confidence
        idx += 1

    data = []
    data.append({})
    data[0]['id'] = 0
    data[0]['keypoints3d'] = keypoint_3d

    return data