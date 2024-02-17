import shutil
import os

from PyInstaller.__main__ import run

def compile(name, source):
    print(f"Compiling {source} as {name}.exe")
    run((
        "--log-level=ERROR",
        "--distpath=./build",
        "--workpath=./build_temp",
        "--specpath=./build",
        f"--name={name}",
        "--debug=imports",
        "--onefile",
        "--windowed",
        source
    ))

compile("game", "src/__main__.py")
compile("QuaTrythm_Launcher", "src/launcher.py")

if os.path.exists("build/charts/"):
    shutil.rmtree("build/charts/")

if os.path.exists("build/assets/"):
    shutil.rmtree("build/assets/")

if os.path.exists("build/user/"):
    shutil.rmtree("build/user/")

shutil.copytree("src/charts/", "build/charts/")
shutil.copytree("src/assets/", "build/assets/")