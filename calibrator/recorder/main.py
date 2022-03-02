import cv2
import sys
import pyzed.sl as sl
import numpy as np

if __name__ == "__main__":
    print("Recording video with mp4")
    if len(sys.argv) is 1:
        print("Use Default filename : video00.mp4")
        filename = "video00.mp4"
    else:
        cam_id = sys.argv[1]
        filename = "video0"+str(cam_id)+".mp4"

    print("Filename : ", filename)

    zed = sl.Camera()

    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
#    init_params.coordinate_units = sl.UNIT.METER
#    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    image_size = zed.get_camera_information().camera_resolution

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(filename, fourcc, 30.0, (int(image_size.width), int(image_size.height)))

    print((image_size.width, image_size.height))
    image = sl.Mat()
    while True:
        # Grab an image
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            image_left_ocv = image.get_data()[:,:,:3]
            cv2.imshow("ZED | 2D View", image_left_ocv)
            #print(image_left_ocv)
            if out.isOpened():
                out.write(image_left_ocv)
            else:
                print('File open failed')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    out.release()
    zed.close()
    image.free(sl.MEM.CPU)
