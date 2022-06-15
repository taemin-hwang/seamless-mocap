import cv2
import sys
import pyzed.sl as sl
import numpy as np
import utils
import viewer

class calibrator:
    def __init__(self):
        print("calibrator constructor")
        pass

    def initialize(self, cam_id):
        print("Recording video with mp4")

        self.__image_filename = str(cam_id)+".mp4"
        print("Filename : ", self.__image_filename)

        self.__zed = sl.Camera()

        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720
        init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

        # Open the camera
        print('Open zed cam')
        err = self.__zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)

        # Enable Positional tracking (mandatory for object detection)
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
        positional_tracking_parameters.set_as_static = True
        self.__zed.enable_positional_tracking(positional_tracking_parameters)

        self.__obj_param = sl.ObjectDetectionParameters()
        self.__obj_param.enable_body_fitting = True            # Smooth skeleton move
        self.__obj_param.enable_tracking = True                # Track people across images flow
        self.__obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST
        self.__obj_param.body_format = sl.BODY_FORMAT.POSE_34  # Choose the BODY_FORMAT you wish to use

        # Enable Object Detection module
        self.__zed.enable_object_detection(self.__obj_param)

    def run(self):
        left_calibration = self.__zed.get_camera_information().calibration_parameters.left_cam
        fx = left_calibration.fx
        fy = left_calibration.fy
        cx = left_calibration.cx
        cy = left_calibration.cy

        obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
        obj_runtime_param.detection_confidence_threshold = 20

        image_size = self.__zed.get_camera_information().camera_resolution
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        image_out = cv2.VideoWriter(self.__image_filename, fourcc, 10.0, (int(image_size.width), int(image_size.height)))

        print((image_size.width, image_size.height))
        image = sl.Mat()
        depth_map = sl.Mat()
        depth_display = sl.Mat()
        bodies = sl.Objects()

        frame_number = 0
        frame_buffer_3d = np.zeros((5, 25, 4))
        while True:
            # Grab an image
            if self.__zed.grab() == sl.ERROR_CODE.SUCCESS:
                self.__zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
                self.__zed.retrieve_image(depth_display, sl.VIEW.DEPTH)
                self.__zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
                self.__zed.retrieve_objects(bodies, obj_runtime_param)

                image_left_ocv = image.get_data()[:,:,:3]
                #cv2.imshow("ZED | 2D View", image_left_ocv)
                depth_left_ocv = depth_display.get_data()[:,:,:3]
                if len(bodies.object_list) == 1 and len(bodies.object_list[0].keypoint_2d) > 0:
                    person = bodies.object_list[0]

                    keypoint_3d_34 = utils.get_keypoint_3d(person.keypoint_2d, person.keypoint_confidence, int(image_size.width), int(image_size.height), depth_map, cx, cy, fx, fy)
                    keypoint_3d_25 = utils.convert_25_from_34(keypoint_3d_34)
                    frame_buffer_3d, avg_keypoint_3d = utils.smooth_3d_pose(frame_buffer_3d, keypoint_3d_25)
                    overlay = viewer.render_2D(depth_left_ocv, bodies.object_list, self.__obj_param.enable_tracking, self.__obj_param.body_format)

                    data = utils.get_udp_message(avg_keypoint_3d)
                    if len(data) > 0:
                        self.__send_keypoint_3d(data)

                cv2.imshow("ZED | DEPTH View", overlay)

                if image_out.isOpened():
                    pass
                    #image_out.write(image_left_ocv)
                else:
                    print('File open failed')

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        image_out.release()
        self.__zed.close()
        image.free(sl.MEM.CPU)

    def set_send_keypoint_3d(self, send_keypoint_3d_func):
        self.__send_keypoint_3d = send_keypoint_3d_func