import cv2
import sys
import pyzed.sl as sl
import numpy as np
import os

if __name__ == "__main__":
    print("Capture JPEG image")
    if len(sys.argv) == 1:
        print("Need to pass camera index")
        sys.exit()
    else:
        cam_id = sys.argv[1]
        image_path = "./" + str(cam_id)
        file_list = os.listdir(image_path)
        number = 0
        while True:
            if str(number).zfill(2) + ".jpg" not in file_list:
                filename = image_path + "/" + str(number).zfill(2) + ".jpg"
                break
            if number >= 100:
                print("Cannot exceed 100 JPEG imgea")
                sys.exit()
            number += 1

    print("Filename : ", filename)

    zed = sl.Camera()

    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.coordinate_units = sl.UNIT.METER
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    image_size = zed.get_camera_information().camera_resolution

    print((image_size.width, image_size.height))
    image = sl.Mat()
    while True:
        # Grab an image
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            image_left_ocv = image.get_data()[:,:,:3]
            cv2.imwrite(filename, image_left_ocv)
            break

    zed.close()
    image.free(sl.MEM.CPU)
