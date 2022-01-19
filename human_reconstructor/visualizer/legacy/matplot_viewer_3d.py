#---------------------------------------------------
#        3D VIEWER FOR POSE ESTIMATION
#---------------------------------------------------

from IPython.display import clear_output
import matplotlib.pyplot as plt
import numpy as np
from scipy import array
from matplotlib.animation import FuncAnimation
import time
import math
import threading
from datetime import datetime

from visualizer.utils import *

class RealtimePlotter:
    def __init__(self):
        # create figure
        self.fig = plt.figure()
        self.fig.canvas.manager.set_window_title('3D Viewer')
        self.ax = self.fig.gca(projection = '3d')

        # set color
        self.fig.patch.set_facecolor([51/255, 0.0, 25/255])
        self.ax.set_facecolor([51/255, 0.0, 25/255])

        # set window size
        width = 540 / self.fig.dpi
        height = 540 / self.fig.dpi
        self.fig.set_figwidth(width)
        self.fig.set_figheight(height)
        plt.tight_layout()
        plt.ion()
        plt.show()

    def render_MV1P(self, people):
        '''render 3D skeletons'''
        #clear_output(wait=True)
        plt.cla()
        now = datetime.now()
        skeletons = people
        self.draw_skeleton(0, skeletons)
        #plt.draw()
        later = datetime.now()
        print(later-now)
        plt.pause(0.01)

    def render_3D(self, people):
        '''render 3D skeletons'''
        #clear_output(wait=True)
        plt.cla()
        now = datetime.now()
        for person in people:
            person_id = person['id']
            skeletons = person['keypoints3d']
            self.draw_skeleton(person_id, skeletons)
        #plt.draw()
        later = datetime.now()
        print(later-now)
        plt.pause(0.01)

    def draw_skeleton(self, person_id, skeletons):
        if len(skeletons) > 0:
            clr = generate_color_id_u(person_id)
            plt_clr = [clr[0]/255, clr[1]/255, clr[2]/255]

            # POSE_18 -> 18 keypoints
            if len(skeletons) == 18:
                # Bones
                # Definition of SKELETON_BONES in cv_viewer.utils.py, which slightly differs from BODY_BONES
                for bone in SKELETON_BONES:
                    kp_1 = skeletons[bone[0].value]
                    kp_2 = skeletons[bone[1].value]
                    if math.isfinite(kp_1[0]) and math.isfinite(kp_2[0]):
                        self.ax.plot([kp_1[0], kp_2[0]], [kp_1[1], kp_2[1]], [kp_1[2], kp_2[2]], color=plt_clr)

                for part in range(len(BODY_PARTS)-1): # -1 to avoid LAST
                    kp = skeletons[part]
                    norm = np.linalg.norm(kp)
                    if math.isfinite(norm):
                        self.ax.scatter(kp[0], kp[1], kp[2], color=plt_clr)

                # Create backbone (not defined in BODY_BONES)
                spine = (skeletons[BODY_PARTS.LEFT_HIP.value] + skeletons[BODY_PARTS.RIGHT_HIP.value]) / 2
                neck = skeletons[BODY_PARTS.NECK.value]
                self.ax.plot([spine[0], neck[0]], [spine[1], neck[1]], [spine[2], neck[2]], color=plt_clr)

                # Spine base joint
                if math.isfinite(np.linalg.norm(spine)):
                    self.ax.scatter(spine[0], spine[1], spine[2], color=plt_clr)

            # POSE_25 -> 25 keypoints
            elif len(skeletons) == 25:
                for bone in BODY_BONES_POSE_25:
                    kp_1 = skeletons[bone[0].value]
                    kp_2 = skeletons[bone[1].value]
                    #if math.isfinite(kp_1[0]) and math.isfinite(kp_2[0]):
                    self.ax.plot([kp_1[0], kp_2[0]], [kp_1[1], kp_2[1]], [kp_1[2], kp_2[2]], color=plt_clr)

                for part in range(len(BODY_PARTS_POSE_25)-1):
                    kp = skeletons[part]
                    #norm = np.linalg.norm(kp)
                    #if math.isfinite(norm):
                    self.ax.scatter(kp[0], kp[1], kp[2], color=plt_clr)

            # POSE_34 -> 34 keypoints
            elif len(skeletons) == 34:
                for bone in BODY_BONES_POSE_34:
                    kp_1 = skeletons[bone[0].value]
                    kp_2 = skeletons[bone[1].value]
                    if math.isfinite(kp_1[0]) and math.isfinite(kp_2[0]):
                        self.ax.plot([kp_1[0], kp_2[0]], [kp_1[1], kp_2[1]], [kp_1[2], kp_2[2]], color=plt_clr)

                for part in range(len(BODY_PARTS_POSE_34)-1):
                    kp = skeletons[part]
                    norm = np.linalg.norm(kp)
                    if math.isfinite(norm):
                        self.ax.scatter(kp[0], kp[1], kp[2], color=plt_clr)
