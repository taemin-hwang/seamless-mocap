import numpy as np
import time, logging

from src.models import model_interface
from src.models.higherhrnet.SimpleHigherHRNet import SimpleHigherHRNet
from src.models.higherhrnet.misc.visualization import draw_points, draw_skeleton, draw_points_and_skeleton, joints_dict, check_video_rotation
from src.models.higherhrnet.misc.utils import find_person_id_associations

class HigherHrNetManager(model_interface.ModelInterface):
    def __init__(self, model):

        is_trt  = False
        if model == "higherhrnet-fast":
            hrnet_weight = './model/pose_higher_hrnet_w32_512.pth'
            resolution = 512
            channel = 32
        elif model == "higherhrnet-fast":
            hrnet_weight = './model/pose_higher_hrnet_w32_640.pth'
            resolution = 640
            channel = 32
        elif model == "higherhrnet-fast":
            hrnet_weight = './model/pose_higher_hrnet_w48_640.pth'
            resolution = 640
            channel = 32
        elif model == "higherhrnet-fast-trt":
            hrnet_weight = './model/pose_higher_hrnet_w32_512.engine'
            is_trt  = True
            channel = 32
            resolution = 512
        else:
            logging.error("[ERROR] Not supported model : {}".format(model))
            hrnet_weight = './model/pose_higher_hrnet_w32_512.pth'
            channel = 32
            resolution = 512

        self.__hhrnet = SimpleHigherHRNet(c=channel, nof_joints=17, checkpoint_path=hrnet_weight, enable_tensorrt=is_trt, resolution=resolution, return_bounding_boxes=True, device='cuda')

        self.__prev_boxes = None
        self.__prev_pts = None
        self.__prev_person_ids = None
        self.__next_person_id = 0

    def initialize(self):
        pass

    def get_keypoint(self, image):
        t = time.time()

        ret = {}
        ret['annots'] = []

        frame = image
        pts = self.__hhrnet.predict(frame)
        boxes, pts = pts

        if len(pts) > 0:
            if self.__prev_pts is None and self.__prev_person_ids is None:
                person_ids = np.arange(self.__next_person_id, len(pts) + self.__next_person_id, dtype=np.int32)
                self.__next_person_id = len(pts) + 1
            else:
                boxes, pts, person_ids = find_person_id_associations(
                    boxes=boxes, pts=pts, prev_boxes=self.__prev_boxes, prev_pts=self.__prev_pts, prev_person_ids=self.__prev_person_ids,
                    next_person_id=self.__next_person_id, pose_alpha=0.2, similarity_threshold=0.4, smoothing_alpha=0.1,
                )
                self.__next_person_id = max(self.__next_person_id, np.max(person_ids) + 1)
        else:
            person_ids = np.array((), dtype=np.int32)

        self.__prev_boxes = boxes.copy()
        self.__prev_pts = pts.copy()
        self.__prev_person_ids = person_ids

        for i, (box, pt, pid) in enumerate(zip(boxes, pts, person_ids)):
            # joints_dict()[hrnet_joints_set]['skeleton']
            annot = {}
            annot['personID'] = pid
            annot['keypoints'] = np.zeros((18, 3))
            for j, kpt in enumerate(pt):
                cvt_idx = self.convert_idx(j)
                if cvt_idx != 1: # Neck
                    if kpt[2] > 0.3:
                        annot['keypoints'][cvt_idx] = [kpt[1], kpt[0], kpt[2]]
                    else:
                        annot['keypoints'][cvt_idx] = [0.0, 0.0, 0.0]

                if kpt[1] < 0 or kpt[1] > image.shape[1]:
                    annot['keypoints'][cvt_idx] = [0.0, 0.0, 0.0]
                if kpt[0] < 0 or kpt[0] > image.shape[0]:
                    annot['keypoints'][cvt_idx] = [0.0, 0.0, 0.0]

                print('[{}] {}, {}, {}(max: {}, {})'.format(j, kpt[1], kpt[0], kpt[2], image.shape[1], image.shape[0]))

            if annot['keypoints'][5][2] > 0.3 and annot['keypoints'][2][2] > 0.3:
                annot['keypoints'][1] = (annot['keypoints'][5] + annot['keypoints'][2])/2 # mid-shoudler
            else:
                annot['keypoints'][1] = [0.0, 0.0, 0.0]

            annot['keypoints'] = annot['keypoints'].tolist()
            annot['bbox'] = [box[0], box[1], box[2], box[3], 1.0]
            ret['annots'].append(annot)

        self.__fps = 1.0 / (time.time() - t)

        return ret, self.__fps

    def convert_idx(self, idx):
        hrnet_keypoint = ["nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle", "neck"]
        cvt_keypoint = ["nose", "neck", "right_shoulder", "right_elbow", "right_wrist", "left_shoulder", "left_elbow", "left_wrist", "right_hip", "right_knee", "right_ankle", "left_hip", "left_knee", "left_ankle", "right_eye", "left_eye", "right_ear", "left_ear"]

        keypoint_name = hrnet_keypoint[idx]
        cvt_idx = cvt_keypoint.index(keypoint_name)
        # logging.debug("{}-->{} : {}-->{}".format(hrnet_keypoint[idx], cvt_keypoint[cvt_idx], idx, cvt_idx))
        return cvt_idx