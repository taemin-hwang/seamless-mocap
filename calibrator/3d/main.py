import sys
import calibrator as cb
import transfer as tf

if __name__ == "__main__":
    cali = cb.calibrator()
    tran = tf.UnitySender()

    if len(sys.argv) is 1:
        cam_id = 0
    else:
        cam_id = sys.argv[1]

    cali.initialize(cam_id)
    tran.initialize("192.168.0.13", 50002)

    cali.set_send_keypoint_3d(tran.send_3d_skeleton)
    cali.run()
