from src.camera import camera_interface, camera_config
from src.camera import zed_manager, realsense_manager

class CameraManager(camera_interface.CameraInterface):
    def __init__(self, args):
        self.__args = args
        self.__camera_manager = None

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