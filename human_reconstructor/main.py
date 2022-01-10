import sys
import threading
import time
import json

from transfer import skeleton_server
from visualizer import viewer_2d
from visualizer import viewer_3d
from reconstructor import reconstructor

'''
  TEST CODE
'''
def run_test():
    print('Run test')
#    with open("./etc/msg_2d.json", "r") as message_file:
#        skeletons = json.load(message_file)
#        viewer_2d.render_2D(skeletons)

    plotter = viewer_3d.RealtimePlotter()
    for i in range(0, 600):
        filename = str(i).zfill(6) + '.json'
        print(filename)
        with open("./etc/mvmp/" + filename, "r") as mvmp_file:
            skeletons = json.load(mvmp_file)
            plotter.render_3D(skeletons)

def run(enable_viewer):
    print('Run 3D reconstructor')
    skeleton_server.execute()
    while True:
        mq = skeleton_server.message_queue
        if mq.qsize() > 0:
            skeletons_2d = json.loads(mq.get())
            if enable_viewer is True:
                viewer_2d.render_2D(skeletons_2d)
        else:
            time.sleep(0.01)

if sys.argv.count('-t'):
    run_test()
elif sys.argv.count('-v'):
    run(enable_viewer=True)
