#https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

import sched
import json
import re

scheduler = sched.scheduler()

def printAREM(*arg, **kwargs):
    print("[AREM]", *arg, **kwargs)

def info(obj):
    typestr = re.sub(r"^<class '(.*)'>$", r"<\1>", repr(type(obj)))
    return f"{typestr} {repr(obj)}"

def show(**kwargs):
    items = kwargs.items()
    assert len(items) == 1
    key, value = next(iter(items))
    printAREM(f"{key}:: {info(value)}")


def nope(*args, **kwargs):
    pass


def action_tell(down=None, forward=None, frontT=None, backT=None):
    show(down=down)
    show(forward=forward)
    show(frontT=frontT)
    show(backT=backT)


rootPath = Path().cwd()

def serve_with_action_handler(port=9000, action=nope):
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length)
            
            body = json.loads(post_body)

            ok = isinstance(body, dict)
            ok = ok and body.keys() <= set("down forward frontT backT".split())
            ok = ok and all(isinstance(val, int) and -100 <= val <= 100 for val in body.values())
            if ok:
                ok_noContent = 204
                show(CODE=ok_noContent)
                self.send_response(ok_noContent)
                self.end_headers()
                action(**body)
                scheduler.enter(
                    delay=0,
                    priority=1,
                    action=action,
                    argument=[],
                    kwargs=body,
                )
            else:
                error = 400
                show(CODE=error)
                self.send_response(error)
                self.end_headers()

    server_address = ('', port)
    http_server = HTTPServer(server_address, Handler)
    printAREM(f"Starting http server on port {port}")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    printAREM("Stoping http server")


if __name__ == '__main__':
    from sys import argv
    workingDirectory="../remote"
    port=9000
    if len(argv) >= 2:
        workingDirectory = argv[1]
        if len(argv) >= 3:
            port = int(argv[2])
    os.chdir(workingDirectory)
    serve_with_action_handler(port=port, action=action_tell)
