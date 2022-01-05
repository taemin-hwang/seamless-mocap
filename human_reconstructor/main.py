import sys
import threading
import time
import json

from transfer import skeleton_server
from visualizer import viewer_2d

'''
  TEST CODE
'''
def run_test():
    with open("./etc/msg_2d.json", "r") as json_file:
        item = json.load(json_file)
        viewer_2d.render_2D(item)

def run():
    skeleton_server.execute()
    while True:
        mq = skeleton_server.message_queue
        if mq.qsize() > 0:
            item = json.loads(mq.get())
            #print(item)
            viewer_2d.render_2D(item)
        else:
            time.sleep(0.01)

if sys.argv.count('-t'):
    run_test()
else:
    run()
