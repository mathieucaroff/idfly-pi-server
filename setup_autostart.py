#!/usr/bin/python3

runlevels = [2, 3, 4, 5]
description = """
Install the server on the system
Copy the python files to a directory in /opt
Add an executable file in /etc/init.d and symlink(s) in /etc/rc{x}.d, so that the
python server is automatically run as root at startup
""".format(x=runlevels)

serviceName = "idfly"

import os
import sys
import shutil
import random
from pathlib import Path

initdFile = Path("/etc/init.d/" + serviceName)
rcxdFiles = [Path("/etc/rc{x}.d/{sn}".format(x=x, sn=serviceName)) for x in runlevels]
optDir = Path("/opt/" + serviceName)

allFiles = [initdFile, optDir] + rcxdFiles

runningAsRoot = os.geteuid() == 0
if not runningAsRoot:
    print("This script must be run as root.", file=sys.stderr)
    exit(4)

print("Will install files:")
print("*", "\n* ".join(map(str, allFiles)))

if any(f.exists() for f in allFiles):
    print("""Warning: Some files are already installed. They will be reinstalled.""")
    for f in allFiles:
        oldfstr = str(f)
        if f.is_symlink():
            f.unlink()
        elif f.exists():
            dstPath = "/tmp/{dirname}-{sn}-{rdm}".format(
                dirname=f.parent.name,
                sn=serviceName,
                rdm=random.randrange(10**6)
            )
            f.rename(dstPath)

shutil.copytree(
    src=str(Path(__file__).parent),
    dst=str(optDir),
    ignore=shutil.ignore_patterns(".*")
)

initdFile.touch(mode=0o755)
initdFile.write_text("""
#!/bin/sh
### BEGIN INIT INFO
# Provides           idfly
# Default-Start:     {rlvls}
# Short-Description: Serveur du dirigeable ID-FLY
### END INIT INFO

env PWD=/opt/pi-server /usr/bin/python3 /opt/pi-server/idfly.py /opt/remote 80 0.0.0.0
""")

for f in rcxdFiles:
    f.symlink_to(initdFile)

print("Done")