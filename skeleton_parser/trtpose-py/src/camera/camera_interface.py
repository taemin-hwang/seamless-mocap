from abc import *
from src.camera import camera_config

class CameraInterface(metaclass=ABCMeta):
    def __init__(self, resolution: camera_config.Resolution):
        pass

    @abstractmethod
    def get_image(self):
        pass

    @abstractmethod
    def get_depth(self, x, y):
        pass