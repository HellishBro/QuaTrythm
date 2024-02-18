import os
import sys
from pathlib import Path

def path(*path) -> Path:
    if getattr(sys, 'frozen', False):
        return Path(os.path.join(os.path.dirname(sys.executable), *path))
    else:
        return Path(os.path.join(os.path.dirname(sys.argv[0]), *path))

if os.path.exists(path("__main__.py")):
    args = [sys.executable, path("__main__.py").as_posix()]
elif os.path.exists(path("game.exe")):
    args = [path("game.exe").as_posix()]
else:
    print("Cannot find entry-point")
    print("If you are running in a dev environment, please check if __main__.py exists")
    print("If you are a consumer, please keep the game as game.exe")
    print("Press Ctrl-C to exit...")
    while True:
        pass

error = -1
while error == -1:
    error = os.system(' '.join(args))

    if error == -1:
        print("Error returned. Restarting...")
