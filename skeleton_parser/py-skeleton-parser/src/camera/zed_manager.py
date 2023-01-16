from src.camera import camera_interface, camera_config

import cv2
import sys
import pyzed.sl as sl
import numpy as np
import logging
import time

SKELETON_BONES = [  sl.BODY_PARTS.NOSE,
                    sl.BODY_PARTS.NECK,
                    sl.BODY_PARTS.RIGHT_SHOULDER,
                    sl.BODY_PARTS.RIGHT_ELBOW,
                    sl.BODY_PARTS.RIGHT_WRIST,
                    sl.BODY_PARTS.LEFT_SHOULDER,
                    sl.BODY_PARTS.LEFT_ELBOW,
                    sl.BODY_PARTS.LEFT_WRIST,
                    sl.BODY_PARTS.RIGHT_HIP,
                    sl.BODY_PARTS.RIGHT_KNEE,
                    sl.BODY_PARTS.RIGHT_ANKLE,
                    sl.BODY_PARTS.LEFT_HIP,
                    sl.BODY_PARTS.LEFT_KNEE,
                    sl.BODY_PARTS.LEFT_ANKLE,
                    sl.BODY_PARTS.RIGHT_EYE,
                    sl.BODY_PARTS.LEFT_EYE,
                    sl.BODY_PARTS.RIGHT_EAR,
                    sl.BODY_PARTS.LEFT_EAR ]

class ZedManager(camera_interface.CameraInterface):
    def __init__(self, args):
        self.__args = args
        self.__zed = sl.Camera()
        self.__image = sl.Mat()
        self.__depth_map = sl.Mat()
        self.__bodies = sl.Objects()
        self.__fps = 0.0

    def initialize(self):
        resolution = self.__args.resolution
        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        if resolution == "HD720":
            init_params.camera_resolution = sl.RESOLUTION.HD720
        elif resolution == "HD1080":
            init_params.camera_resolution = sl.RESOLUTION.HD1080
        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

        err = self.__zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            logging.error("[ZED] Cannot open ZED camera")
            exit(1)

        camera_info = self.__zed.get_camera_information()
        self.__display_resolution = sl.Resolution(camera_info.camera_resolution.width, camera_info.camera_resolution.height)

        # ZED FAST, MEDIUM, ACCURATE
        if "zed" in self.__args.model:
            positional_tracking_parameters = sl.PositionalTrackingParameters()
            # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
            positional_tracking_parameters.set_as_static = True
            self.__zed.enable_positional_tracking(positional_tracking_parameters)

            obj_param = sl.ObjectDetectionParameters()
            obj_param.enable_body_fitting = True            # Smooth skeleton move
            obj_param.enable_tracking = True                # Track people across images flow
            if self.__args.model == "zed-fast":
                obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST
            elif self.__args.model == "zed-medium":
                obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_MEDIUM
            else:
                obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_ACCURATE
            obj_param.body_format = sl.BODY_FORMAT.POSE_18  # Choose the BODY_FORMAT you wish to use

            # Enable Object Detection module
            self.__zed.enable_object_detection(obj_param)

            self.__obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
            self.__obj_runtime_param.detection_confidence_threshold = 40

        left_calibration = self.__zed.get_camera_information().calibration_parameters.left_cam
        self.__fx = left_calibration.fx
        self.__fy = left_calibration.fy
        self.__cx = left_calibration.cx
        self.__cy = left_calibration.cy
        self.__image_width = camera_info.camera_resolution.width
        self.__image_height = camera_info.camera_resolution.height

    def get_image(self):
        logging.debug("[ZED] Get image")
        if self.__zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.__zed.retrieve_image(self.__image, sl.VIEW.LEFT, sl.MEM.CPU, self.__display_resolution)
            t = time.time()
            if "zed" in self.__args.model:
                self.__zed.retrieve_objects(self.__bodies, self.__obj_runtime_param)
                self.__keypoint = self.parse_keypoint_from_object(self.__bodies.object_list)
                # print(self.__keypoint)
            if "zed" == self.__args.camera:
                self.__zed.retrieve_measure(self.__depth_map, sl.MEASURE.DEPTH, sl.MEM.CPU, self.__display_resolution)
            self.__fps = 1.0 / (time.time() - t)
        return self.__image.get_data()

    def get_keypoint(self):
        logging.debug("[ZED] Get keypoint")
        return (self.__keypoint, self.__fps)

    def parse_keypoint_from_object(self, bodies):
        data = {}
        data['annots'] = []
        for body in bodies:
            annot = {}
            annot['personID'] = body.id
            annot['keypoints'] = []
            if len(body.keypoint_2d) > 0:
                for part in SKELETON_BONES:
                    kp = body.keypoint_2d[part.value]
                    kp_confidence = body.keypoint_confidence[part.value] / 100
                    annot['keypoints'].append([kp[0], kp[1], kp_confidence])

            if len(body.bounding_box_2d) > 0:
                bb_a = body.bounding_box_2d[0]
                bb_b = body.bounding_box_2d[2]
                bb_confidence = body.confidence / 100
                annot['bbox'] = [bb_a[0], bb_a[1], bb_b[0], bb_b[1], bb_confidence]
            data['annots'].append(annot)
        return data

    def get_depth(self, x, y):
        return self.__depth_map.get_value(x, y)

    def get_depth_from_keypoint(self, keypoint):
        if keypoint == None:
            logging.error("[ZED] 2D pose detection failed")
            return {}
        data = {}
        data['annots'] = []
        pos_idx = [0, 1, 2, 5, 8, 11] # Nose, Neck, R-Shoulder, L-Shoulder, R-Pelvis, L-Pelvis
        bodies = keypoint['annots']

        for body in bodies:
            annot = {}
            annot['personID'] = body['personID']
            annot['position'] = []
            for idx in pos_idx:
                keypoints = body['keypoints'][idx]
                x_pixel = keypoints[0]
                y_pixel = keypoints[1]
                depth_value = cnt = 0.0
                for i in range(-2, 3):
                    for j in range(-2, 3):
                        if x_pixel + i > 0 and x_pixel + i < self.__image_width and y_pixel + j > 0 and y_pixel + j < self.__image_height:
                            (result, depth) = self.get_depth(x_pixel + i, y_pixel + j) # (result, m)
                            if result == sl.ERROR_CODE.SUCCESS:
                                depth_value += depth
                                cnt += 1
                if cnt > 0:
                    depth_value = depth_value/cnt
                else:
                    depth_value = 0.0

                x = float(x_pixel - self.__cx) * float(depth_value) / self.__fx # meter
                y = float(y_pixel - self.__cy) * float(depth_value) / self.__fy # meter
                z = float(depth_value) # meter

                if np.isnan(x) or np.isinf(x):
                    x = 0.0
                if np.isnan(y) or np.isinf(y):
                    y = 0.0
                if np.isnan(z) or np.isinf(z):
                    z = 0.0

                annot['position'].append(z)
            data['annots'].append(annot)

        return data

    def get_width(self):
        return self.__zed.get_camera_information().camera_resolution.width

    def get_height(self):
        return self.__zed.get_camera_information().camera_resolution.height