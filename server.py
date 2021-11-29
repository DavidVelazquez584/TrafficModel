from http.server import HTTPServer, BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        response = """{
    \"data\": [
        {\"x\":0, \"y\":1, \"z\":2},
        {\"x\":3, \"y\":4, \"z\":5},
        {\"x\":6, \"y\":7, \"z\":8}
    ]
}"""
        # send 200 response
        self.send_response(200)
        # send response headers
        self.end_headers()
        # send the body of the response
        self.wfile.write(bytes(response, "utf-8"))

httpd = HTTPServer(('localhost', 8000), MyHandler)
httpd.serve_forever()