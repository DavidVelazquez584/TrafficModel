from http.server import HTTPServer, BaseHTTPRequestHandler
from TrafficM import runModel

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self, dataJson):
        data = runModel()
        response = data
        # send 200 response
        self.send_response(200)
        # send response headers
        self.end_headers()
        # send the body of the response
        self.wfile.write(bytes(response, "utf-8"))

httpd = HTTPServer(('localhost', 8020), MyHandler)
httpd.serve_forever()