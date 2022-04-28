import manager as mn
import tester as ts
import argparse

parser = argparse.ArgumentParser(description="Reconstruct 3D pose and shape with SMPL model")

parser.add_argument('-p', '--path', required=True, help='Path for config.json')
parser.add_argument('-v', '--visual', action='store_true', help='Enable 2D visualizer')
parser.add_argument('-s', '--smpl', action='store_true', help='Reconstruct shape with SMPL')
parser.add_argument('-k', '--keypoint', action='store_true', help='Reconstruct 3D keypoint wihtout SMPL')
parser.add_argument('-t1', '--test1', action='store_true', help='Test 1 with stored 2D skeletons')
parser.add_argument('-t2', '--test2', action='store_true', help='Test 2 with stored 2D skeletons')
parser.add_argument('-u', '--unity', action='store_true', help='Test with Unity 3D')

args = parser.parse_args()
print('[OPTION] visual  : ', args.visual)
print('[OPTION] smpl    : ', args.smpl)
print('[OPTION] keypoint: ', args.keypoint)
print('[OPTION] unity   : ', args.unity)

if args.test1 is False and args.test2 is False:
    manager = mn.Manager(args)
    manager.initialize()
    manager.run()
else:
    tester = ts.TestManager(args)
    tester.initialize()
    tester.run()
