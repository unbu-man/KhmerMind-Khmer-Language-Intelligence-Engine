"""Serve the demo on the local machine using the same retrieval as the CLI."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .glossary import Glossary


def handler_for(glossary: Glossary) -> type[BaseHTTPRequestHandler]:
    page = Path(__file__).with_name("demo.html").read_bytes()

    class DemoHandler(BaseHTTPRequestHandler):
        def send_body(self, code: int, body: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, code: int, payload: dict) -> None:
            self.send_body(code, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                           "application/json")

        def do_GET(self) -> None:
            url = urlsplit(self.path)
            if url.path == "/":
                self.send_body(200, page, "text/html")
            elif url.path == "/api/releases":
                self.send_json(200, {"releases": glossary.sessions})
            elif url.path == "/api/ask":
                try:
                    params = parse_qs(url.query)
                    question = params.get("question", [""])[0]
                    if len(question) > 500:
                        raise ValueError("Keep the question within 500 characters.")
                    release = int(params.get("release", [""])[0])
                    response = glossary.ask(question, release)
                except ValueError as error:
                    self.send_json(400, {"error": str(error)})
                else:
                    self.send_json(200, response)
            else:
                self.send_json(404, {"error": "Page not found."})

    return DemoHandler


def serve(glossary: Glossary, port: int) -> None:
    with ThreadingHTTPServer(("127.0.0.1", port), handler_for(glossary)) as server:
        print(f"KhmerMind is running at http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
