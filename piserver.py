#https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

import os
import time
import multiprocessing as mp
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

import json
import re

VAL_MOTEUR_MIN = -100 # valeur minimale de commande prise en compte
VAL_MOTEUR_MAX = 100 # valeur maximale de commande prise en compte
COMMANDS = set("forward down frontT backT".split()) # noms des commandes pris en compte
code_ok_noContent = 204 #code de réussite
code_error = 400 # code d'erreur
workingDirectory = "../remote" # dossier contenant la page web à envoyer
port = 9000 # port par défaut
host = '' # hote accepté par défaut

commandQueue = mp.SimpleQueue() # file des actions reçues par le serveur et en attente de traitement

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


def nope(*args, **kwargs):
    pass


def action_tell(command):
    '''
    Print les valeurs des 4 moteurs
    :param: command Dictionnaire contenant les valeurs pour les clés à mettre à jour.
    '''
    for key, value in command.items():
        printAREM("  {}: {}".format(key, value))
    time.sleep(0.2) # seconds


def serve_with_action_handler(port=port, host=host, action=nope): # action est l'action qu'on veut voir effectuée avec les informations de POST
    ''' fonction serveur '''
    class Handler(SimpleHTTPRequestHandler):
        log_message = nope # on rédéfinit la fonction log_message

        def do_POST(self):
            content_length = int(self.headers['Content-Length']) # longueur du body
            post_body = self.rfile.read(content_length).decode("utf-8") #body
            
            body = json.loads(post_body)
            ok = isinstance(body, dict) # json peut renvoyer plein de trucs, mais on attend un dict
            ok = ok and body.keys() <= COMMANDS # on regarde si les clefs reçues sont dans l'ensemble attendu
            ok = ok and all(isinstance(val, int) and VAL_MOTEUR_MIN <= val <= VAL_MOTEUR_MAX for val in body.values()) # (...for...) est un générateur, all s'en sert

            if ok:
                code = code_ok_noContent # code de réussite
            else:
                code = code_error # code d'erreur
            
            printAREM("POST / {}:".format(code))
            self.send_response(code) # envoi du code de réponse
            self.end_headers() # envoi de la réponse (fin)

            if ok:
                command = body
                commandQueue.put(command) # commande ajoutée à la file d'attente

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
            command = commandQueue.get() # Probably blocking
            action(command)
    
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

    serve_with_action_handler(port=port, host=host, action=action_tell) # lancement du serveur
