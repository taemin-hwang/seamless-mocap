import cv2
import time
import numpy as np

import mediapipe as mp
import pyzed.sl as sl

import estimator.hand_estimator as he
import estimator.pose_estimator as pe
import writer.json_writer as jw

class SkeletonWriter:
    def __init__(self, args):
        # For webcam input:
        if args.camera:
            self.zed = sl.Camera()
            init_params = sl.InitParameters()
            init_params.camera_resolution = sl.RESOLUTION.HD720
            err = self.zed.open(init_params)
            self.image_size = self.zed.get_camera_information().camera_resolution
            if err != sl.ERROR_CODE.SUCCESS:
                exit(1)
        self.args = args

    def initialize(self):
        self.pose_estimator = pe.PoseEstimator()
        self.hand_estimator = he.HandEstimator()
        self.json_writer = jw.JsonWriter()

    def run(self):
        if self.args.camera is False:
            self.read_2d_skeleton_from_video('./etc/cam1.mp4')
        else:
            self.read_2d_skeleton_from_camera()

    def read_2d_skeleton_from_video(self, video_file):
        vc = cv2.VideoCapture(video_file)
        while True:
            ret, image = vc.read()
            image = self.get_2d_skeleton_from_image(image)

            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break

    def read_2d_skeleton_from_camera(self):
        while True:
            if self.zed.grab() != sl.ERROR_CODE.SUCCESS:
                exit(1)
            image = sl.Mat()
            self.zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, self.image_size)
            image = image.get_data()[:,:,:3]
            current_fps = self.zed.get_current_fps()
            print('Current FPS : {}'.format(current_fps))
            image = self.get_2d_skeleton_from_image(image)

            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break

        self.zed.close()
        image.free(sl.MEM.CPU)

    def get_2d_skeleton_from_image(self, image):
        # To improve performance, optionally mark the image as not writeable to pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pose_results = self.pose_estimator.get_2d_pose_from_image(image)
        #hand_results = self.hand_estimator.get_2d_hand_from_image(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = self.pose_estimator.get_pose_image(image, pose_results)
        #image = self.hand_estimator.get_hand_image(image, hand_results)
        return image