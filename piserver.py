#https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

import os
import time
import multiprocessing as mp
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

import json
import re

VAL_MOTEUR_MIN = -100
VAL_MOTEUR_MAX = 100

COMMANDS = set("forward down frontT backT".split())

commandQueue = mp.Queue()

def printAREM(*arg, **kwargs):
    print("[AREM]", *arg, **kwargs)

def info(obj):
    typestr = re.sub(r"^<class '(.*)'>$", r"<\1>", repr(type(obj)))
    return "{} {}".format(typestr, repr(obj))

def show(**kwargs):
    ''' montre la valeur de la valiable renseignée '''
    items = kwargs.items()
    assert len(items) == 1
    key, value = next(iter(items)) # équivalent à items[0]
    printAREM("{}:: {}".format(key, info(value))) # f remplace les termes entre crochets par leurs valeurs


def nope(*args, **kwargs):
    pass


def action_tell(command):
    """Print les valeurs des 4 moteurs
    
    :param: command Dictionnaire contenant les valeurs pour les clés à metter à jour.
    """
    for key, value in command.items():
        printAREM("  {}: {}".format(key, value))
    time.sleep(2.0) # seconds


def serve_with_action_handler(port=9000, host='', action=nope): # action est l'action qu'on veut voir effectuée avec les informations de POST
    ''' fonction serveur '''
    class Handler(SimpleHTTPRequestHandler):
        log_message = nope # on rédéfinit la fonction log_message

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length).decode("utf-8")
            
            body = json.loads(post_body)
            ok = isinstance(body, dict) # json peut renvoyer plein de trucs, mais on attend un dict
            ok = ok and body.keys() <= COMMANDS # on regarde si les clefs reçues sont dans l'ensemble attendu
            ok = ok and all(isinstance(val, int) and VAL_MOTEUR_MIN <= val <= VAL_MOTEUR_MAX for val in body.values()) # (...for...) est un générateur, all s'en sert

            if ok:
                code_ok_noContent = 204
                code = code_ok_noContent
            else:
                code_error = 400
                code = code_error
            
            printAREM("POST / {}:".format(code))
            self.send_response(code)
            self.end_headers()

            if ok:
                command = body
                commandQueue.put(command)

    def serve():
        server_address = (host, port)
        http_server = HTTPServer(server_address, Handler)
        printAREM("Starting http server on port {port}".format(port=port))
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        printAREM("Stoping http server")

    def queueRunner():
        while True:
            command = commandQueue.get(block=True)
            action(command)
    
    pqr = mp.Process(target=queueRunner)
    pqr.start()
    serve()
    pqr.join()

if __name__ == '__main__': # sert à savoir si on est utilisé comme module ou comme programme principal
    from sys import argv
    workingDirectory = "../remote"
    port = 9000
    host = ''
    if len(argv) >= 2: # on regarde s'il y a au moins un argument
        workingDirectory = argv[1]
        if len(argv) >= 3:
            port = int(argv[2])
            if len(argv) >= 4:
                host = argv[3]
    os.chdir(workingDirectory)

    serve_with_action_handler(port=port, host=host, action=action_tell)
