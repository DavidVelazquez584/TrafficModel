from http.server import HTTPServer, BaseHTTPRequestHandler
from TrafficM import runModel

class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, dataJson):
        self.data = dataJson

    def do_GET(self, dataJson):

        response = dataJson
        # send 200 response
        self.send_response(200)
        # send response headers
        self.end_headers()
        # send the body of the response
        self.wfile.write(bytes(response, "utf-8"))

data = runModel()
httpd = HTTPServer(('localhost', 8020), MyHandler.do_GET(data))
httpd.serve_forever()