Le fichier pyserver.py crée un serveur python en utilisant la classe 'SimpleHTTPRequestHandler' du module http.server de python 3. Cette classe implémente les requêtes GET et HEAD, et envoie en réponse, les fichiers du dossier PWD -- dossier que nous selectionons dans le script via la commande os.chdir().

Ainsi, lorsqu'un navigateur se connect en http à la racine du serveur, le fichier index.html est envoyé. De même, toutes les ressources chargées par la page sont envoyées lorsque c'est demandé. Se réferer au README du projet remote.js pour le comportement de la page.

Pour reçevoir les instructions de commande, le serveur accèpte des requêtes POST, qui sont prises en charge par la méthode do_POST. Celle-ci s'assure que le format (json) de la requête est correct et que les données sont valides (validité de tous les nom des champs et de leur valeur). Si la requête est invalide, le code d'erreur 400 est renvoyé. Si la requête est valide, elle est stoquée dans une file et le code de confirmation 204 (NoContent) est renvoyé.

Les valeurs présentes dans la file sont consommées par un second processus python crée grâce au module multiprocessing de python. Le second processus appèle la fonction d'action donnée en lui passant en paramètre les instructions reçues, sous forme d'un dictionnaire Python. Actuellement, il s'agit de `action_tell` -- une fonction qui affiche les instruction donnée.

Les clés utilisées pour transmettre les instructions sont:

* `forward`
* `down`
* `frontT`
* `backT`

Les valeurs accéptées sont des int, compris entre -100 et 100 inclus.

Les commentaires explicatifs du code vous sont gracieusement fournis par Yann, pour un code plus compréhensible de tous, plus ouvert et perrenne.