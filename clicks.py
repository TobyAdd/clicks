import struct
import os
import random
from sys import argv
from pydub import AudioSegment

replay_file = ""
clickpack_folder = ""
output_file = ""

def read_float32(f, endianness):
    [read_f] = struct.unpack(f"{'<' if endianness else '>'}f", f.read(4))
    return read_f

def read_int32(f, endianness):
    return int.from_bytes(f.read(4), {True: "little", False: "big"}[endianness])

def read_bool8(f):
    return bool.from_bytes(f.read(1), byteorder='little')

print("Replay Engine Clickbot by TobyAdd")

for arg in argv[1:]:
    if arg.startswith("-r"):
        replay_file = arg[2:]

    if arg.startswith("-c"):
        clickpack_folder = arg[2:]

    if arg.startswith("-o"):
        output_file = arg[2:]

print("Replay:", replay_file)

with open(replay_file, "rb") as f:
    fps = read_float32(f, True)
    replay_size = read_int32(f, True)
    replay2_size = read_int32(f, True)

    f.read(32 * replay_size)
    
    replay2 = []
    for i in range(replay2_size):
        frame = read_int32(f, True)
        hold = read_bool8(f)
        player = read_bool8(f)
        f.read(2)
        replay2.append({
            "frame": frame,
            "hold": hold,
            "player": player,
        })

print("FPS:", fps)
print("Actions:", len(replay2))

holds = [AudioSegment.from_wav(os.path.join(clickpack_folder, "holds", hold)) for hold in os.listdir(os.path.join(clickpack_folder, "holds"))]
releases = [AudioSegment.from_wav(os.path.join(clickpack_folder, "releases", release)) for release in os.listdir(os.path.join(clickpack_folder, "releases"))]

output = AudioSegment.silent(duration=replay2[-1]['frame'] / fps * 1000 + 3000)

for i, replay in enumerate(replay2):
    print(f"Rendering Actions ({i+1}/{len(replay2)})", end="\r")
    audio = holds[random.randrange(len(holds))] if replay['hold'] == 1 else releases[random.randrange(len(releases))]
    position = replay['frame'] / fps * 1000
    output = output.overlay(audio, position=position)

output.export(output_file, format="mp3", bitrate="320k")
print("\nSaved as", output_file)
