from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return

        response = json.dumps(
            {
                "status": "healthy",
                "service": "daily-ticket-health",
            }
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, message_format, *args):
        print(
            f"{self.client_address[0]} - {message_format % args}",
            flush=True,
        )


if __name__ == "__main__":
    print("Starting daily-ticket-health on port 8080", flush=True)
    HTTPServer(("0.0.0.0", 8080), HealthHandler).serve_forever()