from email import message
import queue
import threading
import socket
import json

global message_queue
message_queue = queue.Queue() # global message queue
lock = threading.Lock() # lock object
thread_pool = {}

def run_server(server_socket):
    print('Run UDP server')
    while True:
        data, addr = server_socket.recvfrom(65535)
        #print(data.decode())
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
    # del thread_pool[tid]
    # client_socket.close()


def accept_client(server_socket):
    tid = 0
    while True:
        client_socket, addr = server_socket.accept()
        t = threading.Thread(target=run_server, args=(client_socket, tid))
        t.start()
        thread_pool[tid] = t
        tid += 1

def execute():
    host = '192.168.0.13'
    port = 50001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    #server_socket.listen()
    t = threading.Thread(target=run_server, args=(server_socket,))
    t.start()

