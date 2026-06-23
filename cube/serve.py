#!/usr/bin/env python3
"""Tiny static server with CORRECT MIME types for ES modules.

Python's stdlib http.server reads MIME types from the Windows registry, where
`.js` is often `text/plain` — and browsers refuse to load ES module scripts
unless the type is `text/javascript`, so the page comes up blank. This forces
the right types. Run from the repo root:

    python cube/serve.py            # then open http://localhost:8087/cube/
    python cube/serve.py 9000       # custom port
"""
import http.server
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8087

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map = {
    **Handler.extensions_map,
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".json": "application/json",
    ".css": "text/css",
    ".html": "text/html",
    ".wasm": "application/wasm",
}

if __name__ == "__main__":
    # ThreadingHTTPServer: a browser opens several parallel connections for
    # the ES-module graph; a single-threaded server resets all but one.
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"serving repo root at http://localhost:{PORT}/  (open /cube/)")
        httpd.serve_forever()
