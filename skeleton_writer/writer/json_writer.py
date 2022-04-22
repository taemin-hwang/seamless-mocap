import numpy as np
import json
import socket

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class JsonWriter:
    def __init__(self, path="./etc"):
        self.path = path
        pass

    def write_2d_skeleton(self, skeletons, timestamp):
        data = []
        data.append({})
        data[0]['id'] = 0
        data[0]['timestamp'] = timestamp
        data[0]['keypoints2d'] = skeletons
        json_data = json.dumps(data, cls=NumpyEncoder)
