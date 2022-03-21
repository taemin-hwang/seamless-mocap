import manager as mn
import test as ts
import argparse

parser = argparse.ArgumentParser(description="Reconstruct 3D pose and shape with SMPL model")

parser.add_argument('-p', '--path', required=True, help='Path for config.json')
parser.add_argument('-v', '--visual', action='store_true', help='Enable 2D visualizer')
parser.add_argument('-s', '--smpl', action='store_true', help='Reconstruct shape with SMPL')
parser.add_argument('-k', '--keypoint', action='store_true', help='Reconstruct 3D keypoint wihtout SMPL')

args = parser.parse_args()
print('[OPTION] visual  : ', args.visual)
print('[OPTION] smpl    : ', args.smpl)
print('[OPTION] keypoint: ', args.keypoint)

manager = mn.Manager(args)
manager.initialize()
manager.run()

# tester = test.TestManager()
# tester.initialize()
# tester.run()