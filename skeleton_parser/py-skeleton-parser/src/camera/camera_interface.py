from abc import *
from src.camera import camera_config

class CameraInterface(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_image(self):
        pass

    @abstractmethod
    def get_depth(self, x, y):
        pass

    @abstractmethod
    def get_depth_from_keypoint(self, keypoint):
        pass