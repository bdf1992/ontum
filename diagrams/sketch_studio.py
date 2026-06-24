#!/usr/bin/env python3
"""sketch_studio.py — the owner-run bridge beneath the hand-drawn sketch studio.

The browser cannot spawn a process or write the repo; it can curl a localhost
endpoint. This is that endpoint — the studio's whole IO channel, in the grain of
`loop/web.py` (the localhost owner surface) and the foundry's `infer-bridge.py`
(bdo, 2026-06-12: "launching local model … never API — more like CURL"). It is
owner-run, 127.0.0.1 only, no network egress, pure stdlib — not an ambient
daemon.

Four channels, one server:

  GET  /              → serve sketch-studio.html (read fresh each time, so edits
                        show on reload — the iteration loop)
  GET  /health        → which local minds are up (the arrival pings this)
  POST /infer         → the NL CONTROL PANEL: prompt → local model (ollama
                        qwen3:14b by default) → text/JSON back. format:"json"
                        forces parseable ops. <think> stripped.
  POST /requisition   → the canvas → SESSION loop: the parts you selected + your
                        note + the button, appended to .studio/requisitions.jsonl
                        for THIS Claude session to fold by hand. A requisition is
                        a request for work, not a fact — it does not touch the log.
  GET/POST /state     → persist the canvas (.studio/state.json) so work survives
                        a reload and the session can read the full scene.
  POST /asset         → save a placed image (.studio/assets/<name>) so an image
                        on the canvas is a real file the session can open.

  python diagrams/sketch_studio.py            # serve on 8770
  python diagrams/sketch_studio.py 8771        # alternate port
"""
import argparse
import base64
import json
import re
import sys
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent          # diagrams/
HTML = HERE / "sketch-studio.html"
DATA = HERE / ".studio"                          # gitignored runtime data
REQS = DATA / "requisitions.jsonl"
STATE = DATA / "state.json"
ASSETS = DATA / "assets"

OLLAMA = "http://localhost:11434/api/generate"
OLLAMA_TAGS = "http://localhost:11434/api/tags"
DEFAULT_MODEL = "mistral:latest"                 # reliable + fast for NL→ops JSON (no <think>); qwen3 collapses under forced-json
THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def via_ollama(prompt, model, timeout, as_json, system):
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    if system:
        payload["system"] = system
    if as_json:
        payload["format"] = "json"
    body = json.dumps(payload).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read().decode())
    text = THINK.sub("", out.get("response", "")).strip()
    return text, {"model": model or DEFAULT_MODEL, "eval_count": out.get("eval_count")}


class Handler(BaseHTTPRequestHandler):
    # --- helpers -------------------------------------------------------------
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, (bytes, bytearray)) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _read(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        return self.rfile.read(n) if n else b""

    # --- GET -----------------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html", "/studio"):
            if not HTML.exists():
                return self._send(404, "studio html missing", "text/plain")
            return self._send(200, HTML.read_bytes(), "text/html; charset=utf-8")
        if path == "/health":
            ok = {}
            try:
                with urllib.request.urlopen(OLLAMA_TAGS, timeout=2) as r:
                    ok["minds"] = [m["name"] for m in json.loads(r.read())["models"]]
            except Exception as e:
                ok["minds"] = f"down: {e}"
            return self._send(200, json.dumps({"ok": True, "default_model": DEFAULT_MODEL, **ok}))
        if path == "/state":
            return self._send(200, STATE.read_bytes() if STATE.exists() else b"{}")
        if path.startswith("/asset/"):
            f = ASSETS / SAFE.sub("_", path[len("/asset/"):])
            if f.exists():
                ext = f.suffix.lower().lstrip(".")
                ct = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                      "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml"}.get(ext, "application/octet-stream")
                return self._send(200, f.read_bytes(), ct)
            return self._send(404, '{"error":"no asset"}')
        return self._send(404, '{"error":"not found"}')

    # --- POST ----------------------------------------------------------------
    def do_POST(self):
        path = self.path.split("?", 1)[0]
        raw = self._read()
        if path == "/infer":
            try:
                req = json.loads(raw or b"{}")
            except Exception as e:
                return self._send(400, json.dumps({"error": f"bad json: {e}"}))
            prompt = (req.get("prompt") or "").strip()
            if not prompt:
                return self._send(400, json.dumps({"error": "prompt required"}))
            t0 = time.time()
            try:
                text, meta = via_ollama(prompt, req.get("model"), float(req.get("timeout", 120)),
                                        bool(req.get("json")), req.get("system"))
                return self._send(200, json.dumps({"result": text, "ms": int((time.time() - t0) * 1000), "meta": meta}))
            except Exception as e:
                return self._send(502, json.dumps({"error": str(e), "ms": int((time.time() - t0) * 1000)}))
        if path == "/requisition":
            try:
                payload = json.loads(raw or b"{}")
            except Exception as e:
                return self._send(400, json.dumps({"error": f"bad json: {e}"}))
            DATA.mkdir(exist_ok=True)
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **payload}
            with REQS.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return self._send(200, json.dumps({"ok": True, "wrote": str(REQS.relative_to(HERE.parent))}))
        if path == "/state":
            DATA.mkdir(exist_ok=True)
            STATE.write_bytes(raw or b"{}")
            return self._send(200, json.dumps({"ok": True}))
        if path == "/asset":
            try:
                payload = json.loads(raw or b"{}")
                name = SAFE.sub("_", payload.get("name", "image.png")) or "image.png"
                data_url = payload.get("data", "")
                b64 = data_url.split(",", 1)[1] if "," in data_url else data_url
                ASSETS.mkdir(parents=True, exist_ok=True)
                f = ASSETS / name
                f.write_bytes(base64.b64decode(b64))
                return self._send(200, json.dumps({"ok": True, "path": str(f.relative_to(HERE.parent)), "url": f"/asset/{name}"}))
            except Exception as e:
                return self._send(400, json.dumps({"error": str(e)}))
        return self._send(404, '{"error":"not found"}')

    def log_message(self, *a):  # quiet
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="Owner-run bridge for the hand-drawn sketch studio.")
    ap.add_argument("port", nargs="?", type=int, default=8770)
    args = ap.parse_args(argv)
    DATA.mkdir(exist_ok=True)
    print(f"sketch studio  →  http://localhost:{args.port}/")
    print(f"  control panel : NL → ollama ({DEFAULT_MODEL})   ·   /infer")
    print(f"  → session     : Send-to-Claude writes {REQS.relative_to(HERE.parent)}")
    print("  done | report : open the URL, author by gesture + talking; hit Send-to-Claude, then tell the session to read the requisition.")
    try:
        ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
