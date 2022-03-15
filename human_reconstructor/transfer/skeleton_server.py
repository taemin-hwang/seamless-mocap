from email import message
import queue
import threading
import socket
import json

global message_queue
message_queue = queue.Queue() # global message queue
lock = threading.Lock() # lock object
thread_pool = {}

# Receive from UDP client
# - insert received data to the message queue
def run_server(server_socket):
    print('Run UDP server')
    while True:
        data, addr = server_socket.recvfrom(65535)
        if data:
            lock.acquire() # lock acquire
            if message_queue.qsize() < 1000:
                message_queue.put(data.decode())
                if message_queue.qsize() > 10:
                    print('WARNING: Message queue size exceeds 10, current size is ', message_queue.qsize())
            else:
                print( 'Message queue size exceeds 1000, cannot receive anymore')
            lock.release() # lock release
        else:
            break

def execute(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    t = threading.Thread(target=run_server, args=(server_socket,))
    t.start()

