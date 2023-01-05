from src.models import model_interface

from src.models import trt_manager

class ModelManager(model_interface.ModelInterface):
    def __init__(self, args):
        self.__args = args

        self.__model_implement = None

        if "zed" in self.__args.model:
            self.__model_implement = None
        if "resnet" in self.__args.model or "densenet" in self.__args.model:
            self.__model_implement = trt_manager.TrtManager(self.__args.model)

    def get_keypoint(self, image):
        ret = None
        if self.__extern_keypoint_getter is not None:
            ret = self.__extern_keypoint_getter.get_keypoint(image)
        if self.__model_implement is not None:
            ret = self.__model_implement.get_keypoint(image)
        return ret