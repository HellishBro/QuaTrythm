pyinstaller ^
    --log-level=ERROR ^
    --distpath=./build ^
    --workpath=./build_temp ^
    --specpath=./build ^
    --name=game ^
    --debug=imports ^
    --onefile --windowed ^
    src/__main__.py