import os
import json
import logging
from typing import Dict, Any
from http.server import HTTPServer, SimpleHTTPRequestHandler

logger = logging.getLogger("growth.server")


class AnalyticsAPIHandler(SimpleHTTPRequestHandler):
    """
    Lightweight REST API Handler serving 4-platform live video metrics from data/analytics_history.json
    and dashboard static assets.
    """

    def do_GET(self):
        if self.path == "/api/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            history_file = "data/analytics_history.json"
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    data = f.read()
                    self.wfile.write(data.encode("utf-8"))
            else:
                fallback = {
                    "history": [{
                        "date": "2026-08-04",
                        "youtube": {"total_views": 25, "subscribers": 1, "is_live_api": False},
                        "instagram": {"estimated_weekly_reach": 120, "followers": 10, "is_live_api": False},
                        "facebook": {"total_views": 0, "followers": 0, "is_live_api": False},
                        "tiktok": {"total_views": 0, "followers": 0, "is_live_api": False}
                    }]
                }
                self.wfile.write(json.dumps(fallback).encode("utf-8"))
        else:
            super().do_GET()


def run_server(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AnalyticsAPIHandler)
    logger.info(f"Growth Analytics API Server active on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
