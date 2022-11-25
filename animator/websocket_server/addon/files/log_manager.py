import numpy as np
import json

class LogManager:
    def __init__(self, path):
        self.__path = path

    def read_logging_file(self, framenum):
        file_path = self.__path + str(framenum).zfill(6) + ".json"
        print(file_path)
        ret = None
        with open(file_path, "r") as outfile:
            data = json.load(outfile)
            annots = np.array(data["annots"])
            for id in range(annots.shape[0]):
                keypoint = np.array(data["annots"][id]["keypoints3d"])
                for i in range(keypoint.shape[0]):
                    keypoint[i][0] = round(keypoint[i][0], 5)
                    keypoint[i][1] = round(keypoint[i][1], 5)
                    keypoint[i][2] = round(keypoint[i][2], 5)
                data["annots"][id]["keypoints3d"] = keypoint.tolist()
            ret = str(data)
            print(data)

        return ret