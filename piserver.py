#https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

import os
import time
import multiprocessing as mp
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

import json
import re
from abc import ABC, abstractmethod


# Si vous développez sous VSCode avec l'extension python, vous pouvez
# voir survenir des crash de l'application (Segmentation fault).
# Ceux-ci sont dues à un bug de l'extension python.


VAL_MOTEUR_MIN = -100 # valeur minimale de commande prise en compte
VAL_MOTEUR_MAX = 100 # valeur maximale de commande prise en compte
AUTO_CANCEL_TIMING = 1.0 # seconds # temps qu'un moteur tournera si l'instruction de maintient en fonctionnement n'est pas envoyée
MOTORS = set("forward down frontT backT".split()) # noms des moteurs (commandes) pris en compte

# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
code_ok_noContent = 204 # code de réussite
code_badRequest = 400 # code d'erreur
code_serviceUnavailable = 503

workingDirectory = "remote" # dossier contenant la page web à envoyer
port = 9000 # port par défaut
host = '' # hote accepté par défaut ('' == Tous)
maxQueueSize = 4 # nombre de requêtes en attentes à partir duquel elles sont refusées

commandQueue = mp.Queue(maxsize=maxQueueSize) # file des actions reçues par le serveur et en attente de traitement

def printAREM(*arg, **kwargs):
    ''' ajoute "[AREM]" et affiche les données en paramètre '''
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


def nop(*args, **kwargs):
    pass


class BaseActionHandler(ABC):
    @abstractmethod
    def forward(self, value):
        pass
    
    @abstractmethod
    def down(self, value):
        pass

    @abstractmethod
    def frontT(self, valuevalue):
        pass
    
    @abstractmethod
    def backT(self, value):
        pass

class DummyActionHandler(BaseActionHandler):
    forward, down, frontT, backT = [nop] * 4


class ActionHandler_tell(BaseActionHandler):
    def forward(self, value):
        printAREM("  forward: {}".format(value))
    
    def down(self, value):
        printAREM("  down: {}".format(value))

    def frontT(self, value):
        printAREM("  frontT: {}".format(value))
    
    def backT(self, value):
        printAREM("  backT: {}".format(value))


def action_tell(command):
    """
    (No longer used)
    Print les valeurs des 4 moteurs.
    :param: command Dictionnaire contenant les valeurs pour les clés à mettre à jour.
    """
    for key, value in command.items():
        printAREM("  {}: {}".format(key, value))
    time.sleep(0.2) # seconds


def serve_with_action_handler(port=port, host=host, actionHandler=DummyActionHandler): # action est l'action qu'on veut voir effectuée avec les informations de POST
    """ fonction serveur """
    class Handler(SimpleHTTPRequestHandler):
        log_message = nop # on rédéfinit la fonction log_message

        def do_POST(self):
            content_length = int(self.headers['Content-Length']) # longueur du body
            post_body = self.rfile.read(content_length).decode("utf-8") #body
            
            body = json.loads(post_body)
            ok = isinstance(body, dict) # json peut renvoyer plein de trucs, mais on attend un dict
            ok = ok and body.keys() <= MOTORS # on regarde si les clefs reçues sont dans l'ensemble attendu
            ok = ok and all(val is None or isinstance(val, int) and VAL_MOTEUR_MIN <= val <= VAL_MOTEUR_MAX for val in body.values()) # (...for...) est un générateur, all s'en sert

            if ok:
                try:
                    command = body
                    commandQueue.put_nowait(command) # commande ajoutée à la file d'attente
                    code = code_ok_noContent # code de réussite
                except:
                    code = code_serviceUnavailable
            else:
                code = code_badRequest # code d'erreur
            
            printAREM("POST / {}".format(code))
            self.send_response(code) # envoi du code de réponse
            self.end_headers() # envoi de la réponse (fin)

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
        for motor in MOTORS:
            assert hasattr(actionHandler, motor), motor
        dummyTimer = threading.Timer(0, nop)
        motorThreads = dict((motor, dummyTimer) for motor in MOTORS)
        while True:
            command = commandQueue.get() # appel généralement blocant
            for key, value in command.items():
                action = getattr(actionHandler, key)

                # The action should be canceled after AUTO_CANCEL_TIMING.
                # Canceling := passing a value of 0 to the action
                if value != 0:
                    val = 0
                    thread = threading.Timer(AUTO_CANCEL_TIMING, action, args=[val])
                    motorThreads[key] = thread
                    thread.start()
                motorThreads[key].cancel()

                # Do the action (if it isn't just a keep request)
                isKeepRequest = value is None
                if not isKeepRequest:
                    action(value)
                    time.sleep(0.05)
                
    
    pqr = mp.Process(target=queueRunner) # nouveau process : execution des commandes dans la file d'attente
    pqr.start() # démarrage du process pqr
    serve() # démarrage du serveur
    pqr.join() # fin du process pqr


if __name__ == '__main__': # sert à savoir si on est utilisé comme module ou comme programme principal
    from sys import argv
    if len(argv) >= 2:
        workingDirectory = argv[1]
        if len(argv) >= 3:
            port = int(argv[2])
            if len(argv) >= 4:
                host = argv[3]
    os.chdir(workingDirectory)

    serve_with_action_handler(
        port=port,
        host=host,
        actionHandler=ActionHandler_tell()
    ) # lancement du serveur
