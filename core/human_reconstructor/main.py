from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

class MyHTTPRequestHandler( BaseHTTPRequestHandler ):
    def do_GET(self):
        print( 'get방식 요청' )

    def do_POST(self):
        print( 'post방식 요청' )
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        print(post_body)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ""
        # must encode for python 3+
        self.wfile.write(output.encode())

with socketserver.TCPServer(('127.0.0.1', 50001), MyHTTPRequestHandler) as httpd:
  print('Server listening on port 50001...')
  httpd.serve_forever()
