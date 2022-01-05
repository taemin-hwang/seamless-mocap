import threading
import time

from transfer import skeleton_server

skeleton_server.execute()

print('hello')
while True:
    mq = skeleton_server.message_queue
    if mq.qsize() > 0:
        item = mq.get()
        print(item)
    else:
        time.sleep(0.01)
