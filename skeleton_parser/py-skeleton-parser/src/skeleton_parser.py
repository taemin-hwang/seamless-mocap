import cv2, json, logging
from src.models import model_manager
from src.camera import camera_manager

logging.basicConfig(level=logging.DEBUG)

class SkeletonParser:
    def __init__(self, args):
        self.__args = args
        self.__model_manager = model_manager.ModelManager(self.__args)
        self.__camera_manager = camera_manager.CameraManager(self.__args)

        if ("zed" in self.__args.model) and (self.__args.camera != "zed"):
            print("[ERROR] ZED MODEL is only supported for ZED camera")
        elif ("zed" in self.__args.model) and (self.__args.camera == "zed"):
            extern_keypoint_getter = self.__camera_manager.get_keypoint
            self.__model_manager.set_extern_keypoint_getter(extern_keypoint_getter)

    def initialize(self):
        pass

    def run(self):
        while True:
            image = self.__camera_manager.get_image()
            image = self.__model_manager.get_keypoint(image)

    def shutdown(self):
        pass