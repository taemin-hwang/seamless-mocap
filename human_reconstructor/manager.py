import threading
import json
import time
import pause
from queue import Queue
import numpy as np
from datetime import datetime

from transfer import skeleton_server, skeleton_sender, skeleton_udp_sender
from visualizer import viewer_2d as v2d
from config import config_parser as cp
from reconstructor import reconstructor as recon
from visualizer import utils

class Manager:
    def __init__(self, args):
        print('Manager')
        self.args = args
        self.viewer = v2d.Viewer2d()
        self.reconstructor = recon.Reconstructor()
        self.mq_3d_skeleton = Queue()
        self.lk_3d_skeleton = threading.Lock()
        self.config_parser = cp.ConfigParser(self.args.path + 'config.json')
        self.sender = skeleton_sender.SkeletonSender()
        self.udp_sender = skeleton_udp_sender.UdpSocketSender()

    def initialize(self):
        # Read configuration
        self.config = self.config_parser.GetConfig()
        self.cam_num = self.config["cam_num"]
        self.min_cam = self.config["min_cam"]
        self.max_frame = self.config["max_frame"]
        self.target_fps = self.config["fps"]
        self.time_delta = 1000/self.target_fps # milli-seconds
        self.buffer_size = self.config["buffer_size"]
        self.min_confidence = self.config["min_confidence"]
        self.reconstructor.initialize(self.args, self.config)
        skeleton_server.execute(self.config["server_ip"], self.config["server_port"])
        if self.args.visual is True:
            self.sender.initialize(self.config["gui_ip"], self.config["gui_port"])
        if self.args.unity is True:
            self.udp_sender.initialize(self.config["unity_ip"], self.config["unity_port"])

    def run(self):
        t1 = threading.Thread(target=self.work_get_3dskeleton, args=(self.mq_3d_skeleton, self.lk_3d_skeleton, self.reconstructor, self.sender, self.udp_sender))
        t2 = threading.Thread(target=self.work_get_smpl, args=(self.mq_3d_skeleton, self.lk_3d_skeleton, self.reconstructor, self.sender))
        t3 = threading.Thread(target=self.sender.work_send_smpl)

        if self.args.smpl is True:
            # Launch work threads for SMPL reconstruction
            t1.start()
            t2.start()
            t3.start()
            t1.join()
        else:
            # Launch work threads for 3D reconstruction
            t1.start()
            t1.join()

    def work_get_3dskeleton(self, mq_3d_skeleton, lk_3d_skeleton, recon, sender, udp_sender):
    # A thread for reconstruct 3D human pose with multiple 2D skeletons
    # param1: mq_3d_skeleton is message queue for putting estimated 3D human pose
    # param2: lk_3d_skeleton is lock for avoding data missing
    # param3: recon is an instance of Recounstructor
    # param4: sender is an instance of SkeletonSender which sends data to GUI server
        print('Worker: GET SKELETON')
        lk_2d_skeleton = skeleton_server.lock
        mq_2d_skeleton = skeleton_server.message_queue

        # Get initial parameters
        cams = recon.get_cameras()
        matching_table = self.get_initial_matching_table(cams)
        t = self.get_initial_time()

        frame_buffer = np.ones((self.buffer_size, 25, 4))

        # Loop for reconstruct 3D human pose
        while True:
            t_sleep = datetime.now()

            # Time-synchronization between multiple 2D skeletons with timestamp
            t = self.sync_matching_table(mq_2d_skeleton, lk_2d_skeleton, matching_table, t[0], t[1], t[2])
            self.use_previous_frame(matching_table, t[0], t[1])

            # Read data from matching table if there are time-synchronized 2D skeletons
            valid_dlt_element = self.get_valid_dlt_element(matching_table)

            # Try to reconstruct 3D human pose if the number of valid 2D skeletons exceed minimum case
            if valid_dlt_element['count'] >= self.min_cam:
                print('Try to restore 3D pose with ', valid_dlt_element['count'], 'cameras')
                valid_keypoint = np.stack(valid_dlt_element['valid_keypoint'], axis=0)
                valid_p = np.stack(valid_dlt_element['valid_P'], axis=0)

                # Get 3D human pose by using valid 2D keypoints and Camera parameter Ps
                out = recon.get_3d_skeletons(valid_keypoint, valid_p)
                # Smooth 3D human pose with weighted average filter
                frame_buffer, ret = self.smooth_3d_pose(frame_buffer, out)

                # Fit XYZ coordinates
                tmp = ret[:, 0]
                ret[:, 0] = ret[:, 1]
                ret[:, 1] = tmp
                ret[:, 2] = -1*ret[:, 2]
                ret[:, 2] += 1.1
                ret[:, 3][ret[:, 3] < self.min_confidence] = 0
                lk_3d_skeleton.acquire()
                mq_3d_skeleton.put(ret)
                lk_3d_skeleton.release()

                # Send and put 3D human pose to message queue
                if self.args.keypoint is True and self.args.visual is True:
                    sender.send_3d_skeletons(ret)
                if self.args.unity is True:
                    udp_sender.send_3d_skeleton(ret)
            else:
                print('Skip to restore 3D pose, number of valid data is ', valid_dlt_element['count'])

            self.reset_matching_table(matching_table)
            t = self.reset_time(t)

            pause.until(t_sleep.timestamp() + self.time_delta/1000)

    def work_get_smpl(self, mq_3d_skeleton, lk_3d_skeleton, recon, sender):
        print('Worker: GET SMPL')
        while True:
            qsize = mq_3d_skeleton.qsize()
            if qsize >= self.max_frame:
                t = threading.Thread(target=self.send_smpl, args=(mq_3d_skeleton, lk_3d_skeleton, recon, sender))
                t.start()
            time.sleep(0.01)

    def send_smpl(self, mq_3d_skeleton, lk_3d_skeleton, recon, sender):
        lk_3d_skeleton.acquire
        qsize = mq_3d_skeleton.qsize()
        kp3ds = np.empty((0, 25, 4))
        for i in range(qsize):
            keypoints3d = mq_3d_skeleton.get()
            kp3ds = np.append(kp3ds, keypoints3d.reshape(1, 25, 4), axis=0)
        smpl = recon.get_smpl_bunch(kp3ds)
        if smpl:
            sender.send_smpl_bunch(smpl)
        lk_3d_skeleton.release

    def get_initial_matching_table(self, cams):
    # Create initial table for time-sync
    # param1: cam is used for reading camera calibration P
    # return: initialized matching table
        matching_table = {}
        for cam_id in range(1, self.cam_num+1):
            matching_table[str(cam_id)] = {}
            matching_table[str(cam_id)]['is_valid'] = False
            matching_table[str(cam_id)]['timestamp'] = 0
            matching_table[str(cam_id)]['keypoint'] = np.zeros((25, 3))
            matching_table[str(cam_id)]['P'] = cams[str(cam_id)]['P']
        return matching_table

    def reset_matching_table(self, matching_table):
    # Reset matching table to invalid
    # param1: matchig table is a table for time-sync
        for cam_id in range(1, self.cam_num+1):
            matching_table[str(cam_id)]['is_valid'] = False

    def get_valid_dlt_element(self, matching_table):
    # Get Time-synced Keypoints and camera paramter P
    # param1: matching table is a table which providing if it is valid
    # return: valid DLT elements for 3d pose reconstruction
        valid_dlt_element = {}
        valid_dlt_element['count'] = 0
        valid_dlt_element['valid_timestamp'] = []
        valid_dlt_element['valid_keypoint'] = []
        valid_dlt_element['valid_P'] = []
        for cam_id in range(1, self.cam_num+1):
            if matching_table[str(cam_id)]['is_valid'] is True:
                valid_dlt_element['count'] += 1
                valid_dlt_element['valid_timestamp'].append(matching_table[str(cam_id)]['timestamp'])
                valid_dlt_element['valid_keypoint'].append(matching_table[str(cam_id)]['keypoint'])
                valid_dlt_element['valid_P'].append(matching_table[str(cam_id)]['P'])
        return valid_dlt_element

    def sync_matching_table(self, mq_2d_skeleton, lk_2d_skeleton, matching_table, t_start, t_end, t_diff):
    # Synchronize 2D skeletons with Timestamp, and update matching table
    # - (t < t_start)         : throw out-of-date data
    # - (t > t_end)           : put data to message queue to use later
    # - (t_start < t < t_end) : update matching table to use 3D pose estimation
    # param1: mq_2d_skeleton is message queue for putting estimated 2D human pose
    # param2: lk_2d_skeleton is lock for avoding data missing
    # param3: matching table is a table for investigating it is valid
        lk_2d_skeleton.acquire()
        qsize = mq_2d_skeleton.qsize()

        if t_start == -1:
            for i in range(qsize):
                json_data = mq_2d_skeleton.get()
                if i == qsize - 1:
                    data = json.loads(json_data)
                    t_start = data['timestamp']
                    t_end = data['timestamp'] + self.time_delta
                    t_diff = datetime.now().timestamp()*1000 - t_start
        else:
            for i in range(qsize):
                json_data = mq_2d_skeleton.get()
                data = json.loads(json_data)

                t = data['timestamp']
                if t < t_start:
                    continue
                elif t > t_end:
                    mq_2d_skeleton.put(json.dumps(data))
                else:
                    cam_id = data['id']
                    timestamp = data['timestamp']
                    keypoints = np.array(data['annots'][0]['keypoints'])
                    if self.args.visual:
                        self.viewer.render_2d(data)

                    keypoints_25 = utils.convert_25_from_34(keypoints)

                    matching_table[str(cam_id)]['is_valid'] = True
                    matching_table[str(cam_id)]['timestamp'] = timestamp
                    matching_table[str(cam_id)]['keypoint'] = keypoints_25

        lk_2d_skeleton.release()
        return (t_start, t_end, t_diff)

    def use_previous_frame(self, matching_table, t_start, t_end):
        for cam_id in range(1, self.cam_num+1):
            if matching_table[str(cam_id)]['is_valid'] is False:
                if matching_table[str(cam_id)]['timestamp'] > 0 and t_start - matching_table[str(cam_id)]['timestamp'] < self.time_delta*4:
                    matching_table[str(cam_id)]['is_valid'] = True

    def use_latest_matching_table(self, mq_2d_skeleton, lk_2d_skeleton, matching_table):
        lk_2d_skeleton.acquire()
        qsize = mq_2d_skeleton.qsize()

        for i in range(qsize):
            data = mq_2d_skeleton.get()
            cam_id = data[1]['id']
            timestamp = data[1]['timestamp']
            keypoints = data[1]['keypoints']
            matching_table[str(cam_id)]['is_valid'] = True
            matching_table[str(cam_id)]['timestamp'] = timestamp
            matching_table[str(cam_id)]['keypoint'] = keypoints
        lk_2d_skeleton.release()

    def get_initial_time(self):
        t_start = -1
        t_end = -1
        t_diff = 0
        return (t_start, t_end, t_diff)

    def reset_time(self, t):
        t_start = t[0]
        t_end = t[1]
        t_diff = t[2]
        if t_start != -1:
            t_start = t_end
            t_end = t_start + self.time_delta
        return (t_start, t_end, t_diff)

    def smooth_3d_pose(self, frame_buffer, out):
    # Smooth estimated 3D pose
    # - Store 3D pose data to frame_buffer
    # - Apply average filter by using weight, which is confidence
    # param1: frame buffer is a buffer to store 3D poses
    # param2: out is 3D pose from current frame
    # return: ret is averaged 3D pose
        ret = np.zeros((25, 4))
        # moving average
        frame_buffer = np.roll(frame_buffer, -1, axis=0)
        frame_buffer[self.buffer_size-1] = out

        for i in range(out.shape[0]):
            parts = frame_buffer[:, i, :]
            xdata = parts[:, 0]
            ydata = parts[:, 1]
            zdata = parts[:, 2]
            cdata = parts[:, 3]

            if np.sum(cdata) < 0.01:
                break

            x_avg = np.average(xdata, weights=cdata * range(1, self.buffer_size+1))
            y_avg = np.average(ydata, weights=cdata)
            z_avg = np.average(zdata, weights=cdata)
            c_avg = np.average(cdata, weights=cdata)
            ret[i] = [x_avg, y_avg, z_avg, c_avg]

        return frame_buffer, ret
