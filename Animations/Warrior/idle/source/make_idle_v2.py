#!/usr/bin/env python3
"""The Warrior's idle, second version (2026-11-23): cuts source/warrior_idle_sheet_v2.png into ../armored_idle_strip.png, writes its hair mask and its hand marks.

WHY A NEW IDLE: the user said the near arm moved too much (with the shield on it the idle looked wrong). In the first idle (source/old_idle_v1/) the near fist sank by up to 20 px and the
near sword swung 30 degrees between frames. The new sheet (prompt: Warrior_idle_kit/2_paste_this_prompt.txt) keeps the near arm still: measured on the strip its fist moves 4 px at most
(frame 5, the breath out), the far fist 3 px, only the chest, the shoulders, the head and the tips of the hair breathe.

THE MARKS are placed from the user's own marks on the first idle (source/old_idle_v1/*.hand-anchors.json, frame 1 = the rest pose): the same grip point on each fist, moved by how far the
fist skin blob moved between the old frame 1 and the new frame 1 (measured below). The NEAR hand's marks are the SAME in all six frames (so a sword or a shield on it never wobbles),
the FAR hand's follow the fist frame by frame (it moves 3 px at most). The user re-checks them in the hand tool.

  python make_idle_v2.py
"""
import json
import pathlib
import subprocess
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
IDLE = HERE.parent
TOOLS = HERE.parents[3] / "source" / "tools"
SHEET = HERE / "warrior_idle_sheet_v2.png"
STRIP = IDLE / "armored_idle_strip.png"
OLD = HERE / "old_idle_v1"
FRAME = 512


def skin(f):
    r, g, b, al = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
    return (al > 200) & (r > 150) & (r - b > 40) & (g > 80)


def fist(f, cx, cy):
    """the centre (x, y in px) of the skin blob nearest to (cx, cy): a fist"""
    lab, n = ndi.label(skin(f))
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(xs) < 150:
            continue
        d = np.hypot(xs.mean() - cx, ys.mean() - cy)
        if best is None or d < best[0]:
            best = (d, xs.mean(), ys.mean())
    return np.array(best[1:])


def frames(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(int)
    return [a[:, i * FRAME:(i + 1) * FRAME] for i in range(6)]


def main():
    py = sys.executable
    subprocess.run([py, str(TOOLS / "slice_keypose_sheet.py"), str(SHEET), str(STRIP), "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "median", "--modes", "heel", "--heel-x", "160",
                    "--despill-band", "10", "--despill-thr", "4"], check=True)
    subprocess.run([py, str(TOOLS / "hair_mask.py"), str(STRIP), str(IDLE / "armored_idle_strip.hair-mask.png"), "--char", "warrior"], check=True)
    old, new = frames(OLD / "armored_idle_strip.png"), frames(STRIP)
    near_off = fist(new[0], 285, 195) - fist(old[0], 285, 195)                   # how far the near fist moved between the two idles' frame 1
    far_new = [fist(f, 405, 180) for f in new]
    far_off = far_new[0] - fist(old[0], 405, 180)
    print("near fist moved", near_off.round(1), "far fist moved", far_off.round(1), "far fist per frame", [tuple(v.round(1)) for v in far_new])
    # (the SHIELD marks are now the user's own, inbox/warrior_armored_idle.json, 2026-11-23: this script no longer writes them; the marks it derived are kept in derived_shield_marks_2026-11-23.json)
    # (the TWO-SWORD marks too are now the user's own, inbox/warrior_armored_idle_2_weapons.json, 2026-11-23: this script writes no marks any more; the ones it derived are kept in derived_two_sword_marks_2026-11-23.json)
    for fn, near_a in ():
        d = json.load(open(OLD / fn, encoding="utf-8"))
        an = d["characters"][0]["animations"][0]
        m0, o0 = an["tracks"]["main"][0], an["tracks"]["off"][0]                   # the user's marks on the old rest frame
        nx, ny = o0["x"] * FRAME + near_off[0], o0["y"] * FRAME + near_off[1]
        main_t, off_t = [], []
        for i in range(6):
            mx, my = m0["x"] * FRAME + far_off[0] + (far_new[i][0] - far_new[0][0]), m0["y"] * FRAME + far_off[1] + (far_new[i][1] - far_new[0][1])
            main_t.append(dict(m0, x=round(mx / FRAME, 3), y=round(my / FRAME, 3)))
            off_t.append(dict(o0, x=round(nx / FRAME, 3), y=round(ny / FRAME, 3), a=near_a))
        an["tracks"] = {"main": main_t, "off": off_t}
        json.dump(d, open(IDLE / fn, "w", encoding="utf-8"), indent=None)
        print("wrote", fn, "main", [(t["x"], t["y"]) for t in main_t], "off", (off_t[0]["x"], off_t[0]["y"], off_t[0]["a"]))


if __name__ == "__main__":
    main()
