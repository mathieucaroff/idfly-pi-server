"""
Le fichier main. L'invoquer avec l'option --help pour en savoir plus.
"""

import os
import subprocess
from sys import argv


from util import printIDFLY, nop
from gpio import IdflyGPIO, DummyIdflyGPIO
from piserver import serve_with_action_handler, BaseActionHandler


argv0 = argv[0] if argv else "idfly.py"
runningAsRoot = os.geteuid() == 0

httpRoot = "../remote" # dossier contenant la page web à envoyer
port = 80 if runningAsRoot else 9000 # port par défaut
host = '' # hôte accepté par défaut ('' == '0.0.0.0' == Tous)

documentation = """
Usage:
 python3 {argv0} [httpRoot [port [host]]]

Serveur python de la raspberry pi pour le projet IDFLY.

  httpRoot defaults to: {httpRoot}
  port defaults to: {port}
  host defaults to: "{host}"
""".format(**locals())

if __name__ == '__main__': # sert à savoir si on est utilisé comme module ou comme programme principal

    if "--help" in argv or "-h" in argv:
        print(documentation)
        exit()

    from socket import gethostname
    onRaspberryPi = gethostname() in ["raspberrypi", "pix"]
    if onRaspberryPi:
        idfly = IdflyGPIO()
    else:
        idfly = DummyIdflyGPIO()

    class ActionHandler_motor(BaseActionHandler):
        def forward(self, value):
            printIDFLY("  forward: {}".format(value))
            idfly.forward(value)

        def down(self, value):
            printIDFLY("  down: {}".format(value))
            idfly.down(value)

        def frontT(self, value):
            printIDFLY("  frontT: {}".format(value))
            idfly.frontT(value)

        def backT(self, value):
            printIDFLY("  backT: {}".format(value))
            idfly.backT(value)

    try:
        httpRoot = argv[1]
        port = int(argv[2])
        host = argv[3]
    except IndexError:
        pass

    try:
        os.chdir(httpRoot)
    except FileNotFoundError:
        printIDFLY("Erreur, le dossier httpRoot (`{}`) n'existe pas.".format(httpRoot))
        exit()

    serve_with_action_handler(
        port=port,
        host=host,
        ActionHandler=ActionHandler_motor
    ) # lancement du serveur
else:
    print("[IDFLY] idfly.py n'est pas supposé être importé, mais uniquement utilisé depuis la console: `(sudo) python3 idfly.py`")
