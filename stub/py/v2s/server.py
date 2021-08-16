#!/usr/bin/env python

"""
server.py is a rest server hosting scene status objects.

Endpoints:
    GET /SCENE_ID -> json object of the scene
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

from scene import SceneStatus

# default configs
_port = 8089


class S(BaseHTTPRequestHandler):
    """A simple http server."""

    def __init__(self, *args, **kwargs):
        super(S, self).__init__(*args, **kwargs)

    def do_GET(self):
        self._set_headers()
        id_ = self.path.lstrip("/")
        try:
            self.wfile.write(SceneStatus(id_=id_).get(raw=True))
        except Exception as e:
            print("vid2scene serve:", e)
        self.send_response(200)

    def do_POST(self):
        # start a new v2s proc
        # parse input
        config = ""

        # TODO: better err handling
        subprocess.Popen(["python", "vid2scene.py", json.dumps(config)])
        self.wfile.write("done".encode())

    def do_HEAD(self):
        self._set_headers()

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=S,
        addr="localhost", port=_port):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print("v2s serving on {}:{}".format(addr, port))
    httpd.serve_forever()


if __name__ == "__main__":
    run(addr="localhost", port=_port)
