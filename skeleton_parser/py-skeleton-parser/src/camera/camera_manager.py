import numpy as np

from src.camera import camera_interface, camera_config
from src.camera import zed_manager, realsense_manager
from src.visualizer import utils

class CameraManager(camera_interface.CameraInterface):
    def __init__(self, args):
        self.__args = args
        self.__camera_manager = None
        self.__num_sample = 100

        if self.__args.camera == "zed":
            self.__camera_manager = zed_manager.ZedManager(self.__args)
        elif self.__args.camera == "realsense":
            try:
                import pyrealsense2 as rs
                self.__camera_manager = realsense_manager.RealsenseManager(self.__args)
            except ImportError:
                print("Cannot import pyrealsense2")

    def initialize(self):
        self.__camera_manager.initialize()

    def get_image(self):
        return self.__camera_manager.get_image()

    def get_depth(self, x, y):
        return self.__camera_manager.get_depth()

    def get_depth_from_keypoint(self, keypoint):
        return self.__camera_manager.get_depth_from_keypoint(keypoint)

    def get_keypoint(self, image):
        ret = None
        if self.__args.camera == "zed":
            ret = self.__camera_manager.get_keypoint()
        return ret

    def get_color_from_keypoint(self, image, keypoints):
        if keypoints == None:
            return {}

        data = {}
        data['annots'] = []
        pos_idx = [0, 1, 2, 5, 8, 11] # Nose, Neck, R-Shoulder, L-Shoulder, R-Pelvis, L-Pelvis
        bodies = keypoints['annots']

        for body in bodies:
            annot = {}
            annot['personID'] = body['personID']
            cloth_color = self.__get_color(image, body['keypoints'])
            annot['cloth'] = [cloth_color[0], cloth_color[1]]
            data['annots'].append(annot)

        return data

    def __get_color(self, image, keypoint):
        cloth_color = np.empty((2, 3))
        upper_rgb = self.__get_upper_rgb(image, keypoint, self.__num_sample)
        lower_rgb = self.__get_lower_rgb(image, keypoint, self.__num_sample)

        upper_key_rgb, num_upper = self.__get_keyrgb(upper_rgb)
        lower_key_rgb, num_lower = self.__get_keyrgb(lower_rgb)

        if np.array_equal(lower_key_rgb, np.array([255, 0, 0])):
            lower_key_rgb = upper_key_rgb
        elif np.array_equal(upper_key_rgb, np.array([255, 0, 0])):
            upper_key_rgb = lower_key_rgb

        cloth_color[0] = upper_key_rgb
        cloth_color[1] = lower_key_rgb

        return cloth_color.tolist()

    def __get_upper_rgb(self, image, person_keypoint, num_sample):
        person_keypoint = np.array(person_keypoint)
        left_shoulder = person_keypoint[utils.BODY_PARTS.LEFT_SHOULDER.value]
        left_hip = person_keypoint[utils.BODY_PARTS.LEFT_HIP.value]
        right_shoulder = person_keypoint[utils.BODY_PARTS.RIGHT_SHOULDER.value]
        right_hip = person_keypoint[utils.BODY_PARTS.RIGHT_HIP.value]

        left_mid = (left_shoulder + left_hip) / 2
        right_mid = (right_shoulder + right_hip) / 2

        upper1 = self.__get_bone_rgb(image, left_shoulder, right_shoulder, num_sample)
        upper2 = self.__get_bone_rgb(image, left_shoulder, left_mid, num_sample)
        upper3 = self.__get_bone_rgb(image, left_shoulder, right_shoulder, num_sample)
        upper4 = self.__get_bone_rgb(image, right_mid, right_shoulder, num_sample)

        upper = np.vstack((upper1, upper2, upper3, upper4))
        return upper

    def __get_lower_rgb(self, image, person_keypoint, num_sample):
        person_keypoint = np.array(person_keypoint)
        left_hip = person_keypoint[utils.BODY_PARTS.LEFT_HIP.value]
        left_knee = person_keypoint[utils.BODY_PARTS.LEFT_KNEE.value]
        left_ankle = person_keypoint[utils.BODY_PARTS.LEFT_ANKLE.value]
        right_hip = person_keypoint[utils.BODY_PARTS.RIGHT_HIP.value]
        right_knee = person_keypoint[utils.BODY_PARTS.RIGHT_KNEE.value]
        right_ankle = person_keypoint[utils.BODY_PARTS.RIGHT_ANKLE.value]

        lower1 = self.__get_bone_rgb(image, left_hip, left_knee, num_sample)
        lower2 = self.__get_bone_rgb(image, left_knee, left_ankle, num_sample)
        lower3 = self.__get_bone_rgb(image, right_hip, right_knee, num_sample)
        lower4 = self.__get_bone_rgb(image, right_knee, right_ankle, num_sample)

        lower = np.vstack((lower1, lower2, lower3, lower4))
        return lower

    def __get_bone_rgb(self, image, part1, part2, num_sample):
        # print(image.shape)
        rgb = np.zeros((num_sample, 3))

        x_diff = (part2[0]-part1[0])/num_sample
        x_iteration = []
        for i in range(num_sample):
            if i == 0:
                x_iteration.append(part1[0] + x_diff)
            else:
                x_iteration.append(x_iteration[i-1] + x_diff)

        y_diff = (part2[1]-part1[1])/num_sample
        y_iteration = []
        for i in range(num_sample):
            if i == 0:
                y_iteration.append(part1[1] + y_diff)
            else:
                y_iteration.append(y_iteration[i-1] + y_diff)

        for i in range(num_sample):
            x = int(x_iteration[i])
            y = int(y_iteration[i])

            if x < 0 or x >= 1920 or y < 0 or y >= 1080:
                #print("Cannot exceed camera resolution : ({}, {})".format(x, y))
                rgb[i] = np.array([255, 0, 0])
            else:
                rgb[i] = image[y][x][:3] # BGRA

        return rgb

    def __get_keyrgb(self, rgb):
        max_rgb = np.empty(3)
        max_num = np.zeros(3)

        num_r = np.zeros(256)
        num_g = np.zeros(256)
        num_b = np.zeros(256)

        for i in range(rgb.shape[0]):
            r = int(rgb[i][0] / 10) * 10
            g = int(rgb[i][1] / 10) * 10
            b = int(rgb[i][2] / 10) * 10

            num_r[r] += 1
            num_g[g] += 1
            num_b[b] += 1

        step = 10
        for i in range(256):
            if max_num[0] < num_r[i]:
                max_num[0] = num_r[i]
                max_rgb[0] = i

            if max_num[1] < num_g[i]:
                max_num[1] = num_g[i]
                max_rgb[1] = i

            if max_num[2] < num_b[i]:
                max_num[2] = num_b[i]
                max_rgb[2] = i

        num = np.vstack((num_r, num_g, num_b))
        return max_rgb, num
