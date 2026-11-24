#!/usr/bin/env python3
"""Swaps the OLD idle's frames that are baked into other Warrior strips for the NEW idle's frames, and gives those frames the new idle's hand marks (2026-11-24).

WHY: when the new idle (2026-11-23, the near arm nearly still) went in, the strips that END on (or, Static Bash, START with) a pasted copy of the old idle's frame 1 still had the old
picture: the near fist stepped about 4 px and the shield 9 px (its mark moved with the user's new idle marks) at the hand-over from a skill to the idle. The user asked to smooth it.

WHAT IT DOES (idempotent: running it again changes nothing more): the pasted frames are exact copies of the old idle's frames (found by comparing the pictures: IoU 1.0 at no shift;
the table below), so each cell is cleared and the new idle's frame (the same number) is pasted in the same place, and in BOTH marks files of that strip (sword set and shield set) the
two tracks of that frame become copies of the new idle's marks for that frame (the user's own idle marks), so the picture, the sword and the shield all match the idle exactly. The 640 px
tall strip (the Thunderclap Guillotine) has the figure at the bottom (128 px of empty rows on top), so there the y of a mark is (y x 512 + 128) / 640.
The strips' placement files, the other frames and the other marks are untouched.

  python swap_baked_idle_frames.py
"""
import json
import pathlib
import numpy as np
from PIL import Image

W = pathlib.Path(__file__).resolve().parents[2]                      # Animations/Warrior
F = 512
# strip -> the strip frames (1-based) that are copies of the old idle's frame of the same number in the list, as (strip frame, idle frame)
BAKED = {
    "block/armored_block_6frame_strip": [(1, 1), (6, 1)],
    "execute/armored_execute_8frame_strip": [(8, 1)],
    "glacial_blade/armored_glacial_blade_8frame_strip": [(8, 1)],
    "molten_cleave/armored_molten_cleave_8frame_strip": [(8, 1)],
    "sunder_strike/armored_sunder_strike_8frame_strip": [(8, 1)],
    "jump_attack/armored_thunderclap_guillotine_11frame_strip": [(11, 1)],
    "static_bash/armored_static_bash_21frame_strip": [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (21, 1)],
}


def anim(path):
    d = json.load(open(path, encoding="utf-8"))
    return d, d["characters"][0]["animations"][0]


def write(path, d, like):
    text = open(like, encoding="utf-8", newline="").read()
    indent = 1 if text.startswith("{\n") else None
    out = json.dumps(d, indent=indent, ensure_ascii=False) + ("\n" if text.endswith("\n") else "")
    open(path, "w", encoding="utf-8", newline="").write(out)


def main():
    new = Image.open(W / "idle/armored_idle_strip.png").convert("RGBA")
    frames = [new.crop((i * F, 0, (i + 1) * F, F)) for i in range(6)]
    idle_marks = {}
    for suffix in (".hand-anchors.json", ".shield.hand-anchors.json"):
        idle_marks[suffix] = anim(W / ("idle/armored_idle_strip" + suffix))[1]["tracks"]
    for base, pairs in BAKED.items():
        sp = W / (base + ".png")
        strip = Image.open(sp).convert("RGBA")
        h = strip.height
        for k, j in pairs:
            cell = (( k - 1) * F, 0, k * F, h)
            strip.paste((0, 0, 0, 0), cell)                                    # clear the cell (paste of a transparent colour replaces)
            strip.alpha_composite(frames[j - 1], ((k - 1) * F, h - F))         # the idle frame sits at the bottom of the cell (a 640 px cell has 128 empty rows on top)
        strip.save(sp)
        for suffix in (".hand-anchors.json", ".shield.hand-anchors.json"):
            mp = W / (base + suffix)
            d, a = anim(mp)
            for k, j in pairs:
                for tk in ("main", "off"):
                    src = dict(idle_marks[suffix][tk][j - 1])
                    if h != F:
                        src["y"] = round((src["y"] * F + (h - F)) / h, 3)
                    a["tracks"][tk][k - 1] = src
            write(mp, d, mp)
        print("done", base, pairs)


if __name__ == "__main__":
    main()
