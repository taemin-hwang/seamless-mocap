from src.models import model_interface

import torch
import torchvision.transforms as transforms
import torch2trt
from torch2trt import TRTModule

import cv2
import PIL.Image
import os, time, sys, json, logging
import numpy as np

import trt_pose.models
from trt_pose.draw_objects import DrawObjects
from trt_pose.parse_objects import ParseObjects
import trt_pose.coco

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
device = torch.device('cuda')

def preprocess(image):
    global device
    device = torch.device('cuda')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]

class TrtManager(model_interface.ModelInterface):
    def __init__(self, model):
        super().__init__()
        with open('./etc/human_pose.json', 'r') as f:
            human_pose = json.load(f)
        self.__num_parts = len(human_pose['keypoints'])
        self.__num_links = len(human_pose['skeleton'])
        topology = trt_pose.coco.coco_category_to_topology(human_pose)
        self.__parse_objects = ParseObjects(topology)
        self.__draw_objects = DrawObjects(topology)

        if "trt" in model:
            self.__is_trt = True
        else:
            self.__is_trt = False

        if "densenet" in model:
            self.__width = 256
            self.__height = 256
            self.__name = "densenet121_baseline_att_256x256_B_epoch_160"
        else:
            self.__width = 224
            self.__height = 224
            self.__name = "resnet18_baseline_att_224x224_A_epoch_249"

        if self.__is_trt == True:
            self.__model_path = self.__name + "_trt" + ".pth"
        else:
            self.__model_path = self.__name + ".pth"

        self.__model_path = os.path.join("./model", self.__model_path)

        if self.__name == "resnet18_baseline_att_224x224_A_epoch_249":
            model = trt_pose.models.resnet18_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
            model.load_state_dict(torch.load('./model/resnet18_baseline_att_224x224_A_epoch_249.pth'))
        elif self.__name == "densenet121_baseline_att_256x256_B_epoch_160":
            model = trt_pose.models.densenet121_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
            model.load_state_dict(torch.load('./model/densenet121_baseline_att_256x256_B_epoch_160.pth'))

        if (self.__is_trt == True) and (os.path.isfile(self.__model_path) == False):
            data = torch.zeros((1, 3, self.__width, self.__height)).cuda()
            model_trt = torch2trt.torch2trt(model, [data], fp16_mode=True, max_workspace_size=1<<25)
            optimized_model = self.__model_path
            torch.save(model_trt.state_dict(), optimized_model)

        if self.__is_trt is True:
            self.__model = TRTModule()
            self.__model.load_state_dict(torch.load(self.__model_path))

            data = torch.zeros((1, 3, self.__width, self.__height)).cuda()
            t0 = time.time()
            torch.cuda.current_stream().synchronize()
            for i in range(50):
                y = self.__model(data)
            torch.cuda.current_stream().synchronize()
            t1 = time.time()
            print(50.0 / (t1 - t0))
        else:
            if self.__name == "resnet18_baseline_att_224x224_A_epoch_249":
                self.__model = trt_pose.models.resnet18_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
            elif self.__name == "densenet121_baseline_att_256x256_B_epoch_160":
                self.__model = trt_pose.models.densenet121_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
            self.__model.load_state_dict(torch.load(self.__model_path))

        print("[INFO] MODEL PATH : {}".format(self.__model_path))

    def initialize(self):
        pass

    def get_model(self):
        return self.__model

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    def get_model_path(self):
        return self.__model_path

    def get_keypoint(self, image):
        logging.debug("[TRT] Get keypoint")
        ret = {}
        ret['annots'] = []

        image_width = image.shape[1]
        image_height = image.shape[0]

        t = time.time()
        image_resized = cv2.resize(image, dsize=(self.__width, self.__height), interpolation=cv2.INTER_AREA)
        X_compress = image_width / self.__width * 1.0
        Y_compress = image_height / self.__height * 1.0
        data = preprocess(image_resized)
        cmap, paf = self.__model(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
        counts, objects, peaks = self.__parse_objects(cmap, paf)#, cmap_threshold=0.15, link_threshold=0.15)
        for i in range(counts[0]):
            keypoints = self.__get_keypoint(objects, i, peaks)
            annot = {}
            annot['personID'] = i
            annot['keypoints'] = np.zeros((18, 3))

            min_x = min_y = np.inf
            max_x = max_y = 0

            for j in range(len(keypoints)):
                if keypoints[j][1]:
                    x = round(keypoints[j][2] * self.__width * X_compress)
                    y = round(keypoints[j][1] * self.__height * Y_compress)
                    # annot['keypoints'].append([x, y, 1.0])
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y

                    cvt_idx = self.convert_idx(j)
                    annot['keypoints'][cvt_idx] = [x, y, 100.0]

            # print(annot['keypoints'])
            annot['keypoints'] = annot['keypoints'].tolist()

            annot['bbox'] = [min_x, min_y, max_x, max_y, 100.0]
            ret['annots'].append(annot)

            self.__fps = 1.0 / (time.time() - t)
        return (ret, self.__fps)

    def convert_idx(self, idx):
        trt_keypoint = ["nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle", "neck"]
        cvt_keypoint = ["nose", "neck", "right_shoulder", "right_elbow", "right_wrist", "left_shoulder", "left_elbow", "left_wrist", "right_hip", "right_knee", "right_ankle", "left_hip", "left_knee", "left_ankle", "right_eye", "left_eye", "right_ear", "left_ear"]

        keypoint_name = trt_keypoint[idx]
        cvt_idx = cvt_keypoint.index(keypoint_name)
        return cvt_idx

    def execute(self, image, image_width, image_height, t):
        image_resized = cv2.resize(image, dsize=(self.__width, self.__height), interpolation=cv2.INTER_AREA)
        X_compress = image_width / self.__width * 1.0
        Y_compress = image_height / self.__height * 1.0
        color = (0, 255, 0)
        data = preprocess(image_resized)
        cmap, paf = self.__model(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
        counts, objects, peaks = self.__parse_objects(cmap, paf)#, cmap_threshold=0.15, link_threshold=0.15)
        fps = 1.0 / (time.time() - t)
        for i in range(counts[0]):
            keypoints = self.__get_keypoint(objects, i, peaks)
            for j in range(len(keypoints)):
                if keypoints[j][1]:
                    x = round(keypoints[j][2] * self.__width * X_compress)
                    y = round(keypoints[j][1] * self.__height * Y_compress)
                    print("origin x, y : {}, {}".format(keypoints[j][2], keypoints[j][1]))
                    print("image width, height : {}, {}".format(image_width, image_height))
                    print("model width, height : {}, {}".format(self.__width, self.__height))
                    print("({}, {})".format(x, y))
                    cv2.circle(image, (x, y), 3, color, 2)
                    cv2.putText(image , "%d" % int(keypoints[j][0]), (x + 5, y),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
                    cv2.circle(image, (x, y), 3, color, 2)
        print("FPS:%f "%(fps))

        cv2.putText(image , "FPS: %f" % (fps), (20, 20),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
        return image

    def __get_keypoint(self, humans, hnum, peaks):
        #check invalid human index
        kpoint = []
        human = humans[0][hnum]
        C = human.shape[0]
        for j in range(C):
            k = int(human[j])
            if k >= 0:
                peak = peaks[0][j][k]   # peak[1]:width, peak[0]:height
                peak = (j, float(peak[0]), float(peak[1]))
                kpoint.append(peak)
                # print('index:%d : success [%5.3f, %5.3f]'%(j, peak[1], peak[2]) )
            else:
                peak = (j, None, None)
                kpoint.append(peak)
                #print('index:%d : None %d'%(j, k) )
        return kpoint
