from src.camera import camera_interface, camera_config

import cv2
import sys
import pyzed.sl as sl
import numpy as np

class ZedManager(camera_interface.CameraInterface):
    def __init__(self, args):
        self.__args = args
        self.__zed = sl.Camera()
        self.__image = sl.Mat()

        resolution = self.__args.resolution
        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        if resolution == camera_config.Resolution.HD720:
            init_params.camera_resolution = sl.RESOLUTION.HD720
        elif resolution == camera_config.Resolution.HD1080:
            init_params.camera_resolution = sl.RESOLUTION.HD1080

        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

        err = self.__zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print("[ERROR] Cannot open ZED camera")
            exit(1)

        camera_info = self.__zed.get_camera_information()
        self.__display_resolution = sl.Resolution(camera_info.camera_resolution.width, camera_info.camera_resolution.height)

        # ZED FAST, MEDIUM, ACCURATE
        if "zed" in self.__args.model:
            positional_tracking_parameters = sl.PositionalTrackingParameters()
            # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
            # positional_tracking_parameters.set_as_static = True
            zed.enable_positional_tracking(positional_tracking_parameters)

            obj_param = sl.ObjectDetectionParameters()
            obj_param.enable_body_fitting = True            # Smooth skeleton move
            obj_param.enable_tracking = True                # Track people across images flow
            if self.__args.model == "zed-fast":
                obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST
            elif self.__args.mode == "zed-medium":
                obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_MEDIUM
            else:
                obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_ACCURATE
            obj_param.body_format = sl.BODY_FORMAT.POSE_18  # Choose the BODY_FORMAT you wish to use

            # Enable Object Detection module
            zed.enable_object_detection(obj_param)

            obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
            obj_runtime_param.detection_confidence_threshold = 40

    def get_image(self):
        if self.__zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.__zed.retrieve_image(self.__image, sl.VIEW.LEFT)#, sl.MEM.CPU, self.__display_resolution)
            if "zed" in self.__args.model:
                pass
        return self.__image.get_data()

    def get_keypoint(self):
        return self.__keypoint

    def get_depth(self, x, y):
        pass

    def get_width(self):
        return self.__zed.get_camera_information().camera_resolution.width

    def get_height(self):
        return self.__zed.get_camera_information().camera_resolution.height