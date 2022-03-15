import threading
import json
import time
import pause
from queue import Queue
import numpy as np
from datetime import datetime

from transfer import skeleton_server
from transfer import skeleton_sender
from visualizer import viewer_2d as v2d
from reconstructor import reconstructor as recon
from visualizer import utils

class Manager:
    def __init__(self, enable_viewer=False):
        print('Manager')
        self.viewer = v2d.Viewer2d()
        self.reconstructor = recon.Reconstructor()
        self.sender = skeleton_sender.SkeletonSender()
        self.enable_viewer = enable_viewer
        self.mq_3d_skeleton = Queue()
        self.lk_3d_skeleton = threading.Lock()
        self.cam_num = 4
        self.min_cam = 2
        self.max_frame = 50
        self.time_delta = 50 # milli-seconds
        self.target_fps = 1000/self.time_delta
        self.buffer_size = 5
        self.min_confidence = 0.4

    def init(self):
        self.reconstructor.initialize(self.cam_num, './etc')
        skeleton_server.execute()

    def run(self):
        t1 = threading.Thread(target=self.work_get_3dskeleton, args=(self.mq_3d_skeleton, self.lk_3d_skeleton, self.reconstructor, self.sender))
        t2 = threading.Thread(target=self.work_get_smpl, args=(self.mq_3d_skeleton, self.lk_3d_skeleton, self.reconstructor, self.sender))
        t3 = threading.Thread(target=self.sender.work_send_smpl)
        t1.start()
        #t2.start()
        #t3.start()
        t1.join()

    def work_get_3dskeleton(self, mq_3d_skeleton, lk_3d_skeleton, recon, sender):
        print('Worker: get skeleton')
        lk_2d_skeleton = skeleton_server.lock
        mq_2d_skeleton = skeleton_server.message_queue
        cams = recon.get_cameras()
        matching_table = self.get_initial_matching_table(cams)
        t = self.get_initial_time()

        frame_buffer = np.ones((self.buffer_size, 25, 4))

        while True:
            t_sleep = datetime.now()
            t = self.sync_matching_table(mq_2d_skeleton, lk_2d_skeleton, matching_table, t[0], t[1], t[2])
            self.use_previous_frame(matching_table, t[0], t[1])

            valid_dlt_element = self.get_valid_dlt_element(matching_table)
            if valid_dlt_element['count'] >= self.min_cam:
               print('Try to restore 3D pose with ', valid_dlt_element['count'], 'cameras')
               valid_keypoint = np.stack(valid_dlt_element['valid_keypoint'], axis=0)
               valid_p = np.stack(valid_dlt_element['valid_P'], axis=0)
               out = recon.get_3d_skeletons(valid_keypoint, valid_p)

               frame_buffer, ret = self.smooth_3d_pose(frame_buffer, out)

               # send 3d skeleton
               ret[:, 0] = -1*ret[:, 0]
               ret[:, 1] = -1*ret[:, 1]
               ret[:, 2] = -1*ret[:, 2]
               ret[:, 3][ret[:, 3] < self.min_confidence] = 0

               lk_3d_skeleton.acquire()
               sender.send_3d_skeletons(ret)
               mq_3d_skeleton.put(ret)
               lk_3d_skeleton.release()
            else:
               print('Skip to restore 3D pose, number of valid data is ', valid_dlt_element['count'])

            self.reset_matching_table(matching_table)
            t = self.reset_time(t)

            pause.until(t_sleep.timestamp() + self.time_delta/1000)

    def work_get_smpl(self, mq_3d_skeleton, lk_3d_skeleton, recon, sender):
        print('Worker: get SMPL')
        while True:
            qsize = mq_3d_skeleton.qsize()
            if qsize > self.max_frame:
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
        matching_table = {}
        for cam_id in range(1, self.cam_num+1):
            matching_table[str(cam_id)] = {}
            matching_table[str(cam_id)]['is_valid'] = False
            matching_table[str(cam_id)]['timestamp'] = 0
            matching_table[str(cam_id)]['keypoint'] = np.zeros((25, 3))
            matching_table[str(cam_id)]['P'] = cams[str(cam_id)]['P']
        return matching_table

    def reset_matching_table(self, matching_table):
        for cam_id in range(1, self.cam_num+1):
            matching_table[str(cam_id)]['is_valid'] = False

    def get_valid_dlt_element(self, matching_table):
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
        lk_2d_skeleton.acquire()
        qsize = mq_2d_skeleton.qsize()

        for i in range(qsize):
            json_data = mq_2d_skeleton.get()
            data = json.loads(json_data)

            t = data['timestamp']

            # print('-------------------------------------')
            # print('t_start : ', datetime.fromtimestamp(t_start/1000))
            # print('t       : ', datetime.fromtimestamp(t/1000))
            # print('t_end   : ', datetime.fromtimestamp(t_end/1000))

            if t_start == -1:
                t_start = data['timestamp']
                t_end = data['timestamp'] + self.time_delta
                t_diff = datetime.now().timestamp()*1000 - t_start
            elif t < t_start:
                continue
            elif t > t_end:
                mq_2d_skeleton.put(json.dumps(data))
            else:
                cam_id = data['id']
                timestamp = data['timestamp']
                keypoints = np.array(data['annots'][0]['keypoints'])
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

    def is_time_expired(self, t_start, t_end, t_diff):
        if t_end - t_diff >= datetime.now().timestamp()*1000:
            return True
        else:
            return False

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
        ret = np.zeros((25, 4))
        # moving average
        frame_buffer = np.roll(frame_buffer, -1, axis=0)
        frame_buffer[self.buffer_size-1] = out

        for i in range(out.shape[0]):
            parts = frame_buffer[:, i, :]
            xdata = parts[:, 0]
            ydata = parts[:, 1]
            zdata = parts[:, 2]
            cdata = parts[:, 3]*100

            if np.sum(cdata) < 0.01:
                break

            x_avg = np.average(xdata, weights=cdata)
            y_avg = np.average(ydata, weights=cdata)
            z_avg = np.average(zdata, weights=cdata)
            c_avg = np.average(cdata, weights=cdata)
            ret[i] = [x_avg, y_avg, z_avg, c_avg/100]

        return frame_buffer, ret
