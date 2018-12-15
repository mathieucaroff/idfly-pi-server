# Installer le système de télécommande sur Rapbian OS

En cas de problème vous pouvez contacter le développeur initial du projet
Mathieu CAROFF <mathieu.caroff@free.fr> (EI16).

En premier lieu:

1) Installer git, python (3) et pip (de python 3)

```bash
# sudo apt update # Nécéssaire si vous ne l'avez jamais fait
sudo apt install git python3 ipython3 python3-pip
```

2) pi-server

a) Installer les dépendances python

```bash
pip3 install pigpio
```

b) Cloner ce repository

```bash
git clone https://gitlab.emse.fr/IDFLY/pi-server.git ~/pi-server
```

3) Cloner le repository de la télécommande

```bash
git clone https://gitlab.emse.fr/IDFLY/node-remote.git ~/remote
```

4) Suivre les instruction dans README.md pour lancer le serveur

Voici un extrait court de ces instructions:

```bash
sudo pigpio
cd ~/pi-serveur
sudo python3 idfly.py ~/remote 80
```

5) Lancement automatique du serveur au démarrage

Si vous souhaitez que le serveur se lance automatiquement au démarrage, je
recommande de commencer par créer un script contenant les commandes de
lancement. Disons `~/start-idfly.sh`.

Faite ensuite exécuter ce script (avec les droits root) depuis
`~/.config/lxsession/LXDE-pi/autostart` (méthode la plus facile) ou bien
depuis un cron, en utilisant quelquechose comme
`@reboot sudo bash /home/pi/start-idfly.sh`. (Attention, l'environnement
posera souvent des difficulté avec cron. Utiliser
`env -i bash monscript.sh` pour faire des tests avec un environnement vide
et vérifier que ça fonctionne.)

Voir `./startup/idfly-startup.sh` pour un script de lancement, et voir
`./startup/idfly-sestup-startup.sh` pour l'automatisation de l'execution
de ce script avec `~/.config/lxsession/LXDE-pi/autostart`.
