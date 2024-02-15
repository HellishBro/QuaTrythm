import os
import sys
import subprocess
from pathlib import Path

if os.path.exists("__main__.py"):
    args = [sys.executable, (Path(os.path.dirname(sys.argv[0])) / "__main__.py").as_posix()]
elif os.path.exists("game.exe"):
    args = ["game.exe"]
else:
    print("Cannot find entry-point")
    print("If you are running in a dev environment, please check if __main__.py exists")
    print("If you are a consumer, please keep the game as game.exe")
    exit(0xC0000005)

error = 0xC0000005
while error == 0xC0000005:
    with subprocess.Popen(args) as subproc:
        pass

    error = subproc.returncode
    if error == 0xC0000005:
        print("Error 0xC0000005 returned. Restarting...")
