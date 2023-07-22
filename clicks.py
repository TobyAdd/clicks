#!/usr/bin/env python3

from pydub import AudioSegment
from sys import argv
import struct
import random
import shutil
import ast
import sys
import os

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
            
            wavlist = [i for i in os.listdir(pjoin(clickpack_folder, *i.split("/"))) if i.endswith(".wav")]
            if len(wavlist) == 0:
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

                    wavlist = [i for i in os.listdir(pjoin(clickpack_folder, p, click_type, click_part)) if i.endswith(".wav")]
                    if len(wavlist) == 0:
                        print(f"WARN: clickpack parsing: no wavs in {p}/{click_type}/{click_part}, turning {click_type} off")
                        clickpack[p][click_type] = None
                        break
    
                    clickpack[p][click_type][click_part] = [AudioSegment.from_wav(i) for i in map(lambda x: pjoin(clickpack_folder, p, click_type, click_part, x), wavlist)]

            ########## STANDART CLICKS ##########
            for click_part in ("holds", "releases"):
                if not os.path.isdir(pjoin(clickpack_folder, p, click_part)):
                    print(f"ERROR: clickpack parsing: {p} folder must have {click_part} folder")
                    exit(1)

                wavlist = [i for i in os.listdir(pjoin(clickpack_folder, p, click_part)) if i.endswith(".wav")]
                if len(wavlist) == 0:
                    print(f"ERROR: clickpack parsing: there should be at least one wav in {p}/{click_part}")
                    exit(1)

                clickpack[p][click_part] = [AudioSegment.from_wav(i) for i in map(lambda x: pjoin(clickpack_folder, p, click_part, x), wavlist)]

        if nop2:
            clickpack["p2"] = clickpack["p1"]

        return clickpack

class ReplayParser:
    def __init__(self, path):
        self.fps, self.data = self.parse(path)

    @staticmethod
    def read_float32(f, endianness):
        [read_f] = struct.unpack(f"{'<' if endianness else '>'}f", f.read(4))
        return read_f

    @staticmethod
    def read_int32(f, endianness):
        return int.from_bytes(f.read(4), {True: "little", False: "big"}[endianness])

    @staticmethod
    def read_bool8(f):
        return bool.from_bytes(f.read(1), byteorder='little')

    def parse(self, replay_file):
        with open(replay_file, "rb") as f:
            fps = self.read_float32(f, True)
            replay_size1 = self.read_int32(f, True)
            replay_size = self.read_int32(f, True)

            f.read(32 * replay_size1)
    
            replay = []
            for i in range(replay_size):
                frame = self.read_int32(f, True)
                hold = self.read_bool8(f)
                player = self.read_bool8(f)
                f.read(2)
                replay.append({
                    "frame": frame,
                    "hold": hold,
                    "player": player,
                })

        return fps, replay

def print_progress_bar(value, max_value, pb_len):
    print(f"[{''.join(['#' if i / pb_len < value / max_value else ' ' for i in range(pb_len)])}], {round(value / max_value * 100):>3}%", end="\r")

print("Replay Engine Clickbot by TobyAdd (& acidgd)")

if shutil.which("ffmpeg") is None:
    print(f"No ffmpeg in PATH is found. Download it or add its folder to PATH.")
    exit(1)

def parse_arg(arg, t, orig):
    if arg.startswith(t):
        return arg[len(t):]
    return orig

replay_file = None
clickpack_folder = None
output_file = None
end_seconds = 3
softclick_delay = -1
hardclick_delay = -1

for arg in argv[1:]:
    replay_file = parse_arg(arg, "-r", replay_file)
    clickpack_folder = parse_arg(arg, "-c", clickpack_folder)
    output_file = parse_arg(arg, "-o", output_file)
    softclick_delay = int(parse_arg(arg, "-softc", softclick_delay))
    hardclick_delay = int(parse_arg(arg, "-hardc", hardclick_delay))
    end_seconds = int(parse_arg(arg, "-end", end_seconds))

required_args = [replay_file, clickpack_folder, output_file]

if any([i is None for i in required_args]):
    print(f"usage: {sys.argv[0]} -r\"<*.re>\" -c\"<*>\" -o\"<*.(mp3|wav|ogg|flac|...)>\" [-s<0..inf>] [-h<0..inf>] [-e<0..inf>]")
    exit(1)

print(f"Replay: {replay_file}")

########## PARSING ##########

replay = ReplayParser(replay_file)

print(f"FPS: {replay.fps}")
print(f"Actions: {len(replay.data)}")

########## GENERATING ##########

clickpack = Clickpack(clickpack_folder)

last_frame = replay.data[-1]["frame"]

duration =  last_frame / replay.fps  * 1000  + end_seconds * 1000
#          < length in secs > <to ms> <   add end time   >

output = AudioSegment.silent(duration=duration)

p1_click_delta = 0
p1_last_click = 0

p2_click_delta = 0
p2_last_click = 0

for key, action in enumerate(replay.data, start=1):
    print_progress_bar(key, len(replay.data), os.get_terminal_size()[0] - 9)
    # print(f"Rendering Actions ({i}/{len(replay.data)})", end="\r")
    player = int(action["player"]) + 1

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

    position = action["frame"] / replay.fps * 1000
    output = output.overlay(sound, position=position)

output.export(output_file, format=output_file.split(".")[-1], bitrate="320k")
print(f"\nSaved as {output_file}")

