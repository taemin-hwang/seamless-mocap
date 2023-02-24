from src.camera import camera_interface, camera_config
try:
    import pyrealsense2.pyrealsense2 as rs
except ImportError:
    print("Cannot import pyrealsense2")
import cv2
import sys
import numpy as np
import logging
import time

class RealsenseManager(camera_interface.CameraInterface):
    def __init__(self, args):
        self.__args = args
        self.__fps = 0.0
        self.__depth_map = None

    def initialize(self):
        resolution = self.__args.resolution
        self.__pipeline = rs.pipeline()
        config = rs.config()

        width = 1920
        hegith = 1080
        if resolution == "HD720":
            width = 1280
            hegith = 720
        elif resolution == "HD1080":
            width = 1920
            hegith = 1080

        config.enable_stream(rs.stream.color, width, hegith, rs.format.bgr8, 15)
        # config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 15)
        profile = self.__pipeline.start(config)
        intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        self.__cx = intr.ppx
        self.__cy = intr.ppy
        self.__fx = intr.fx
        self.__fy = intr.fy
        self.__image_width = width
        self.__image_height = hegith

    def get_image(self):
        frames = self.__pipeline.wait_for_frames()
        # depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        # depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        # self.__depth_map = depth_frame
        return color_image

    def get_depth(self, x, y):
        if not self.__depth_map:
            return True, 0 # TODO: NEED TO CHANGE FROM TRUE TO FALSE
        return self.__depth_map.get_distance(x, y)

    def get_depth_from_keypoint(self, keypoint):
        if keypoint == None:
            logging.error("[Realsense] 2D pose detection failed")
            return {}
        data = {}
        data['annots'] = []
        pos_idx = [0, 1, 2, 5, 8, 11] # Nose, Neck, R-Shoulder, L-Shoulder, R-Pelvis, L-Pelvis
        bodies = keypoint['annots']

        for body in bodies:
            annot = {}
            annot['personID'] = body['personID']
            annot['position'] = []
            for idx in pos_idx:
                keypoints = body['keypoints'][idx]
                x_pixel = keypoints[0]
                y_pixel = keypoints[1]
                depth_value = cnt = 0.0
                for i in range(-2, 3):
                    for j in range(-2, 3):
                        if x_pixel + i > 0 and x_pixel + i < self.__image_width and y_pixel + j > 0 and y_pixel + j < self.__image_height:
                            (result, depth) = self.get_depth(x_pixel + i, y_pixel + j) # (result, m)
                            if result == True:
                                depth_value += depth
                                cnt += 1
                if cnt > 0:
                    depth_value = depth_value/cnt
                else:
                    depth_value = 0.0

                x = float(x_pixel - self.__cx) * float(depth_value) / self.__fx # meter
                y = float(y_pixel - self.__cy) * float(depth_value) / self.__fy # meter
                z = float(depth_value) # meter

                if np.isnan(x) or np.isinf(x):
                    x = 0.0
                if np.isnan(y) or np.isinf(y):
                    y = 0.0
                if np.isnan(z) or np.isinf(z):
                    z = 0.0

                if x > 0 and y > 0 and z > 0:
                    c = 1.0
                else:
                    c = 0.0

                annot['position'].append([-z, x, -y, c])
            data['annots'].append(annot)

        return data