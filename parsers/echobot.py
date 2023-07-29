"""EchoBot macro parser"""

import json

name = "EchoBot"
wildcard = "*.echo"

class Parser:
    def __init__(self, path):
        self.path = path

    def compile_ef_macro(self, macro):
        a = []

        nop2 = len([i for i in macro if i["Player 2"]]) == 0

        if nop2:
            old = macro[0]["Hold"]
            
            for i in macro:
                if i["Hold"] != old:
                    a.append({"frame": i["Frame"], "hold": i["Hold"], "player": 1})
                old = i["Hold"]
        else:
            old1 = [i for i in macro if not i["Player 2"]][0]["Hold"]
            old2 = [i for i in macro if i["Player 2"]][0]["Hold"]
        
            for i in macro:
                if i["Player 2"]:
                    if i["Hold"] != old2:
                        a.append({"frame": i["Frame"], "hold": i["Hold"], "player": 2})
                    old2 = i["Hold"]
                else:
                    if i["Hold"] != old1:
                        a.append({"frame": i["Frame"], "hold": i["Hold"], "player": 1})
                    old1 = i["Hold"]

        return a

    def parse(self):
        macro = {"fps": None, "replay": None}
        orig_macro = json.load(open(self.path))

        macro["fps"] = orig_macro["FPS"]
        macro["replay"] = self.compile_ef_macro(orig_macro["Echo Replay"])

        return macro

