import sys
import threading
import json
import time
from transfer import skeleton_server
from transfer.skeleton_sender import send_3d_skeletons
from visualizer import viewer_2d
from visualizer import viewer_3d
#from visualizer.legacy import matplot_viewer_3d

from reconstructor import reconstructor

'''
  TEST CODE
'''
def run_vis_test():
    print('Run test')

    v2d = viewer_2d.Viewer2d()
    with open("./etc/msg_2d.json", "r") as message_file:
        skeletons_2d = json.load(message_file)
        v2d.render_2d(skeletons_2d)

    v3d = viewer_3d.Viewer3d()
    v3d.init()
    for i in range(0, 600):
        filename = str(i).zfill(6) + '.json'
        #print(filename)
        with open("./etc/vis_data/" + filename, "r") as mvmp_file:
            skeletons_3d = json.load(mvmp_file)
            if(v3d.is_available()):
                v3d.render_3d(skeletons_3d)
            time.sleep(0.01)
    v3d.exit()

def run_reconstruct_test():
    recon = reconstructor.Reconstructor()
    cam_num = 23
    recon.initialize(cam_num, './etc/mv1p_data')

    for file_id in range(0, 600):
        for cam_id in range(1, cam_num+1):
            filename = str(file_id).zfill(6) + '_keypoints.json'
            with open("./etc/mv1p_data/openpose/" + str(cam_id) + '/' + filename, "r") as mvmp_file:
                skeletons_2d = json.load(mvmp_file)
                recon.set_2d_skeletons_test(cam_id, skeletons_2d)
        keypoints3d = recon.get_3d_skeletons_test()
        send_3d_skeletons(keypoints3d)
        time.sleep(0.1)

def run(enable_viewer):
    print('Run 3D reconstructor')
    recon = reconstructor.Reconstructor()
    cam_num = 4
    recon.initialize(cam_num, './etc/mv1p_data')
    skeleton_server.execute()
    while True:
        mq = skeleton_server.message_queue
        if mq.qsize() > 0:
            skeletons_2d = json.loads(mq.get())
            recon.set_2d_skeletons(skeletons_2d)
        skeletons_3d = recon.get_3d_skeletons()
        if len(skeletons_3d) > 0:
            send_3d_skeletons(skeletons_3d)
        time.sleep(0.01)

if sys.argv.count('-vt'):
    run_vis_test()
elif sys.argv.count('-rt'):
    run_reconstruct_test()
elif sys.argv.count('-voff'):
    run(enable_viewer=False)
else:
    run(enable_viewer=True)
