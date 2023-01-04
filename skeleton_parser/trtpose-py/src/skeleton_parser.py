import torch
import torchvision
import json

from src.models import model_manager
from src.camera import zed_manager, camera_config
class SkeletonParser:
    def __init__(self, args):
        self.__args = args
        self.__initialized = False
        with open('human_pose.json', 'r') as f:
            self.__human_pose = json.load(f)
        self.__model_manager = model_manager.ModelManager(self.__args.model, self.__args.trt, self.__human_pose)
        self.__zed_manager = zed_manager.ZedManager(camera_config.Resolution.HD720)

    def initialize(self):
        self.__model = self.__model_manager.get_model()
        self.__initialized = True

    def run(self):
        if self.__initialized != True:
            print("[ERROR] SkeletonParser is not initialized")
            return
        self.__zed_manager.get_image()

    def shutdown(self):
        if self.__initialized != True:
            print("[ERROR] SkeletonParser is not initialized")
            return
