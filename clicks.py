#!/usr/bin/env python3

from multiprocessing import Process, Queue, Value
from pydub import AudioSegment
from sys import argv, exit
import fnmatch
import struct
import random
import shutil
import ast
import sys
import os


frozen = False
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    frozen = True

pjoin = os.path.join

class Clickpack:
    def __init__(self, clickpack_folder):
        self.data = self.parse(clickpack_folder)

    @staticmethod
    def parse(clickpack_folder):
        clickpack = {
            "p1": {
                "softclicks": {
                    "holds": [],
                    "releases": [],
                },
                "hardclicks": {
                    "holds": [],
                    "releases": [],
                },
                "holds": [],
                "releases": [],
            },
            "p2": {
                "softclicks": {
                    "holds": [],
                    "releases": [],
                },
                "hardclicks": {
                    "holds": [],
                    "releases": [],
                },
                "holds": [],
                "releases": [],
            },
        }

        # pjoin == os.path.join (see line 9)
        # two players
        
        if not os.path.isdir(clickpack_folder):
            print(f"ERROR: clickpack parsing: no directory {clickpack_folder} found")
            exit(1)

        p2_required = [
            "p2",
            "p2/holds",
            "p2/releases",
            "p2/softclicks/holds",
            "p2/softclicks/releases",
            "p2/hardclicks/holds",
            "p2/hardclicks/releases",
        ]

        nop2 = False
        for i in p2_required:
            if not os.path.isdir(pjoin(clickpack_folder, *i.split("/"))):
                nop2 = True
                print(f"WARN: clickpack parsing: no {i} found in clickpack - defaulting to p1")
                break
            
            sndlist = [i for i in os.listdir(pjoin(clickpack_folder, *i.split("/"))) if i.lower().endswith((".wav", ".mp3", ",ogg", ".flac"))]
            if len(sndlist) == 0:
                nop2 = True
                print(f"WARN: clickpack parsing: no wavs found in {i} - defaulting to p1")
                break

        for p in ("p1",) if nop2 else ("p1", "p2"):
            ########## SOFT|HARD CLICKS ##########
            
            for click_type in ("softclicks", "hardclicks"):
                # no (soft|hard)clicks in clickpack
                if not os.path.isdir(pjoin(clickpack_folder, p, click_type)):
                    print(f"WARN: clickpack parsing: no {p}/{click_type} found, turning it off")
                    clickpack[p][click_type] = None
                    continue
                
                for click_part in ("holds", "releases"):
                    if not os.path.isdir(pjoin(clickpack_folder, p, click_type, click_part)):
                        print(f"WARN: clickpack parsing: {p}/{click_type} does not have {click_part} folder, turning {click_type} off")
                        clickpack[p][click_type] = None
                        break

                    sndlist = [i for i in os.listdir(pjoin(clickpack_folder, p, click_type, click_part)) if i.lower().endswith((".wav", ".mp3", ",ogg", ".flac"))]
                    if len(sndlist) == 0:
                        print(f"WARN: clickpack parsing: no wavs in {p}/{click_type}/{click_part}, turning {click_type} off")
                        clickpack[p][click_type] = None
                        break
    
                    clickpack[p][click_type][click_part] = [AudioSegment.from_file(i, i.split(".")[-1].lower()) for i in map(lambda x: pjoin(clickpack_folder, p, click_type, click_part, x), sndlist)]

            ########## STANDART CLICKS ##########
            for click_part in ("holds", "releases"):
                if not os.path.isdir(pjoin(clickpack_folder, p, click_part)):
                    print(f"ERROR: clickpack parsing: {p} folder must have {click_part} folder")
                    exit(1)

                sndlist = [i for i in os.listdir(pjoin(clickpack_folder, p, click_part)) if i.lower().endswith((".wav", ".mp3", ",ogg", ".flac"))]
                if len(sndlist) == 0:
                    print(f"ERROR: clickpack parsing: there should be at least one wav in {p}/{click_part}")
                    exit(1)

                clickpack[p][click_part] = [AudioSegment.from_file(i, i.split(".")[-1].lower()) for i in map(lambda x: pjoin(clickpack_folder, p, click_part, x), sndlist)]

        if nop2:
            clickpack["p2"] = clickpack["p1"]

        return clickpack

def chop_replay(arr, pieces):
    res = []
    a = len(arr) // pieces
    
    for i in range(pieces):
        res.append(arr[i * a:(i + 1) * a])

    res[-1] += arr[pieces * a:]
    return res

def parse_seconds(time):
    time = round(time)
    s = time % 60
    m = (time // 60) % 60
    h = time // 3600
    return f"{h}:{m}:{s}"

def print_progress_bar(value, max_value, pb_len):
    print(f"[{''.join(['#' if i / pb_len < value / max_value else ' ' for i in range(pb_len)])}], {round(value / max_value * 100):>3}%", end="\r")

if "-v" in sys.argv:
    print("Replay Engine Clickbot")
    print("Authors: TobyAdd and acidgd")
    print("Licensed under MIT license")
    sys.exit(0)

print("REClickbot by TobyAdd && acidgd")

if shutil.which("ffmpeg") is None:
    print(f"No ffmpeg in PATH is found. Download it or add its folder to PATH.")
    exit(1)

dep_args = []

def parse_arg(arg, t, orig, deprecated=None):
    global dep_args

    if arg.startswith(t):

        if orig is not None:
            return orig

        if deprecated is not None and t not in dep_args:
            print(f"WARNING: {t} is deprecated and soon will be removed. use {deprecated} intread")
            dep_args.append(t)
        
        return arg[len(t):]
    
    return orig

replay_file = None
clickpack_folder = None
output_file = None
end_seconds = 3
softclick_delay = -1
hardclick_delay = -1
processes_to_spawn = 12

for arg in argv[1:]:
    replay_file = parse_arg(arg, "-r=", replay_file)
    clickpack_folder = parse_arg(arg, "-c=", clickpack_folder)
    output_file = parse_arg(arg, "-o=", output_file)
    softclick_delay = int(parse_arg(arg, "-softc=", softclick_delay))
    hardclick_delay = int(parse_arg(arg, "-hardc=", hardclick_delay))
    end_seconds = int(parse_arg(arg, "-end=", end_seconds))
    softclick_delay = int(parse_arg(arg, "-s=", softclick_delay))
    hardclick_delay = int(parse_arg(arg, "-h=", hardclick_delay))
    end_seconds = int(parse_arg(arg, "-e=", end_seconds))
    processes_to_spawn = int(arg[3:]) if arg.startswith("-p=") else processes_to_spawn

required_args = [replay_file, clickpack_folder, output_file]

if any([i is None for i in required_args]):
    print(f"usage: {sys.argv[0]} -r=\"<*.re>\" -c=\"<*>\" -o=\"<*.(mp3|wav|ogg|flac|...)>\" [-s=<-1..inf> -softc=<-1..inf>] [-h=<-1..inf> -hardc=<-1..inf>] [-e=<0..inf> -end=<0..inf>] [-p=<1..inf>] [-v]")
    exit(1)

print(f"Replay: {replay_file}")

########## PARSING ##########

if frozen:
    old_cwd = os.getcwd()
    os.chdir(sys._MEIPASS)

for i in os.listdir("parsers"):
    if i.endswith(".py"):
        parser = getattr(__import__(f"parsers.{i.replace('.py', '')}"), i.replace(".py", ''))

        if fnmatch.fnmatch(replay_file, parser.wildcard):
            break

if frozen:
    os.chdir(old_cwd)

replay = parser.Parser(replay_file).parse()

print(f"Parser: {parser.name} ({os.path.basename(parser.__file__)})")
print(f"FPS: {replay['fps']}")
print(f"Actions: {len(replay['replay'])}")
print(f"Parallel processes: {processes_to_spawn}")

########## GENERATING ##########
last_frame = replay['replay'][-1]["frame"]

duration = (last_frame / replay['fps'] * 1000) + (end_seconds * 1000)

print(f"Duration: {parse_seconds(duration)}")

clickpack = Clickpack(clickpack_folder)

p1_click_delta = 0
p1_last_click = 0

p2_click_delta = 0
p2_last_click = 0

sounds = []

for action in replay['replay']:
    # print_progress_bar(key, len(replay['replay']), os.get_terminal_size()[0] - 9)
    # print(f"Rendering Actions ({i}/{len(replay['replay'])})", end="\r")
    player = action["player"]

    if player == 1:
        p1_click_delta = action["frame"] - p1_last_click

        sound = None
        if softclick_delay != -1 and clickpack.data["p1"]["softclicks"] is not None and p1_click_delta <= softclick_delay:
            sound = random.choice(clickpack.data["p1"]["softclicks"]["holds" if action["hold"] else "releases"])
        elif hardclick_delay != -1 and clickpack.data["p1"]["hardclicks"] is not None and p1_click_delta >= hardclick_delay:
            sound = random.choice(clickpack.data["p1"]["hardclicks"]["holds" if acition["hold"] else "releases"])
        else:
            sound = random.choice(clickpack.data["p1"]["holds" if action["hold"] else "releases"])

        p1_last_click = action["frame"]
    else:
        p2_click_delta = action["frame"] - p2_last_click

        sound = None
        if softclick_delay != -1 and clickpack.data["p2"]["softclicks"] is not None and p2_click_delta <= softclick_delay:
            sound = random.choice(clickpack.data["p2"]["softclicks"]["holds" if action["hold"] else "releases"])
        elif hardclick_delay != -1 and clickpack.data["p2"]["hardclicks"] is not None and p2_click_delta >= hardclick_delay:
            sound = random.choice(clickpack.data["p2"]["hardclicks"]["holds" if acition["hold"] else "releases"])
        else:
            sound = random.choice(clickpack.data["p2"]["holds" if action["hold"] else "releases"])

        p2_last_click = action["frame"]

    position = action["frame"] / replay['fps'] * 1000
    sounds.append((position, sound))

chopped = chop_replay(sounds, processes_to_spawn)

output = AudioSegment.silent(duration=duration)

progress = Value("i", 1)

def write_sound(length, sounds, q, n):
    output = AudioSegment.silent(duration=length)
    
    for pos, snd in sounds:
        print_progress_bar(n.value, length, os.get_terminal_size()[0] - 9)
        n.value += 1
        output = output.overlay(snd, position=pos)

    q.put(output)

processes = []
queues = []

for i in range(processes_to_spawn):
    queues.append(Queue())
    processes.append(Process(target=write_sound, args=(len(sounds), chopped[i], queues[i], progress)))

for i in processes: i.start()

for q in queues: output = output.overlay(q.get(), position=0)

print("\nSaving...")
output.export(output_file, format=output_file.split(".")[-1], bitrate="320k")

