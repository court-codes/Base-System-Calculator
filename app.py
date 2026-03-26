"""HTTP server: serves the static UI and JSON API (stdlib only; no Flask required)."""

import json
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from calculator_core import api_calculate

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, "static")

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(
        self,
        code,
        body,
        content_type="text/plain; charset=utf-8",
        *,
        cors_api=False,
    ):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if cors_api:
            self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        path = urlparse(self.path).path
        if path != "/api/calculate":
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            path = "/index.html"
        if path.startswith("/api/"):
            self._send(404, b"Not found")
            return
        rel = path.lstrip("/")
        if ".." in rel or rel.startswith("/"):
            self._send(400, b"Bad path")
            return
        fp = os.path.join(STATIC, rel)
        if not os.path.isfile(fp):
            self._send(404, b"Not found")
            return
        ext = os.path.splitext(fp)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        with open(fp, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/calculate":
            self._send(404, b"Not found")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(
                400,
                json.dumps({"ok": False, "error": "Invalid JSON."}).encode("utf-8"),
                "application/json; charset=utf-8",
                cors_api=True,
            )
            return
        out = api_calculate(data)
        code = 200 if out.get("ok") else 400
        self._send(
            code,
            json.dumps(out).encode("utf-8"),
            "application/json; charset=utf-8",
            cors_api=True,
        )


def main():
    port = int(os.environ.get("PORT", 5000))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving http://127.0.0.1:{port}/ (Ctrl+C to stop)")
    print("Open that URL in your browser — Calculate needs the server (not a saved HTML file).")
    server.serve_forever()


if __name__ == "__main__":
    main()
