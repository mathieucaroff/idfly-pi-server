#!/usr/bin/python3

runlevels = [2, 3, 4, 5]
description = """
Install the server on the system
Copy the python files to a directory in /opt
Add an executable file in /etc/init.d and symlink(s) in /etc/rc{x}.d, so that the
python server is automatically run as root at startup
""".format(x=runlevels)

mainName = "idfly.py"
serviceName = "idfly"
httpRootDirName = "remote"

import os
import sys
import shutil
import random
from pathlib import Path

initdFile = Path("/etc/init.d/" + serviceName)
rcxdFiles = [Path("/etc/rc{x}.d/{sn}".format(x=x, sn=serviceName)) for x in runlevels]
optDirService = Path("/opt/" + serviceName)
optDirHttpRoot = Path("/opt/" + httpRootDirName)

allFiles = [initdFile, optDirService, optDirHttpRoot] + rcxdFiles

runningAsRoot = os.geteuid() == 0
if not runningAsRoot:
    print("This script must be run as root.", file=sys.stderr)
    exit(4)

print("Will install files:")
print("*", "\n* ".join(map(str, allFiles)))

if any(f.exists() for f in allFiles):
    print("""Warning: Some files are already installed. They will be reinstalled.""")
    randomVal = random.randrange(10**6)
    for f in allFiles:
        oldfstr = str(f)
        if f.is_symlink():
            f.unlink()
        elif f.exists():
            dstPath = "/tmp/{randomVal}-{dirname}-{filename}-{sn}".format(
                randomVal=randomVal,
                dirname=f.parent.name,
                filename=f.name,
                sn=serviceName,
            )
            f.rename(dstPath)

currentDir = Path(__file__).parent.absolute() # pylint: disable=no-member
shutil.copytree(
    src=str(currentDir),
    dst=str(optDirService),
    ignore=shutil.ignore_patterns(".*")
)
shutil.copytree(
    src=str(currentDir.parent / httpRootDirName),
    dst=str(optDirHttpRoot),
    ignore=shutil.ignore_patterns(".*")
)

initdFile.touch(mode=0o755)
initdFile.write_text("""
#!/bin/sh
### BEGIN INIT INFO
# Provides           idfly
# Default-Start:     {runlvls}
# Short-Description: Serveur du dirigeable ID-FLY
### END INIT INFO

env PWD="{optDirLocation}" "{pythonLocation}" "{mainLocation}" "{httpRootLocation}" 80 0.0.0.0
""".format(
    runlvls=" ".join(map(str,runlevels)),
    optDirLocation=str(optDirService),
    pythonLocation="/usr/bin/python3",
    mainLocation=str(optDirService / mainName),
    httpRootLocation=str(optDirHttpRoot),
))

for f in rcxdFiles:
    f.symlink_to(initdFile)

print("Done")
