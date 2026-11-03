#!/usr/bin/env python3
"""
ApexStock Enterprise Portfolio — Zero-Dependency Python HTTP Server
Supports local development and Render Python Web Service deployments.
"""

import os
import sys
import http.server
import socketserver
import json
from pathlib import Path

PORT = int(os.environ.get("PORT", 3000))
DIRECTORY = Path(__file__).resolve().parent

class PortfolioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def do_GET(self):
        # Healthcheck endpoint for Render
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "status": "healthy",
                "server": "Python SimpleHTTP",
                "port": PORT
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        # Security Headers
        self.send_header_hook = True
        return super().do_GET()

    def end_headers(self):
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def do_HEAD(self):
        return super().do_HEAD()

if __name__ == "__main__":
    # Ensure stdout handles UTF-8 on Windows cp1252 consoles
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioRequestHandler) as httpd:
        print("=" * 60)
        print(f"[ApexStock] Portfolio Python Server is LIVE!")
        print(f"-> Local:   http://localhost:{PORT}")
        print(f"-> Health:  http://localhost:{PORT}/healthz")
        print(f"-> Root:    {DIRECTORY}")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()
            sys.exit(0)
