# python -m PyInstaller -F clicks.py --add-data="parsers:parsers" -n "REClickbot"

docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows

docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux

