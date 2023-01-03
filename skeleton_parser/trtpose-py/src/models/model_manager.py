import torch
import torch2trt
from torch2trt import TRTModule

from src import models
import os

class ModelManager:
    def __init__(self, level, is_trt, human_pose):
        self.__num_parts = len(human_pose['keypoints'])
        self.__num_links = len(human_pose['skeleton'])

        self.__is_trt = is_trt

        if level == str(2):
            self.__width = 256
            self.__height = 256
            self.__name = "densenet121_baseline_att_256x256_B_epoch_160"
        elif level == str(3):
            self.__width = 320
            self.__height = 320
            self.__name = "densenet121_baseline_att_320x320_A_epoch_240"
        else:
            self.__width = 224
            self.__height = 224
            self.__name = "resnet18_baseline_att_224x224_A_epoch_249"

        if is_trt == True:
            self.__model_path = self.__name + "_trt" + ".pth"
        else:
            self.__model_path = self.__name + ".pth"

        self.__model_path = os.path.join("./model", self.__model_path)
        print("[INFO] model path : {}".format(self.__model_path))

        if is_trt == True and os.path.isfile(self.__model_path) == False:
            if self.__name == "resnet18_baseline_att_224x224_A_epoch_249":
                model = models.resnet18_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
                model.load_state_dict(torch.load('./model/resnet18_baseline_att_224x224_A_epoch_249.pth'))
            elif self.__name == "densenet121_baseline_att_256x256_B_epoch_160":
                model = models.densenet121_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
                model.load_state_dict(torch.load('./model/densenet121_baseline_att_256x256_B_epoch_160.pth'))
            elif self.__name == "densenet121_baseline_att_320x320_A_epoch_240":
                model = models.densenet121_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
                model.load_state_dict(torch.load('./model/densenet121_baseline_att_320x320_A_epoch_240.pth'))

            model.eval()
            data = torch.zeros((1, 3, self.__width, self.__height)).cuda()
            model_trt = torch2trt.torch2trt(model, [data], fp16_mode=True, max_workspace_size=1<<25)
            optimized_model = self.__model_path
            torch.save(model_trt.state_dict(), optimized_model)

    def get_model(self):
        if self.__is_trt is True:
            self.__model = TRTModule()
            self.__model.load_state_dict(torch.load(self.__model_path))
        else:
            if self.__name == "resnet18_baseline_att_224x224_A_epoch_249":
                self.__model = models.resnet18_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
                self.__model.load_state_dict(torch.load('./model/resnet18_baseline_att_224x224_A_epoch_249.pth'))
            elif self.__name == "densenet121_baseline_att_256x256_B_epoch_160":
                self.__model = models.densenet121_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
                self.__model.load_state_dict(torch.load('./model/densenet121_baseline_att_256x256_B_epoch_160.pth'))
            elif self.__name == "densenet121_baseline_att_320x320_A_epoch_240":
                self.__model = models.densenet121_baseline_att(self.__num_parts, 2 * self.__num_links).cuda().eval()
                self.__model.load_state_dict(torch.load('./model/densenet121_baseline_att_320x320_A_epoch_240.pth'))
        return self.__model
