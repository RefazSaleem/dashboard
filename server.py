#!/usr/bin/env python3

import os, sys, json, logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial

def load_conf(path):
    conf = {
        "host":    "0.0.0.0",
        "port":    "8080",
        "root":    os.path.dirname(os.path.abspath(__file__)),
        "logfile": "",
        "title":   "Dashboard",
        "theme":   "android",
        "logo":    "",
    }
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    k, v = k.strip(), v.strip()
                    if k in conf:
                        conf[k] = v
    except FileNotFoundError:
        print(f"[warn] {path} not found — using defaults")
    return conf

class Handler(SimpleHTTPRequestHandler):
    config = {}

    def log_message(self, fmt, *args):
        logging.info("%s - %s" % (self.address_string(), fmt % args))

    def do_GET(self):
        if self.path == "/api/config":
            body = json.dumps({
                "title": self.config.get("title", "Dashboard"),
                "theme": self.config.get("theme", "android"),
                "logo":  self.config.get("logo",  ""),
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

if __name__ == "__main__":
    conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.conf")
    conf = load_conf(conf_path)

    host    = conf["host"]
    port    = int(conf["port"])
    root    = conf["root"]
    logfile = conf["logfile"]

    handlers = [logging.StreamHandler(sys.stdout)]
    if logfile:
        os.makedirs(os.path.dirname(logfile), exist_ok=True)
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )

    os.chdir(root)
    Handler.config = conf
    handler = partial(Handler, directory=root)
    httpd = HTTPServer((host, port), handler)

    logging.info(f"Dashboard  : http://{host}:{port}")
    logging.info(f"Root       : {root}")
    logging.info(f"Title      : {conf['title']}")
    logging.info(f"Theme      : {conf['theme']}")
    if logfile:
        logging.info(f"Log        : {logfile}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopped.")


