# python -m PyInstaller -F clicks.py --add-data="parsers:parsers" -n "REClickbot"

a="n"
echo "Updated in-app version? (yn) "
read a
if [$a == "n"]
then
	exit 0
fi

echo "Release source code first!"
sleep 5

docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows
docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux

