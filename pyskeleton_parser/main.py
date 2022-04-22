import skeleton_parser as sp
import argparse

parser = argparse.ArgumentParser(description="Estimate 2D skeleton")

parser.add_argument('-v', '--visual', action='store_true', help='Enable 2D visualizer')
parser.add_argument('-c', '--camera', action='store_true', help='Enable RGB camera')

args = parser.parse_args()
print('[OPTION] visual  : ', args.visual)
print('[OPTION] camera  : ', args.camera)

skeleton_parser = sp.SkeletonParser(args)
skeleton_parser.initialize()
skeleton_parser.run()
