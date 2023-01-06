import sys, logging

from src.models import model_interface
from src.models import trt_manager

class ModelManager(model_interface.ModelInterface):
    def __init__(self, args):
        super().__init__()
        self.__args = args
        self.__model_implement = None

        self.__supported_models = ["zed-fast", "zed-medium", "zed-accurate", "resnet", "resnet-trt", "densenet", "densenet-trt"]

        if (self.__args.model in self.__supported_models) == False:
            logging.error("[MODEL] {} is not supported \nsupported models: {}".format(self.__args.model, self.__supported_models))
            sys.exit()

        if "zed" in self.__args.model:
            self.__model_implement = None
        if "resnet" in self.__args.model or "densenet" in self.__args.model:
            self.__model_implement = trt_manager.TrtManager(self.__args.model)

    def initialize(self):
        if self.__model_implement != None:
            self.__model_implement.initialize()

    def get_keypoint(self, image):
        ret = None
        if self._extern_keypoint_getter is not None:
            ret = self._extern_keypoint_getter(image)
        elif self.__model_implement is not None:
            ret = self.__model_implement.get_keypoint(image)
        return ret