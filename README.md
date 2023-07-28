# Clickbot for ReplayEngine
This is repo for RE clickbot. [Original RE repo](https://github.com/tobyadd/replayengine)

## Overview

This clickbot is used in ReplayBot, but if you want you can use it in your own projects.

```shell
$ ./clicks.py -c"clickpack folder" -r"replay.re" -o"output.flac" \
    -softc300 -hardc-1 -end5 # this arguments are optional
```
Bundled binaries available in [releases](https://github.com/tobyadd/clicks).

## Parser system

Clickbot uses a "parser" system. You can add your own parsers by creating `parsername.py`
file in `parser` directory, and add to it:

- **Variable** `name` containing human-readable parser name (e.g. `ReplayEngine`)
- **Variable** `wildcard` containing wildcard for replay file (e.g. `*.re`)
- **Class** `Parser` containing:
  - `\_\_init\_\_` method, with such arguments: (self, path) where:
    - path - path to a file
  - `parse` method returning such hash (dict):
    `{"fps": INT, "replay": [
        {"frame": INT, "hold": BOOL, "player": INT(1,2)},
        ...
    ]}`

When Clickbot is built with PyInstaller parsers get fusen into the executable and to add/delete

parsers you need to rebuild application. Only parser included with standart distro is ReplayEngine

parser ([replayengine.py](/parsers/replayengine.py)). Feel free to fork repo and add your own parsers.

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

