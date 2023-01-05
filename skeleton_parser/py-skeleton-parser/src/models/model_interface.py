from abc import *

class ModelInterface(metaclass=ABCMeta):
    def __init__(self):
        self._extern_keypoint_getter = None
        pass

    @abstractmethod
    def get_keypoint(self, image):
        pass

    def set_extern_keypoint_getter(self, f):
        self._extern_keypoint_getter = f
        pass