"""TasBot macro parser"""

import json

name = "TasBot"
wildcard = "*.json"

class Parser:
    def __init__(self, path):
        self.path = path

    def parse(self):
        macro = {"fps": None, "replay": []}
        orig_macro = json.load(open(self.path))

        macro["fps"] = orig_macro["fps"]
        for i in orig_macro["macro"]:
            if i["player_1"]["click"] != 0:
                macro["replay"].append({
                    "frame": i["frame"], "hold": [None, False, True][i["player_1"]["click"]], "player": 1,
                })
            if i["player_2"]["click"] != 0:
                macro["replay"].append({
                    "frame": i["frame"], "hold": [None, False, True][i["player_2"]["click"]], "player": 2,
                })

        return macro

