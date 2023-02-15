import sys
import parser as ps
import transfer as tf
import calibrator as cb
import argparse

arg_parser = argparse.ArgumentParser(description="RGB-D camera calibration")

arg_parser.add_argument('-n', '--number', required=True, help='camera number')
arg_parser.add_argument('-m', '--max', required=True, help='max camera number')
arg_parser.add_argument('-v', '--visual', action='store_true', help='enable 2D visualizer')
arg_parser.add_argument('-t', '--transfer', action='store_true', help='transfer 3D data')
arg_parser.add_argument('-o', '--output', action='store_true', help='create transition matrix')
args = arg_parser.parse_args()

if __name__ == "__main__":
    if args.output is False:
        keypoint_parser = ps.parser()
        keypoint_parser.initialize(args)

        if args.transfer is True:
            tran = tf.GuiSender()
            #tran = tf.UnitySender()
            tran.initialize("192.168.0.13", 9999)
            keypoint_parser.set_send_keypoint_3d(tran.send_3d_skeleton)
        keypoint_parser.run()
    else:
        cali = cb.calibrator(int(args.max))
        cali.initialize(args, "./etc/")
        cali.run()
