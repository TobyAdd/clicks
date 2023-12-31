This README is also available in [russian](/README.ru.md) language.

# Clickbot for ReplayEngine
This is repo for RE clickbot. [Original RE repo](https://github.com/tobyadd/replayengine)

## Overview

This clickbot is used in ReplayEngine, but if you want you can use it in your own projects.

```shell
$ ./clicks.py -c="clickpack folder" -r="replay.re" -o="output.flac" \
    -s=300 -h=-1 -e=5 # this arguments are optional
```
Bundled binaries available in [releases](https://github.com/tobyadd/clicks).

## Parser system

Clickbot uses a "parser" system. You can add your own parsers by creating `parsername.py`
file in `parser` directory, and add to it:

- **Variable** `name` containing human-readable parser name (e.g. `ReplayEngine`)
- **Variable** `wildcard` containing wildcard for replay file (e.g. `*.re`)
- **Class** `Parser` containing:
  - `__init__` method, with such arguments: (self, path) where:
    - path - path to a file
  - `parse` method returning such hash (dict):<br>
    `{"fps": INT, "replay": [`<br>
    `    {"frame": INT, "hold": BOOL, "player": INT(1,2)},`<br>
    `    ...`<br>
    `]}`<br>

When Clickbot is built with PyInstaller parsers get fusen into the executable and to add/delete
parsers you need to rebuild application. Main parser included with standart distro is ReplayEngine
parser ([replayengine.py](/parsers/replayengine.py)), but not limited to. Feel free to fork repo
and add your own parsers.

## Clickpacks

Here's clickpack format:
```
clickpack/
├─ p1/
│  ├─ softclicks/  # optional
│  │  ├─ holds/
│  │  ├─ releases/
│  ├─ hardclicks/  # optional
│  │  ├─ holds/
│  │  ├─ releases/
│  ├─ holds/
│  ├─ releases/
├─ p2/             # optional
│  ├─ softclicks/  # optional
│  │  ├─ holds/
│  │  ├─ releases/
│  ├─ hardclicks/  # optional
│  │  ├─ holds/
│  │  ├─ releases/
│  ├─ holds/
│  ├─ releases/
```

