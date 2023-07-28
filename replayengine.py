"""Replay Engine (RE for short) macro parser"""

import struct

name = "Replay Engine"

wildcard = "*.re"

class Parser:
    def __init__(self, path):
        self.path = path

    @staticmethod
    def read_f32(f, endianness=False):
        return struct.unpack(f"{'>' if endianness else '<'}f", f.read(4))[0]

    @staticmethod
    def read_i32(f, endianness=False):
        return int.from_bytes(f.read(4), byteorder={True: "big", False: "little"}[endianness])

    @staticmethod
    def read_b8(f):
        return bool.from_bytes(f.read(1), byteorder="little")

    def parse(self):
        macro = {"fps": None, "replay": []}
        with open(self.path, "rb") as f:
            macro["fps"] = self.read_f32(f)
            temp_macro_size = self.read_i32(f)
            macro_size = self.read_i32(f)
            f.read(32 * temp_macro_size)
            
            for i in range(macro_size):
                macro["replay"].append({
                    "frame": self.read_i32(f),
                    "hold": self.read_b8(f),
                    "player": [1, 2][self.read_b8(f)],
                })
                f.read(2)
            
        return macro

