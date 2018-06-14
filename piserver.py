#https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

import os
import time
import multiprocessing as mp
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
from abc import ABC, abstractmethod

from util import printIDFLY, nop



# Si vous développez sous VSCode avec l'extension python, le seveur peut crasher
# lorsqu'il reçoit beaucoups de requêtes (Segmentation fault).
# Cela est dues à un bug de l'extension Python. Ça ne se produisent pas lorsque
# le serveur est lancé sans debugger, comme par exemple, depuis la ligne de
# commande.


# Les constantes ci-dessous sont utilisées pour la vérification de la validité des données
VAL_MOTEUR_MAX = 100 # valeur maximale de commande prise en compte
VAL_MOTEUR_MIN = -VAL_MOTEUR_MAX # valeur minimale de commande prise en compte
AUTO_CANCEL_TIMING = 1.0 # seconds # temps qu'un moteur tournera si l'instruction de maintient en fonctionnement n'est pas envoyée
MOTORS = set("forward down frontT backT".split()) # noms des moteurs (commandes) pris en compte

# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
code_ok_noContent = 204 # code de réussite
code_badRequest = 400 # code d'erreur en cas de mauvaise requête du navigateur
code_serviceUnavailable = 503 # code d'erreur en cas de surchage du serveur

maxQueueSize = 4 # nombre de requêtes en attentes au delà duquel les requêtes sont refusées

commandQueue = mp.Queue(maxsize=maxQueueSize) # file des actions reçues par le serveur et en attente de traitement


class BaseActionHandler(ABC):
    @abstractmethod
    def forward(self, value):
        pass
    
    @abstractmethod
    def down(self, value):
        pass

    @abstractmethod
    def frontT(self, value):
        pass
    
    @abstractmethod
    def backT(self, value):
        pass

class DummyActionHandler(BaseActionHandler):
    forward, down, frontT, backT = [nop] * 4

class ActionHandler_tell(BaseActionHandler):
    def forward(self, value):
        printIDFLY("  forward: {}".format(value))
    
    def down(self, value):
        printIDFLY("  down: {}".format(value))

    def frontT(self, value):
        printIDFLY("  frontT: {}".format(value))
    
    def backT(self, value):
        printIDFLY("  backT: {}".format(value))


def serve_with_action_handler(port, host, ActionHandler=DummyActionHandler): # action est l'action qu'on veut voir effectuée avec les informations de POST
    """Fonction serveur"""
    
    actionHandler = ActionHandler()

    class HTTPRequestHandler(SimpleHTTPRequestHandler):
        log_message = nop # on redéfinit la fonction log_message

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
            
            printIDFLY("POST / {}".format(code))
            self.send_response(code) # envoi du code de réponse
            self.end_headers() # envoi de la réponse (fin)

    def serve():
        server_address = (host, port)
        http_server = HTTPServer(server_address, HTTPRequestHandler)
        printIDFLY("Starting http server on port {port}".format(port=port))
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        printIDFLY("Stoping http server")

    def queueRunner():
        """Thread recevant les informations transmise par le serveur et appelant les méthodes correspondantes"""
        for motor in MOTORS:
            assert hasattr(actionHandler, motor), motor
        dummyTimer = threading.Timer(0, nop)
        motorThreads = dict((motor, dummyTimer) for motor in MOTORS)
        while True:
            command = commandQueue.get() # appel généralement blocant
            for key, value in command.items():
                action = getattr(actionHandler, key) # Get the method (forward, ...)

                motorThreads[key].cancel() # Cancel scheduled motor stop

                # The motor should be stopped after AUTO_CANCEL_TIMING
                if value != 0:
                    val = 0
                    thread = threading.Timer(AUTO_CANCEL_TIMING, action, args=[val])
                    motorThreads[key] = thread
                    thread.start()

                # Do the action (if it isn't just a keep request)
                isKeepRequest = value is None
                if not isKeepRequest:
                    action(value)
                    time.sleep(0.05)
    
    pqr = mp.Process(target=queueRunner) # nouveau process : execution des commandes dans la file d'attente
    pqr.start() # démarrage du process pqr (Process Queue Runner)
    serve()     # démarrage du serveur
    pqr.join()  # fin du process pqr