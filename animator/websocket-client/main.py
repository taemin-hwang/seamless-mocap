# pip3 install websockets

import websocket
import socket

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(('127.0.0.1', 7777))

ws = websocket.WebSocket()
uri = "ws://10.252.72.168:8000"
ws.connect(uri)

while(True):
    bytes_address_pair = udp_socket.recvfrom(12288)
    message = bytes_address_pair[0]
    address = bytes_address_pair[1]
    client_message = message.decode('utf-8')
    print(f"< {client_message}")
    ws.send(client_message)

ws.close()