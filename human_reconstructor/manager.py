import threading
import json
import time
from queue import Queue
import numpy as np

from transfer import skeleton_server
from transfer import skeleton_sender
from visualizer import viewer_2d as v2d
from reconstructor import reconstructor as recon

class Manager:
    def __init__(self, enable_viewer=False):
        print('Manager')
        self.viewer = v2d.Viewer2d()
        self.reconstructor = recon.Reconstructor()
        self.sender = skeleton_sender.SkeletonSender()
        self.enable_viewer = enable_viewer
        self.q = Queue()
        self.lock = threading.Lock()
        self.cam_num = 4
        self.max_frame = 50

    def init(self):
        self.reconstructor.initialize(self.cam_num, './etc/keti_mv1p_data')

    def run(self):
        t1 = threading.Thread(target=self.work_get_skeleton, args=(self.q, self.reconstructor))
        t2 = threading.Thread(target=self.work_get_smpl, args=(self.q, self.reconstructor, self.sender))
        t3 = threading.Thread(target=self.sender.work_send_smpl)
        t1.start()
        t2.start()
        t3.start()
        t3.join()

    def work_get_skeleton(self, q, recon):
        print('Worker: get skeleton')
        skeleton_server.execute()
        lk = skeleton_server.lock
        mq = skeleton_server.message_queue
        skeletons_2d = {}
        frame_2d_num = 0
        frame_3d_num = 0
        while True:
            if mq.qsize() > 0:
                lk.acquire()
                skeletons_2d = json.loads(mq.get())
                self.viewer.render_2d(skeletons_2d)
                recon.set_2d_skeletons(skeletons_2d)
                lk.release()
            skeletons_3d = recon.get_3d_skeletons()

            if (len(skeletons_2d) > 0 and frame_2d_num > 10):
                frame_2d_num = 0
            frame_2d_num += 1

            if (len(skeletons_3d) > 0 and frame_3d_num > 10):
                q.put(skeletons_3d)
                frame_3d_num = 0
            frame_3d_num += 1

            time.sleep(0.001)

    def work_get_smpl(self, q, recon, sender):
        print('Worker: get SMPL')
        while True:
            qsize = q.qsize()
            if qsize > self.max_frame:
                self.lock.acquire
                t = threading.Thread(target=self.send_smpl, args=(q, recon, sender))
                t.start()
                self.lock.release
            time.sleep(0.01)

    def send_smpl(self, q, recon, sender):
        qsize = q.qsize()
        kp3ds = np.empty((0, 25, 4))
        for i in range(qsize):
            keypoints3d = q.get()
            kp3ds = np.append(kp3ds, keypoints3d.reshape(1, 25, 4), axis=0)
        smpl = recon.get_smpl_bunch(kp3ds)
        if smpl:
            sender.send_smpl_bunch(smpl)