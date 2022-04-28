import cv2
import time
import numpy as np
import datetime
import glob, os
from tqdm import tqdm

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

    def __del__(self):
        if args.camera:
            self.zed.close()

    def initialize(self):
        self.pose_estimator = pe.PoseEstimator(self.args)
        self.hand_estimator = he.HandEstimator(self.args)
        self.json_writer = jw.JsonWriter()

    def run(self):
        if self.args.camera is False:
            filepath = './etc/'
            outpath = './out/'
            filename_all = self.get_mp4_array(filepath)
            fileid_all = [filename.replace('.mp4', '') for filename in filename_all]

            for i in range(len(fileid_all)):
                fileid = fileid_all[i]
                filename = filename_all[i]
                mp4path = outpath + fileid + '/'
                if not os.path.exists(mp4path):
                    print('DEBUG: Create new directory : ', mp4path)
                    os.makedirs(mp4path, exist_ok=True)
                self.read_2d_skeleton_from_video(filepath + filename, mp4path, fileid)
        else:
            self.read_2d_skeleton_from_camera()

    def get_mp4_array(self, path):
        filename_all = []
        for file in os.listdir(path):
            if file.endswith(".mp4"):
                filename_all.append(file)
        return filename_all

    def read_2d_skeleton_from_video(self, video_file, path, name):
        print('INFO: Read 2D skeleton from Video : ', video_file)
        vc = cv2.VideoCapture(video_file)
        if self.args.write:
            fourcc, self.video_writer = self.create_video_writer(int(vc.get(3)), int(vc.get(4)), path, name)
        idx = 0
        i = 1
        frame_count = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = tqdm(total = frame_count)
        while frame_count > idx:
            ret, image = vc.read()
            if ret is True:
                image, pose_results = self.get_2d_skeleton_from_image(image)
                pbar.update(i)
                if self.args.visual:
                    cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
                if self.args.write:
                    self.write_image_to_mp4(image, self.video_writer)
                    self.json_writer.write_2d_pose_skeleton(path, idx, pose_results, int(vc.get(3)), int(vc.get(4)))
                    idx += 1

        if self.args.write:
            self.video_writer.release()

    def read_2d_skeleton_from_camera(self):
        print('INFO: Read 2D skeleton from Camera')
        if self.args.write:
            fourcc, self.video_writer = self.create_video_writer(1280, 720)
        while True:
            if self.zed.grab() != sl.ERROR_CODE.SUCCESS:
                exit(1)
            image = sl.Mat()
            self.zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, self.image_size)
            image = image.get_data()[:,:,:3]
            current_fps = self.zed.get_current_fps()
            print('Current FPS : {}'.format(current_fps))
            image, pose_result = self.get_2d_skeleton_from_image(image)

            if self.args.visual:
                cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if self.args.write:
                self.write_image_to_mp4(image, self.video_writer)

            if cv2.waitKey(5) & 0xFF == 27:
                break

        if self.args.write:
            self.video_writer.release()
        image.free(sl.MEM.CPU)

    def create_video_writer(self, width, height, path='./', name='default'):
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        now = datetime.datetime.now()
        if name == 'default':
            filename = './' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.mp4'
        else:
            filename = path + name + '.mp4'

        print('INFO: Create Video : ', filename)
        video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (int(width), int(height)))
        return fourcc, video_writer

    def get_2d_skeleton_from_image(self, image):
        # To improve performance, optionally mark the image as not writeable to pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pose_results = self.pose_estimator.get_2d_pose_from_image(image)
        hand_results = self.hand_estimator.get_2d_hand_from_image(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = self.pose_estimator.get_pose_image(image, pose_results)
        image = self.hand_estimator.get_hand_image(image, hand_results)
        return image, pose_results

    def write_image_to_mp4(self, image, video_writer):
        if self.args.write:
            if self.video_writer.isOpened():
                video_writer.write(image)