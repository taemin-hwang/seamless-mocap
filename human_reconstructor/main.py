from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import socket
import json

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print( 'GET requenst handler' )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('<h1>hello</h1>'.encode('utf-8'))

    def do_POST(self):
        print( 'POST request handler' )
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        self.message = post_body
        print(post_body)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ""
        self.wfile.write(output.encode())

class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

httpd = MyTCPServer(('127.0.0.1', 50001), MyHTTPRequestHandler)
print('Server listening on port 50001...')
httpd.serve_forever()