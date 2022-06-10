import numpy as np

def get_keypoint_3d(keypoint, confidence, depth_map, cx, cy, fx, fy):

    keypoint_3d = np.empty((len(keypoint), 4)) # (x, y, z, c)
    print(keypoint_3d)

    idx = 0
    for kp_2d in keypoint:
        x_pixel = kp_2d[0] # pelvis-x
        y_pixel = kp_2d[1] # pelvis-y
        depth_value = depth_map.get_value(x_pixel,y_pixel)[1] # (result, m)

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