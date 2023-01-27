import cv2, json, logging, time
from src.models import model_manager
from src.camera import camera_manager
from src.visualizer import visual_manager
from src.transfer import transfer_manager

logging.basicConfig(level=logging.DEBUG)

class SkeletonParser:
    def __init__(self, args):
        self.__args = args
        self.__model_manager = model_manager.ModelManager(self.__args)
        self.__camera_manager = camera_manager.CameraManager(self.__args)
        self.__visual_manager = visual_manager.VisualManager()
        self.__transfer_manager = transfer_manager.TransferManager(self.__args)

        if ("zed" in self.__args.model) and (self.__args.camera != "zed"):
            print("[ERROR] ZED MODEL is only supported for ZED camera")
        elif ("zed" in self.__args.model) and (self.__args.camera == "zed"):
            extern_keypoint_getter = self.__camera_manager.get_keypoint
            self.__model_manager.set_extern_keypoint_getter(extern_keypoint_getter)

    def initialize(self):
        self.__model_manager.initialize()
        self.__camera_manager.initialize()
        if self.__args.transfer:
            self.__transfer_manager.initialize()

    def run(self):
        while True:
            image = self.__camera_manager.get_image()
            (keypoint, fps) = self.__model_manager.get_keypoint(image)
            depth_map = self.__camera_manager.get_depth_from_keypoint(keypoint)
            if self.__args.visual:
                self.__visual_manager.show_keypoint(image, keypoint, fps)
            else:
                logging.info("[FPS] {}".format(fps))
            if self.__args.transfer:
                self.__transfer_manager.send_result(keypoint, depth_map)

    def shutdown(self):
        pass