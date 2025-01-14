import sys
import argparse
import logging
import json

logging.basicConfig(level=logging.INFO)
import time
import traceback

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, help="port to listen on", required=True)
parser.add_argument("--model-id", type=str, help="model id", required=True)
parser.add_argument("--model-path", type=str, help="path to model", required=True)
parser.add_argument(
    "--model-arguments-path", type=str, help="path to model arguments", required=True
)
args = parser.parse_args()

model_exception = None
try:
    sys.path.insert(0, args.model_path)
    logging.info(f"Initialising model {args.model_id} from {args.model_path}...")
    with open(args.model_arguments_path, "r") as f:
        arguments = json.load(f)

    from main import Model

    model = Model(arguments)
    logging.info("Model initialised.")
except Exception as e:
    model_exception = e
    logging.error(f"Model could not be initialised: {model_exception}")

import http.server
import socketserver
import json
import threading


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_request(self, code="-", size="-"):
        """Suppress logging of requests"""
        pass

    def do_GET(self):
        if self.path == "/healthy":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"time": time.time()}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/execute":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                if model_exception != None:
                    raise model_exception

                response = model.execute(json.loads(post_data))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "error": str(e),
                            "stacktrace": traceback.format_exc(),
                            "python_version": str(sys.version_info),
                        }
                    ).encode("utf-8")
                )
        elif self.path == "/exit":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            stop_server()
        else:
            self.send_response(404)
            self.end_headers()


def stop_server():
    threading.Thread(target=server.shutdown).start()


with socketserver.TCPServer(("", args.port), SimpleHTTPRequestHandler) as server:
    server.serve_forever()
