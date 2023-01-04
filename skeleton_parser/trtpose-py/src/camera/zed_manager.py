from src.camera import camera_interface, camera_config

class ZedManager(camera_interface.CameraInterface):
    def __init__(self, resolution):
        super().__init__(resolution)

        if resolution == camera_config.Resolution.HD720:
            pass

    def get_image(self):
        pass

    def get_depth(self, x, y):
        pass