import shutil
import os

from PyInstaller.__main__ import run

def compile(name, source, **additional):
    print(f"Compiling {source} as {name}.exe")
    config = [
        "--log-level=ERROR",
        "--distpath=./build",
        "--workpath=./build_temp",
        "--specpath=./build",
        f"--name={name}",
        "--debug=imports",
        "--onefile",
        source
    ]
    for k, v in additional.items():
        if v is True:
            config.insert(-2, "--" + k.replace("_", "-"))
        else:
            config.insert(0, f"--{k.replace('_', '-')}={v}")

    run(config)

compile("game", "src/__main__.py", windowed=True)
compile("QuaTrythm_Launcher", "src/launcher.py", hide_console="minimize-early")

if os.path.exists("build/charts/"):
    shutil.rmtree("build/charts/")

if os.path.exists("build/assets/"):
    shutil.rmtree("build/assets/")

if os.path.exists("build/user/"):
    shutil.rmtree("build/user/")

shutil.copytree("src/charts/", "build/charts/")
shutil.copytree("src/assets/", "build/assets/")