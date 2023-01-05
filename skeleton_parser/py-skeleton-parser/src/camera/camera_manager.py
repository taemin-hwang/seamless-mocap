from src.camera import camera_interface, camera_config
from src.camera import zed_manager

class CameraManager(camera_interface.CameraInterface):
    def __init__(self, args):
        self.__args = args
        self.__camera_manager = None

        if self.__args.camera == "zed":
            self.__camera_manager = zed_manager.ZedManager(self.__args)

    def get_image(self):
        return self.__camera_manager.get_image()

    def get_depth(self, x, y):
        return self.__camera_manager.get_depth()

    def get_keypoint(self, image):
        ret = None
        if self.__args.camera == "zed":
            ret = self.__camera_manager.get_keypoint()
        return ret