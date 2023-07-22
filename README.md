# Clickbot for ReplayEngine
This is repo for RE clickbot. [Original RE repo](https://github.com/tobyadd/replayengine)

## Overview
This clickbot is used in ReplayEngine, but if you want you can use it in your own projects.
It's cli-only. Arguments:
```shell
$ ./clicks.py -c"clickpack folder" -r"replay.re" -o"output.flac" \
    -softc300 -hardc0 -end5 # this arguments are optional
```
Bundled binaries available in [releases](https://github.com/tobyadd/clicks).

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

