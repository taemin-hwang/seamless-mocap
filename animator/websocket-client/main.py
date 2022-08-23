# pip3 install websockets

import websocket
import socket
import time

def try_to_connect_websocket():
    ws = websocket.WebSocket()
    #url = "ws://10.252.72.168:8000"
    url = "wss://plask-keti.dot-sine.com/websocket:443"
    ws.connect(url)
    return ws

#from signal import signal, SIGPIPE, SIG_DFL
#signal(SIGPIPE, SIG_DFL)

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(('127.0.0.1', 7777))

i = 0
ws = try_to_connect_websocket()
while(True):
    print("RECEIVE MESSAGE FROM UNITY")
    bytes_address_pair = udp_socket.recvfrom(12288)
    message = bytes_address_pair[0]
    address = bytes_address_pair[1]
    client_message = message.decode('utf-8')
    #print("[SIZE: {}], {}".format(len(client_message), client_message))
    print("SEND MESSAGE TO WSS SERVER")
    try:
        ret = ws.send(client_message)
    except Exception as e:
        print(str(e))
        ws = try_to_connect_websocket()

ws.close()
