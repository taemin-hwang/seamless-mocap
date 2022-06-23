import sys
import calibrator as cb
import transfer as tf
import argparse

parser = argparse.ArgumentParser(description="RGB-D camera calibration")

parser.add_argument('-n', '--number', required=True, help='camera number')
parser.add_argument('-v', '--visual', action='store_true', help='enable 2D visualizer')
parser.add_argument('-t', '--transfer', action='store_true', help='transfer 3D data')
args = parser.parse_args()

if __name__ == "__main__":
    cali = cb.calibrator()
    cali.initialize(args)

    if args.transfer is True:
        tran = tf.GuiSender()
        #tran = tf.UnitySender()
        tran.initialize("192.168.0.13", 9999)
        cali.set_send_keypoint_3d(tran.send_3d_skeleton)
    cali.run()
