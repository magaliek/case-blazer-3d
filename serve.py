"""Tiny dev server for testing the blazer .glb on laptop + phone.

Run from the repo root:  python serve.py
Then open the printed URL (laptop: localhost, phone: the LAN URL, same wifi).
"""
import http.server
import socket
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".glb": "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".js": "text/javascript",
    }

    def end_headers(self):
        # no caching, so a re-exported glb always shows up on refresh
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no packet is actually sent
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    print(f"Laptop: http://localhost:{PORT}/web/")
    print(f"Phone:  http://{lan_ip()}:{PORT}/web/   (same wifi)")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
