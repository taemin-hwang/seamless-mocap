import cv2
import json
import time
from src.models import model_manager
from src.camera import zed_manager, camera_config
class SkeletonParser:
    def __init__(self, args):
        self.__args = args
        self.__initialized = False
        with open('human_pose.json', 'r') as f:
            self.__human_pose = json.load(f)
        self.__model_manager = model_manager.ModelManager(self.__args.model, self.__args.trt, self.__human_pose)
        if self.__args.resolution == "HD720":
            self.__resolution = camera_config.Resolution.HD720
        else:
            self.__resolution = camera_config.Resolution.HD1080

        self.__zed_manager = zed_manager.ZedManager(self.__resolution)
        self.__image_width = self.__zed_manager.get_width()
        self.__image_height = self.__zed_manager.get_height()

    def initialize(self):
        self.__model = self.__model_manager.get_model()
        self.__initialized = True

    def run(self):
        if self.__initialized != True:
            print("[ERROR] SkeletonParser is not initialized")
            return
        while True:
            image = self.__zed_manager.get_image()
            image = self.__model_manager.execute(image.copy(), self.__image_width, self.__image_height, time.time())
            cv2.imshow("CAMERA", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def shutdown(self):
        if self.__initialized != True:
            print("[ERROR] SkeletonParser is not initialized")
            return
