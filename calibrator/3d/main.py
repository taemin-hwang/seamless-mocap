import cv2
import sys
import pyzed.sl as sl
import numpy as np

if __name__ == "__main__":
    print("Recording video with mp4")
    if len(sys.argv) is 1:
        print("Use Default filename : video00.mp4")
        image_filename = "0.mp4"
    else:
        cam_id = sys.argv[1]
        image_filename = str(cam_id)+".mp4"

    print("Filename : ", image_filename)

    zed = sl.Camera()

    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    # positional_tracking_parameters.set_as_static = True
    zed.enable_positional_tracking(positional_tracking_parameters)

    obj_param = sl.ObjectDetectionParameters()
    obj_param.enable_body_fitting = True            # Smooth skeleton move
    obj_param.enable_tracking = True                # Track people across images flow
    obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST
    obj_param.body_format = sl.BODY_FORMAT.POSE_34  # Choose the BODY_FORMAT you wish to use

    # Enable Object Detection module
    zed.enable_object_detection(obj_param)

    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    obj_runtime_param.detection_confidence_threshold = 20

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    image_size = zed.get_camera_information().camera_resolution

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    image_out = cv2.VideoWriter(image_filename, fourcc, 30.0, (int(image_size.width), int(image_size.height)))

    print((image_size.width, image_size.height))
    image = sl.Mat()
    depth_map = sl.Mat()
    depth_display = sl.Mat()
    bodies = sl.Objects()

    frame_number = 0
    while True:
        # Grab an image
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            zed.retrieve_image(depth_display, sl.VIEW.DEPTH)
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            zed.retrieve_objects(bodies, obj_runtime_param)

            image_left_ocv = image.get_data()[:,:,:3]
            cv2.imshow("ZED | 2D View", image_left_ocv)
            cv2.imshow("ZED | DEPTH View", depth_display)
            #print(image_left_ocv)
            if image_out.isOpened():
                image_out.write(image_left_ocv)

                if len(bodies) == 1 and len(bodies[0].keypoint_2d) > 0:
                    x_pixel = bodies[0].keypoint_2d[0][0] # pelvis-x
                    y_pixel = bodies[0].keypoint_2d[0][1] # pelvis-y
                    depth_value = depth_map.get_value(x,y) # mm

                    x = -x_pixel * depth_value
                    y = y_pixel * depth_value
                    z = depth_value

            else:
                print('File open failed')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    image_out.release()
    zed.close()
    image.free(sl.MEM.CPU)
