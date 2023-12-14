import os
import io
import select
from http.server import SimpleHTTPRequestHandler
from socketserver import ForkingTCPServer

server_name = '127.0.0.1'
port = 8001

class MonitorServer(SimpleHTTPRequestHandler):
  def __init__(self, *args):
    self.log_file = os.open("dev.log", os.O_RDONLY | os.O_NONBLOCK)
    self.poll_fd = select.poll()
    self.poll_fd.register(self.log_file, select.POLLIN)
    self.log_lines_buffer = []
    self.log_lines_read = 0
    super(MonitorServer, self).__init__(*args)

  def get_last_n_lines(self, n):
    dev_handle = open('dev.log')
    offset = os.path.getsize('dev.log') - 10
    while offset > 0:
      dev_handle.seek(offset)
      logs_read = dev_handle.read()
      if logs_read.count("\n") == n:
        return logs_read
      else:
        offset -= 10
    else:
      return dev_handle.read()
  
  def do_GET(self):
    if self.path == '/monitor_logs':
      while True:
        events = self.poll_fd.poll()
        for fd, event in events:
          if event & select.POLLIN:
            if (data := os.read(fd, 1024)) != b'':
              print(data)
              response = "event: log_gen\n" + \
                        "data: " + data.decode('utf-8') + "\n\n"
              self.log_lines_buffer.append(data)
              self.send_response(200)
              self.send_header("Cache-Control", "no-store")
              self.send_header("Content-type", "text/event-stream")
              self.end_headers()
              print("response =", data.decode("utf-8"))
              self.wfile.write(bytes(response, 'utf-8'))
              self.wfile.flush()
    else:
      f = open('init.html')
      last_10_lines = self.get_last_n_lines(10)
      print("last_10_lines =", len(last_10_lines))
      init_html = f.read()
      result = init_html.replace("@log_lines", last_10_lines)
      self.send_response(200)
      self.send_header("Content-Type", "text/html")
      self.end_headers()
      self.wfile.write(bytes(result, 'utf-8'))

if __name__ == '__main__':
  server_instance = ForkingTCPServer((server_name, port), MonitorServer)
  print("Server started http://%s:%s" % (server_name, port))
  try:
    server_instance.serve_forever()
  except KeyboardInterrupt:
    pass
  finally:
    server_instance.server_close()
    print("server stopped.")