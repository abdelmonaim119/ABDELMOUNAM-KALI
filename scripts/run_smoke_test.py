from __future__ import annotations

import http.client
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_file(path: Path, required: list[str]) -> None:
    text = path.read_text(encoding='utf-8')
    for token in required:
        if token not in text:
            raise AssertionError(f"Missing '{token}' in {path}")


def run_http_check() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8765, timeout=5)
        for route in ["/index.html", "/about.html", "/contact.html", "/admin.html", "/projects/project-1.html"]:
            conn.request("GET", route)
            resp = conn.getresponse()
            if resp.status != 200:
                raise AssertionError(f"GET {route} returned {resp.status}")
            resp.read()
        conn.close()
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    check_file(ROOT / "admin.html", ["Only <strong>monaimabdel119@gmail.com</strong>", "view-only access"])
    check_file(ROOT / "rules.md", ["owner (`monaimabdel119@gmail.com`)", "watch/browse"])
    check_file(ROOT / "projects/project-1.html", ["Context", "Implementation Highlights", "Outcome"])
    run_http_check()
    print("Smoke tests passed.")


if __name__ == "__main__":
    main()
