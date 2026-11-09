#!/usr/bin/env python3
"""Tiny local server that saves images posted by a test page, so a hidden browser pane can show you what it drew.

The Claude desktop browser pane often cannot be screenshotted (it is a hidden page).  The way around it: the page draws
what you want to look at onto a canvas (for example the stage plus the effects layer), posts the PNG here, and you open the
file.  See docs/DEV_NOTES.md, "Testing in the browser pane".

  python image_receiver.py [output folder] [port]      # defaults: ./dev_shots and 8766

From the page:   fetch('http://127.0.0.1:8766/?name=my_shot', {method: 'POST', body: canvas.toDataURL('image/png')})
The file is written as <output folder>/my_shot.png.  Stop the server when you are done (it has no authentication, so keep it local).
"""
import base64
import http.server
import pathlib
import sys
import urllib.parse

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dev_shots")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8766
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        name = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("name", ["shot"])[0]
        name = "".join(ch for ch in name if ch.isalnum() or ch in "-_") or "shot"
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        (OUT / (name + ".png")).write_bytes(base64.b64decode(body.split(",", 1)[1]))
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"ok")

    def log_message(self, *args):
        pass

print("saving posted images to", OUT.resolve(), "on http://127.0.0.1:%d" % PORT)
http.server.HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
