from src import skeleton_parser
import argparse

parser = argparse.ArgumentParser(description="Estimate 2D pose in real-time from RGB-D camera")

parser.add_argument('-c', '--camera', default='USB', help='Camera model: zed, realsense')
parser.add_argument('-m', '--model', required=True, help='Pre-trained model: zed-fast, zed-medium, zed-accurate, resnet, densnet, resnet-trt, denset-trt, keypoint-rcnn')
parser.add_argument('-r', '--resolution', default='HD1080', help='Image resolution from RGB camera: HD720, HD1080')
parser.add_argument('-v', '--visual', action='store_true', help='Show 2D pose estimation results')
parser.add_argument('-t', '--transfer', action='store_true', help='Transfer 2D pose estimation result')

args = parser.parse_args()
print('[OPTION] camera     : {}'.format(args.camera))
print('[OPTION] model      : {}'.format(args.model))
print('[OPTION] resolution : {}'.format(args.resolution))
print('[OPTION] visual     : {}'.format(args.visual))
print('[OPTION] transfer   : {}'.format(args.transfer))

skeleton_parser_ = skeleton_parser.SkeletonParser(args)
skeleton_parser_.initialize()
skeleton_parser_.run()
skeleton_parser_.shutdown()