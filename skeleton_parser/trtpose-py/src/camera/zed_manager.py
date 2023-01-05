from src.camera import camera_interface, camera_config

import cv2
import sys
import pyzed.sl as sl
import numpy as np

class ZedManager(camera_interface.CameraInterface):
    def __init__(self, resolution):
        self.__zed = sl.Camera()
        self.__image = sl.Mat()
        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        if resolution == camera_config.Resolution.HD720:
            init_params.camera_resolution = sl.RESOLUTION.HD720
        elif resolution == camera_config.Resolution.HD1080:
            init_params.camera_resolution = sl.RESOLUTION.HD1080
        init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

        # Open the camera
        err = self.__zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print("[ERROR] Cannot open ZED camera")
            exit(1)

        # Get ZED camera information
        camera_info = self.__zed.get_camera_information()

        # 2D viewer utilities
        # self.__display_resolution = sl.Resolution(min(camera_info.camera_resolution.width, 1280), min(camera_info.camera_resolution.height, 720))
        self.__display_resolution = sl.Resolution(camera_info.camera_resolution.width, camera_info.camera_resolution.height)


    def get_image(self):
        if self.__zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.__zed.retrieve_image(self.__image, sl.VIEW.LEFT)#, sl.MEM.CPU, self.__display_resolution)
        return self.__image.get_data()

    def get_depth(self, x, y):
        pass

    def get_width(self):
        return self.__zed.get_camera_information().camera_resolution.width

    def get_height(self):
        return self.__zed.get_camera_information().camera_resolution.height