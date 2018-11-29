# Pi Server

Un serveur http en Python pour Raspberry Pi permettant le contrôle de PWM par des requêtes POST (json).

Ce serveur doit être couplé à un site (HTML/CSS/JS) dont il envera les pages, ce site présentant une interface agréable pour l'utilisateur. Jusqu'à présent nous avons utilisé https://gitlab.emse.fr/IDFLY/node-remote.

## Utilisation

En premier lieu, lancer le service `pigpiod` de `pigpio`, afin de controller les gpios de la carte:

```sh
sudo pigpiod
```

Pour lancer le serveur, utiliser :

```sh
python3 idfly.py
```

### Aide

*Exécutez la commande ci-dessous pour savoir comment invoquer `idfly.py`.*

```sh
python3 idfly.py --help
```

## Résponsabilité associée à chaque fichier

<dl>
<dt>idfly.py</dt>
<dd>Lire les arguments de lancement du script (argv), observer l'environnement et choisir des valeurs par défaut sensées. Rassembler les fonctionnalités des autres fichiers pour créer le système complet.</dd>

<dt>gpio.py</dt>
<dd>Gérer les gpios: la connection au service pigpiod, savoir quel port utiliser, l'initialisation des ports en PWM et passer les consignes de rapport cyclique.</dd>

<dt>pi-server.py</dt>
<dd>Accepter les connections entrantes. Servir les fichiers du dossier httpRoot lorsqu'il s'agit de requêtes GET et recevoir les requêtes POST (json) pour changer les valeurs des PWMs.</dd>

<dt>util.py</dt>
<dd>Rassmebler le code implémentant des fonctionnalités génériques qui ne sont pas propres au projet.</dd>
<dl>

## Fonctionnement de piserver.py

Le fichier piserver.py crée un serveur python en utilisant la classe 'SimpleHTTPRequestHandler' du module http.server de python 3. Cette classe implémente les requêtes GET et HEAD, et envoie en réponse, les fichiers du dossier PWD -- dossier que nous sélectionnons dans le script via la commande os.chdir().

Ainsi, lorsqu'un navigateur se connect en http à la racine du serveur, le fichier index.html est envoyé. De même, toutes les ressources chargées par la page sont envoyées lorsque c'est demandé. Se référer au README du projet remote.js pour le comportement de la page.

Pour recevoir les instructions de commande, le serveur accepte des requêtes POST, qui sont prises en charge par la méthode do_POST. Celle-ci s'assure que le format (json) de la requête est correct et que les données sont valides (validité de tous les nom des champs et de leur valeur). Si la requête est invalide, le code d'erreur 400 est renvoyé. Si la requête est valide, elle est stockée dans une file et le code de confirmation 204 (NoContent) est renvoyé.

Les valeurs présentes dans la file sont consommées par un second processus python crée grâce au module multiprocessing de python. Pour chaque valeur reçue dans la requête, le second processus appelle la méthode correspondante en lui passant en paramètre les instructions reçues, sous forme d'un dictionnaire Python. Actuellement, il s'agit d'une instance de  `ActionHandler_tell` -- un objet qui ne fait qu'afficher les nom des instructions qu'il reçoit. 

Pour chaque moteur, s'il est maintenu actif pendant une seconde sans que le serveur ne reçoive une requête POST le mentionnant, le serveur l'arrête. Le serveur différencie les requêtes d'affectation d'une valeur, des requête utilisées pour demander le maintient de la valeur actuelle.

Les clés utilisées pour transmettre les instructions sont:

* `forward`
* `up`
* `frontT`
* `backT`

Les valeurs acceptées sont des int, compris entre -100 et 100 inclus.

Les commentaires explicatifs du code vous sont gracieusement fournis par Yann, pour un code plus compréhensible de tous, plus ouvert et perrenne.