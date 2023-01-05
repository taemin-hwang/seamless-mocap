from abc import *

class ModelInterface(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def get_keypoint(self, image):
        pass