import torch
import torchvision
import json

from src.models import model_manager

class SkeletonParser:
    def __init__(self, args):
        self.__args = args
        self.__initialized = False
        with open('human_pose.json', 'r') as f:
            self.__human_pose = json.load(f)
        self.__model_manager = model_manager.ModelManager(self.__args.model, self.__args.trt, self.__human_pose)

    def initialize(self):
        self.__model = self.__model_manager.get_model()
        self.__initialized = True

    def run(self):
        if self.__initialized != True:
            print("[ERROR] SkeletonParser is not initialized")
            return

    def shutdown(self):
        if self.__initialized != True:
            print("[ERROR] SkeletonParser is not initialized")
            return
