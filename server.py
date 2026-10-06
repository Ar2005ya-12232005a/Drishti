from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from theme import message_page, status_page
from tracker import FollowUpTracker

HOST, PORT = "localhost", 8000


class DRISHTIServer(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        pid = query.get("pid", [""])[0].strip().upper()
        tracker = FollowUpTracker()
        try:
            tracker.load()               # reload so new assignments show up
            info = tracker.get_status(pid)
            body, code = self.status_page(info), 200
        except KeyError:
            body, code = self.message_page("Patient not found"), 404
        except (FileNotFoundError, ValueError) as e:
            body, code = self.message_page(f"Server data error: {e}"), 500

        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def status_page(info):
        return status_page(info)

    @staticmethod
    def message_page(msg):
        return message_page(msg)


if __name__ == "__main__":
    print(f"DRISHTI server running at http://{HOST}:{PORT}  (Ctrl+C to stop)")
    HTTPServer((HOST, PORT), DRISHTIServer).serve_forever()