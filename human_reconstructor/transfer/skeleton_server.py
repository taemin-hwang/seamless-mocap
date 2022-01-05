from http.server import HTTPServer, BaseHTTPRequestHandler
import queue
import threading
import socketserver
import socket
import json

global message_queue
message_queue = queue.Queue() # global message queue
lock = threading.Lock() # lock object

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print( 'GET requenst handler' )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('<h1>hello</h1>'.encode('utf-8'))

    def do_POST(self):
        print( 'POST request handler' )
        global message_queue # declare global variable

        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        self.message = post_body

        lock.acquire() # lock acquire
        if message_queue.qsize() < 1000:
            message_queue.put(post_body)
            print('queue size : ', message_queue.qsize())
        else:
            print( 'Message queue size exceeds 1000, cannot receive anymore')
        lock.release() # lock release

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("".encode())

class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

def run_server():
    httpd = MyTCPServer(('127.0.0.1', 50001), MyHTTPRequestHandler)
    print('Server listening on port 50001...')
    httpd.serve_forever()

def execute():
    th1 = threading.Thread(target=run_server)
    th1.start()
