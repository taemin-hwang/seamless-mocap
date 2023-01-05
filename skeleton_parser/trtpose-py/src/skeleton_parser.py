import cv2
import json
import time
from src.models import model_manager
from src.camera import camera_manager
class SkeletonParser:
    def __init__(self, args):
        self.__args = args
        self.__initialized = False

        self.__model_manager = model_manager.ModelManager(self.__args)
        self.__camera_manager = camera_manager.CameraManager(self.__args)

        # self.__image_width = self.__zed_manager.get_width()
        # self.__image_height = self.__zed_manager.get_height()

    def initialize(self):
        # self.__model = self.__model_manager.get_model()
        # self.__initialized = True
        pass

    def run(self):
        while True:
            image = self.__camera_manager.get_image()
            image = self.__model_manager.get_keypoint(image) #execute(image.copy(), 1920, 1080, time.time())
        #     cv2.imshow("CAMERA", image)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        # cv2.destroyAllWindows()

    def shutdown(self):
        pass