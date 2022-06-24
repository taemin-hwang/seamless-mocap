import threading
import json
import time
from queue import Queue
import numpy as np

from transfer import gui_sender, unity_sender
from visualizer import viewer_2d as v2d
from reconstructor import reconstructor as recon
from config import config_parser as cp
from reconstructor import preprocessor as pre
from reconstructor import postprocessor as post

class TestManager:
    def __init__(self, args):
        print('Run Test')
        self.viewer = v2d.Viewer2d()
        self.reconstructor = recon.Reconstructor()
        self.lock = threading.Lock()
        self.config_parser = cp.ConfigParser('./etc/config.json')
        self.config = self.config_parser.GetConfig()
        self.gui_sender = gui_sender.GuiSender()
        self.unity_sender = unity_sender.UnitySender()
        self.max_frame = 50
        self.args = args

    def initialize(self):
        self.q = Queue()
        self.reconstructor.initialize(self.args, self.config)
        if self.args.visual is True:
            self.gui_sender.initialize(self.config["gui_ip"], self.config["gui_port"])

        if self.args.unity is True:
            self.unity_sender.initialize(self.config["unity_ip"], self.config["unity_port"])

    def run(self):
        if self.args.test1 is True:
            t1 = threading.Thread(target=self.work_get_skeleton1, args=(self.q, self.reconstructor, self.gui_sender, self.unity_sender))
        elif self.args.test2 is True:
            t1 = threading.Thread(target=self.work_get_skeleton2, args=(self.q, self.reconstructor, self.gui_sender, self.unity_sender))
        elif self.args.test3 is True:
            t1 = threading.Thread(target=self.work_get_skeleton3, args=(self.q, self.reconstructor, self.gui_sender, self.unity_sender))

        t1.start()
        t1.join()

    def work_get_skeleton1(self, q, recon, sender, udp_sender):
        cam_num = 23
        for file_id in range(0, 799):
            for cam_id in range(1, cam_num+1):
                filename = str(file_id).zfill(6) + '_keypoints.json'
                with open("./etc/mv1p_data/openpose/" + str(cam_id) + '/' + filename, "r") as mvmp_file:
                    skeletons_2d = json.load(mvmp_file)
                    recon.set_2d_skeletons_test(cam_id, skeletons_2d)
            keypoints3d = recon.get_3d_skeletons_test()
            if self.args.keypoint is True and self.args.visual is True:
                sender.send_3d_skeletons(keypoints3d)
            if self.args.unity is True:
                udp_sender.send_3d_skeleton(keypoints3d)
            time.sleep(0.05)
            self.lock.acquire
            q.put(keypoints3d)
            self.lock.release

    def work_get_skeleton2(self, q, recon, gui_sender, unity_sender):
        cam_num = 4
        for file_id in range(5, 1799):
            for cam_id in range(1, cam_num+1):
                filename = str(file_id).zfill(6) + '.json'
                directory = './etc/keti_mv1p_data/annots/' + str(cam_id) + '/'
                with open(directory+filename, "r") as json_file:
                    json_data = json.load(json_file)
                    keypoints = np.array(json_data['annots'][0]['keypoints'])
                    recon.set_2d_skeletons_test2(cam_id, keypoints)
            keypoints3d = recon.get_3d_skeletons_test()
            keypoints3d[:, 2] = -1*keypoints3d[:, 2]
            keypoints3d = pre.reverse_skeleton(keypoints3d)

            if self.args.keypoint is True and self.args.visual is True:
                gui_sender.send_3d_skeletons(keypoints3d)
            if self.args.unity is True:
                unity_sender.send_3d_skeleton(keypoints3d)
            time.sleep(0.05)
            self.lock.acquire
            q.put(keypoints3d)
            self.lock.release

    def work_get_skeleton3(self, q, recon, gui_sender, unity_sender):
        cam_num = 4
        buffer_size = 10
        frame_buffer_3d = np.ones((buffer_size, 25, 4))
        for file_id in range(5, 500):
            for cam_id in range(1, cam_num+1):
                filename = str(file_id).zfill(6) + '.json'
                directory = './etc/sgu_mv1p_data/annots/' + str(cam_id) + '/'
                try:
                    with open(directory+filename, "r") as json_file:
                        json_data = json.load(json_file)
                        keypoints = np.array(json_data[0]['keypoints2d'])
                        recon.set_2d_skeletons_test3(cam_id, keypoints)
                except (FileNotFoundError, IOError):
                    print('file not found')

            keypoints3d = recon.get_3d_skeletons_test()
            keypoints3d[:, 2] = -1*keypoints3d[:, 2]
            keypoints3d = pre.reverse_skeleton(keypoints3d)
            frame_buffer_3d, keypoints3d = post.smooth_3d_pose(frame_buffer_3d, keypoints3d)

            if self.args.keypoint is True and self.args.visual is True:
                gui_sender.send_3d_skeletons(keypoints3d)
            if self.args.unity is True:
                unity_sender.send_3d_skeleton(keypoints3d)
            time.sleep(0.05)
            self.lock.acquire
            q.put(keypoints3d)
            self.lock.release
