import os
import select
import time
import sys

from functools import reduce
from http.server import BaseHTTPRequestHandler, HTTPServer

log_file = open("dev.log", 'w')

hostName = '127.0.0.1'
serverPort = 8000

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if os.path.isfile("." + self.path):
            f = open("." + self.path)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(f.read(), "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open("404.html")
            print(f.read())
            self.wfile.write(bytes(f.read(), "utf-8"))

    def log_message(self, format, *args):
        log_file.write(reduce(lambda str, arg: str + ", " + arg, args) + "\n")
        log_file.flush()

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
