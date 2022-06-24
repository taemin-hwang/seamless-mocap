import numpy as np
import utils
import json
import os

class calibrator:
    def __init__(self, cam_num):
        self.__ids = [utils.BODY_PARTS_POSE_25.NOSE.value,
                      utils.BODY_PARTS_POSE_25.NECK.value,
                      utils.BODY_PARTS_POSE_25.RIGHT_SHOULDER.value,
                      utils.BODY_PARTS_POSE_25.LEFT_SHOULDER.value]
        self.__num = cam_num
        pass

    def initialize(self, args, path):
        self.__args = args
        self.__path = path
        self.__out = "./out"
        utils.create_directory(self.__out)

    def run(self):
        matched_points_list = np.empty((self.__num, len(self.__ids), 4))
        for i in range(self.__num):
            cam_id = i
            matched_points = self.__select_matched_points(self.__get_keypoints(cam_id+1))
            matched_points_list[i] = matched_points

        transformation_matrix = np.empty((self.__num, self.__num, 4, 4))
        for from_ in range(self.__num):
            for to_ in range(self.__num):
                if from_ == to_:
                    transformation_matrix[from_][to_] = np.identity(4)
                else:
                    transformation_matrix[from_][to_] = self.__get_transformation_matrix_from_b(matched_points_list[from_], matched_points_list[to_])

        print(transformation_matrix)

    def __get_keypoints(self, cam_id):
        keypoints = []
        keyword = 'cam' + str(cam_id) + '_'
        for fname in os.listdir(self.__path):
            if keyword in fname:
                print(fname, "has the keyword")
                with open(self.__path + fname, "r") as json_file:
                    json_data = json.load(json_file)
                    keypoints = np.array(json_data[0]['keypoints3d'])
                break
        return keypoints

    def __select_matched_points(self, keypoints):
        matched_points = np.empty((len(self.__ids), 4))
        i = 0
        for id in self.__ids:
            matched_points[i] = keypoints[id]
            if matched_points[i, 3] < 0.00001:
                print('[ERROR] low confidence {} of {}'.format(matched_points[i, 3], id))
            i += 1
        return matched_points

    def __get_transformation_matrix_from_b(self, b, a):
        a_arr = np.stack([a[0][:3], a[1][:3], a[2][:3], a[3][:3]], axis=1)
        b_arr = np.stack([b[0][:3], b[1][:3], b[2][:3], b[3][:3]], axis=1)

        a_arr = np.concatenate([a_arr, np.ones_like(a_arr[:1])], axis=0)
        b_arr = np.concatenate([b_arr, np.ones_like(b_arr[:1])], axis=0)

        # make equation (a @ x = b)
        n = a_arr.shape[1]
        a_mat = np.zeros((3*n, 12), dtype=a_arr.dtype)
        b_mat = np.zeros(3*n, dtype=a_arr.dtype)

        a_mat[:n, 0] = a_arr[0]
        a_mat[:n, 1] = a_arr[1]
        a_mat[:n, 2] = a_arr[2]
        a_mat[:n, 3] = a_arr[3]
        b_mat[:n] = b_arr[0]

        a_mat[n:2 * n, 4] = a_arr[0]
        a_mat[n:2 * n, 5] = a_arr[1]
        a_mat[n:2 * n, 6] = a_arr[2]
        a_mat[n:2 * n, 7] = a_arr[3]
        b_mat[n:2 * n] = b_arr[1]
        a_mat[2 * n:, 8] = a_arr[0]
        a_mat[2 * n:, 9] = a_arr[1]
        a_mat[2 * n:, 10] = a_arr[2]
        a_mat[2 * n:, 11] = a_arr[3]
        b_mat[2 * n:] = b_arr[2]
        # Least-squares solution to equations
        x = np.linalg.pinv(a_mat) @ b_mat
        # Reshape into affine transformation matrix
        m2 = np.concatenate([x.reshape(3, 4), [[0.0, 0.0, 0.0, 1.0]]], axis=0)
        return m2