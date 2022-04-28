import numpy as np
import json
import socket
from utils import converter

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class JsonWriter:
    def write_2d_pose_skeleton(self, path, name, pose_results, width, height):
        if not pose_results.pose_landmarks:
            return

        keypoints33 = np.empty((33, 3))
        for idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
            keypoints33[idx] = [landmark.x * width, landmark.y * height, landmark.visibility]

        keypoints25 = converter.convert_25_from_33(keypoints33)

        data = []
        skeletons = []
        data.append({})
        data[0]['id'] = 0
        data[0]['keypoints2d'] = keypoints25
        json_data = json.dumps(data, cls=NumpyEncoder)
        #print(json_data)

        filename = path + str(name).zfill(6) + '.json'
        with open(filename, "w") as json_file:
            json_file.write(json_data)