import threading
import json
import time
from queue import Queue
import numpy as np

from transfer import gui_sender, unity_sender
from visualizer import viewer_2d as v2d
from reconstructor import reconstructor as recon
from config import config_parser as cp

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
        t2 = threading.Thread(target=self.work_get_smpl, args=(self.q, self.reconstructor, self.gui_sender))
        t3 = threading.Thread(target=self.gui_sender.work_send_smpl)

        if self.args.smpl is True:
            t1.start()
            t2.start()
            t3.start()
            t1.join()
        else:
            t1.start()
            t1.join()

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
            self.reverse_skeleton(keypoints3d)

            if self.args.keypoint is True and self.args.visual is True:
                gui_sender.send_3d_skeletons(keypoints3d)
            if self.args.unity is True:
                unity_sender.send_3d_skeleton(keypoints3d)
            time.sleep(0.05)
            self.lock.acquire
            q.put(keypoints3d)
            self.lock.release

    def reverse_skeleton(self, keypoints3d):
        self.swap_skeleton(2, 5, keypoints3d)
        self.swap_skeleton(3, 6, keypoints3d)
        self.swap_skeleton(4, 7, keypoints3d)
        self.swap_skeleton(9, 12, keypoints3d)
        self.swap_skeleton(10, 13, keypoints3d)
        self.swap_skeleton(11, 14, keypoints3d)
        self.swap_skeleton(21, 24, keypoints3d)
        self.swap_skeleton(22, 19, keypoints3d)
        self.swap_skeleton(23, 20, keypoints3d)
        self.swap_skeleton(15, 16, keypoints3d)
        self.swap_skeleton(17, 18, keypoints3d)
        return keypoints3d

    def swap_skeleton(self, id1, id2, keypoints3d):
        tmp = keypoints3d[id1, :].copy()
        keypoints3d[id1, :] = keypoints3d[id2, :]
        keypoints3d[id2, :] = tmp
        return keypoints3d

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

    def send_smpl(self, q, recon, sender):
        qsize = q.qsize()
        kp3ds = np.empty((0, 25, 4))
        for i in range(qsize):
            keypoints3d = q.get()
            kp3ds = np.append(kp3ds, keypoints3d.reshape(1, 25, 4), axis=0)
        smpl = recon.get_smpl_bunch(kp3ds)
        if smpl:
            sender.send_smpl_bunch(smpl)

    def work_get_smpl(self, q, recon, gui_sender):
        while True:
            qsize = q.qsize()
            if qsize > self.max_frame:
                self.lock.acquire
                t = threading.Thread(target=self.send_smpl, args=(q, recon, gui_sender))
                t.start()
                self.lock.release
            time.sleep(0.01)

