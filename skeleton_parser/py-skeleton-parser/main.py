from src.skeleton_parser import SkeletonParser
import argparse

parser = argparse.ArgumentParser(description="Estimate 2D pose in real-time from RGB-D camera")

parser.add_argument('-c', '--camera', default='zed', help='Camera model: zed, realsense')
parser.add_argument('-m', '--model', default='zed-medium', help='Pre-trained model \n : zed-fast, zed-medium, zed-accurate, resnet, densnet, resnet-trt, denset-trt, higherhrnet-fast, higherhrnet-fast-trt, higherhrnet-medium, higherhrnet-accurate')
parser.add_argument('-r', '--resolution', default='HD1080', help='Image resolution from RGB camera: HD720, HD1080')
parser.add_argument('-v', '--visual', action='store_true', help='Show 2D pose estimation results')
parser.add_argument('-t', '--transfer', default=True, action='store_true', help='Transfer 2D pose estimation result')

args = parser.parse_args()
print('[OPTION] camera     : {}'.format(args.camera))
print('[OPTION] model      : {}'.format(args.model))
print('[OPTION] resolution : {}'.format(args.resolution))
print('[OPTION] visual     : {}'.format(args.visual))
print('[OPTION] transfer   : {}'.format(args.transfer))

skeleton_parser = SkeletonParser(args)
skeleton_parser.initialize()
skeleton_parser.run()
skeleton_parser.shutdown()
