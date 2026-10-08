
"""Small dependency-free REST utility service."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def response(status: int, payload, content_type: str = "application/json"):
    if content_type == "application/json":
        data = json.dumps(payload, ensure_ascii=False).encode()
    elif isinstance(payload, str):
        data = payload.encode()
    else:
        data = payload
    return status, {"Content-Type": content_type, "Content-Length": str(len(data))}, data


def error(message: str, status: int = 400):
    return response(status, {"error": message})


class Handler(BaseHTTPRequestHandler):
    def _serve(self, method: str):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            payload = None
        status, headers, body = handle(method, self.path.split("?", 1)[0], payload)
        self.send_response(status)
        for key, value in headers.items(): self.send_header(key, value)
        self.end_headers(); self.wfile.write(body)
    do_GET = lambda self: self._serve("GET")
    do_POST = lambda self: self._serve("POST")
    do_PUT = lambda self: self._serve("PUT")
    do_DELETE = lambda self: self._serve("DELETE")
    def log_message(self, *_): pass


import difflib, json

def handle(method,path,payload):
    if method=="GET" and path=="/health": return response(200,{"ok":True,"service":"diff-api"})
    if method!="POST" or path!="/diff": return error("route not found",404)
    if not isinstance(payload,dict) or "left" not in payload or "right" not in payload: return error("left and right are required")
    left,right=str(payload["left"]),str(payload["right"]); mode=payload.get("mode","text")
    if mode=="json":
        try: left=json.dumps(json.loads(left),indent=2,sort_keys=True).splitlines(); right=json.dumps(json.loads(right),indent=2,sort_keys=True).splitlines()
        except json.JSONDecodeError: return error("left and right must be valid JSON")
    else: left,right=left.splitlines(),right.splitlines()
    diff="\n".join(difflib.unified_diff(left,right,fromfile="left",tofile="right",lineterm=""))
    return response(200,{"changed":bool(diff),"diff":diff})


def serve(host="0.0.0.0", port=8080):
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    serve()
