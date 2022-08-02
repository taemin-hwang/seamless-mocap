import manager as mn
import argparse

parser = argparse.ArgumentParser(description="Reconstruct 3D pose in real-time from 2D skeletons")

parser.add_argument('-p', '--path', required=True, help='Path for config.json')
parser.add_argument('-v', '--visual', action='store_true', help='Enable 2D visualizer')
parser.add_argument('-g', '--gui', action='store_true', help='Enable 3D visualizer')
parser.add_argument('-u', '--unity', action='store_true', help='Test with Unity 3D')
parser.add_argument('-f', '--face', action='store_true', help='Receive face and hand status')
parser.add_argument('-w', '--write', action='store_true', help='Write debug logging')
parser.add_argument('-l', '--log', required=False, help='Read logging files from path')

args = parser.parse_args()
print('[OPTION] visual : ', args.visual)
print('[OPTION] gui    : ', args.gui)
print('[OPTION] unity  : ', args.unity)
print('[OPTION] face   : ', args.face)
print('[OPTION] write  : ', args.write)
print('[OPTION] log    : ', args.log)

manager = mn.Manager(args)
manager.initialize()
manager.run()
