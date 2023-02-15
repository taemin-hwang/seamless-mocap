import numpy as np
import utils
import json
import os
import viewer

class calibrator:
    def __init__(self, cam_num):
        self.__ids = [utils.BODY_PARTS_POSE_25.NOSE.value,
                      utils.BODY_PARTS_POSE_25.NECK.value,
                      utils.BODY_PARTS_POSE_25.RIGHT_SHOULDER.value,
                      utils.BODY_PARTS_POSE_25.LEFT_SHOULDER.value,
                      utils.BODY_PARTS_POSE_25.MID_HIP.value,
                      utils.BODY_PARTS_POSE_25.RIGHT_KNEE.value,
                      utils.BODY_PARTS_POSE_25.LEFT_KNEE.value,
                      utils.BODY_PARTS_POSE_25.RIGHT_ANKLE.value,
                      utils.BODY_PARTS_POSE_25.LEFT_ANKLE.value,]
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
                    transformation_matrix[from_][to_] = self.__get_transformation_matrix(matched_points_list[from_], matched_points_list[to_])

        print("T12 : ", transformation_matrix[0][1])
        print("T21 : ", transformation_matrix[1][0])
        self.__save_transformation_matrix(transformation_matrix)

        self.__show_results(transformation_matrix)

    def __show_results(self, transformation_matrix):
        from mpl_toolkits import mplot3d
        import matplotlib.pyplot as plt

        for i in range(self.__num):
            fig = plt.figure()
            plt.tight_layout()
            skeletons = self.__get_keypoints(i+1)
            # ax = fig.add_subplot(2, 2, i+1, projection='3d')
            ax = plt.axes(projection='3d')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            plt.xlim(-2, 1)
            plt.ylim(-2, 1)
            ax.set_zlim(0, 1.5)
            viewer.draw_3d_skeleton(ax, skeletons)
            plt.show()

        for i in range(self.__num):
            transform = transformation_matrix[i][0]
            skeletons = self.__get_keypoints(i+1)
            transformed_keypoints = self.__get_transformed_keypoints(skeletons, transform)
            fig = plt.figure()
            plt.tight_layout()
            # ax = fig.add_subplot(2, 2, i+1, projection='3d')
            ax = plt.axes(projection='3d')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            plt.xlim(-2, 1)
            plt.ylim(-2, 1)
            ax.set_zlim(0, 1.5)
            viewer.draw_3d_skeleton(ax, transformed_keypoints)
            plt.show()

    def __get_transformed_keypoints(self, keypoints, transform):
        keypoints = np.array(keypoints)
        transform = np.array(transform)
        c = []
        for kp in keypoints:
            k = (transform[:-1, :-1]@kp[:3] + transform[:-1, -1]).tolist()
            k.extend([kp[3]])
            c.append(k)
        c = np.array(c)
        return c

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

    def __get_transformation_matrix(self, a, b):
        a_arr = np.stack([a[i][:3] for i in range(len(self.__ids))], axis=1)
        b_arr = np.stack([b[i][:3] for i in range(len(self.__ids))], axis=1)

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

    def __save_transformation_matrix(self, transformation_matrix):
        data = {}
        for _from in range(self.__num):
            skeletons = self.__select_matched_points(self.__get_keypoints(_from+1))
            print(skeletons)
            data["C{}".format(_from+1)] = [np.average(skeletons[:, 0]), np.average(skeletons[:, 1]), np.average(skeletons[:, 2]), np.average(skeletons[:, 3])]
            for _to in range(self.__num):
                data["T{}{}".format(_from+1, _to+1)] = transformation_matrix[_from][_to].tolist()

        with open(os.path.join(self.__out, "transformation.json"), "w") as f:
            json.dump(data, f)
