from src import skeleton_parser
import argparse

parser = argparse.ArgumentParser(description="Estimate 2D pose in real-time from RGB-D camera")

parser.add_argument('-m', '--model', required=True, help='Pre-trained model for 2D pose estimation: resnet18 or densenet121')
parser.add_argument('-r', '--resolution', default='HD1080', help='Image resolution from RGB camera')
parser.add_argument('-t', '--trt', action='store_true', help='Use pre-trained TensorRT model')
parser.add_argument('-v', '--visual', action='store_true', help='Enable 2D visualizer')

args = parser.parse_args()
print('[OPTION] model      : {}'.format(args.model))
print('[OPTION] resolution : {}'.format(args.resolution))
print('[OPTION] visual     : {}'.format(args.visual))
print('[OPTION] trt        : {}'.format(args.trt))

skeleton_parser_ = skeleton_parser.SkeletonParser(args)
skeleton_parser_.initialize()
skeleton_parser_.run()
skeleton_parser_.shutdown()