#!/usr/bin/env python3
"""Writes first-draft hand marks (hand-anchors/3) for the Rogue's strips by finding her two bare fists in every frame.

The Rogue (2026-11-04): the BACK fist (the character's far arm, behind her hip in the idle) holds the DAGGER, the main hand, track "main", drawn
behind the body; the FRONT fist (the near arm, low in front of her thigh) holds the CUTLASS, the off hand, track "off" (offItem kind "other"),
drawn in front of the body with the hand drawn over its grip. Both hands are bare skin, so they are found by colour.

How the hands are found: skin-coloured regions in each frame; the largest is the face, the next two big ones that are away from the face are the
fists; the one further LEFT is the back fist (dagger), the one further right the front fist (cutlass). A hand the colour rule misses is given by
hand in OVERRIDE (animation, frame) -> {"back": (x, y), "front": (x, y)} in px of the 512 px frame. The angle of each item per frame is set in
ANGLES (degrees, 0 = the item points up, clockwise positive = the top leans toward the enemy): the dagger points along the forearm past the fist
(hanging down behind her in the idle, trailing back in the run), the cutlass points up and forward from the low front fist. These are drafts:
check them with preview_marks.py and refine them in hand-anchor-tool.html, or edit ANGLES here and run it again.

NOTE (2026-11-04): the user made the real marks by hand in the tool and swapped the tracks (cutlass = main/behind at the front fist, dagger = off/in front at the back
fist, dagger Length 0.33); those are the files next to the strips. This script only makes first drafts (it never overwrites real marks).

  python make_rogue_marks.py [animation ...]   (writes Animations/Rogue/<animation>/source/<strip>.hand-anchors.draft.json;
                                                 add --promote to write the marks next to the strip as <strip>.hand-anchors.json, unless it exists)

Needs pillow, numpy and scipy.
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAR = "Rogue"
FIST = 0.045                                                   # radius of the hand search circle, share of the frame width
DAGGER = dict(length=0.22, pivot=0.73, overlay=False, picture="dagger")
CUTLASS = dict(kind="other", picture="cutlass", length=0.32, pivot=0.82, overlay=True)

# animation folder -> strip file, the dagger angle per frame, the cutlass angle per frame
ANIMS = {
    # standing: the dagger hangs behind her with its blade pointing down and back (215 degrees), so it is not hidden by her thigh; the cutlass points up and forward
    "idle":  ("cloaked_idle_strip.png",         [215, 215, 215, 215, 215, 215], [48, 48, 48, 48, 48, 48]),
    "hit":   ("cloaked_hit_6frame_strip.png",   [215, 240, 225, 218, 215, 215], [48, 70, 52, 48, 48, 48]),
    "death": ("cloaked_death_6frame_strip.png", [215, 215, 235, 250, 330, 90],  [48, 48, 70, 80, 15, 95]),
    "dodge": ("cloaked_dodge_6frame_strip.png", [215, 215, 220, 220, 215, 215], [48, 48, 48, 48, 48, 48]),
    # run: eight frames since 2026-11-04 (the six poses, then the early and the mid stance again: 1 2 3 4 5 6 2 3); the six-frame version is kept in run/source/six_frame_version/
    "run":   ("cloaked_run_8frame_strip.png",   [-125] * 8, [50] * 8),
}
# a hand the colour rule misses or mixes up: (animation, frame) -> {"back": (x, y) or None, "front": (x, y) or None} in px of the 512 px frame
# (give only the one that needs it; None = that hand is hidden behind the body, its item is hidden on that frame)
OVERRIDE = {("death", 6): {"back": None, "front": (255, 450)}}      # lying flat: only the near fist (the cutlass) shows, the far hand is under her

def skin(frame):
    r, g, b, a = [frame[..., i] for i in range(4)]
    return (a > 200) & (r > 140) & (r < 245) & (g > 90) & (g < 180) & (b > 40) & (b < 135) & (r > g + 22) & (g > b + 10)

def hands_in(frame):
    s = skin(frame)
    lab, n = ndi.label(ndi.binary_closing(s, iterations=1))
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) >= 80:
            comps.append(dict(area=len(ys), cx=float(xs.mean()), cy=float(ys.mean()), y0=int(ys.min())))
    comps.sort(key=lambda c: -c["area"])
    if not comps:
        return [], None
    face = comps[0]
    big = [c for c in comps[1:] if c["area"] >= 120 and (c["cx"] - face["cx"]) ** 2 + (c["cy"] - face["cy"]) ** 2 > 40 ** 2][:2]
    big.sort(key=lambda c: c["cx"])
    return big, face

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    promote = "--promote" in sys.argv
    for folder, (strip_name, dag_a, cut_a) in ANIMS.items():
        if args and folder not in args:
            continue
        path = ROOT / "Animations" / "Rogue" / folder / strip_name
        im = np.array(Image.open(path).convert("RGBA")).astype(int)
        H = im.shape[0]
        n = im.shape[1] // 512
        main, off = [], []
        for k in range(n):
            hs, face = hands_in(im[:, 512 * k:512 * (k + 1)])
            ov = OVERRIDE.get((folder, k + 1), {})
            hide_back = "back" in ov and ov["back"] is None
            hide_front = "front" in ov and ov["front"] is None
            back = {"cx": ov["back"][0], "cy": ov["back"][1]} if ov.get("back") else (hs[0] if len(hs) >= 1 else None)
            front = {"cx": ov["front"][0], "cy": ov["front"][1]} if ov.get("front") else (hs[-1] if len(hs) >= 2 else None)
            note = []
            if back is None and not hide_back:
                note.append("BACK FIST NOT FOUND")
            if front is None and not hide_front:
                note.append("FRONT FIST NOT FOUND")
            if hide_back:
                note.append("dagger hidden (far hand under her)")
            if hide_front:
                note.append("cutlass hidden")
            back = back or {"cx": 256, "cy": 300}
            front = front or {"cx": 330, "cy": 300}
            main.append({"x": round(back["cx"] / 512, 3), "y": round(back["cy"] / H, 3), "a": dag_a[k], "front": False, "hide": bool(hide_back), "w": 1})
            off.append({"x": round(front["cx"] / 512, 3), "y": round(front["cy"] / H, 3), "a": cut_a[k], "front": True, "hide": bool(hide_front), "w": 1})
            print(folder, k + 1, "blobs", [(h["area"], round(h["cx"]), round(h["cy"])) for h in hs], "back (%.0f, %.0f) front (%.0f, %.0f)" % (back["cx"], back["cy"], front["cx"], front["cy"]), " ".join(note))
        stem = strip_name[:-len(".png")]
        doc = {"format": "hand-anchors/3",
               "note": "Draft marks made by source/tools/make_rogue_marks.py. Two tracks per frame: main (the far arm, the back fist: the dagger, drawn behind the body) and off (the near arm, the front fist: the cutlass, offItem kind other, drawn in front with the hand over its grip). x and y are fractions of one frame from its top left. a is degrees, 0 = item points up, clockwise is positive. front=false means the item is drawn behind the body. hide=true means no item on that frame.",
               "characters": [{"name": CHAR, "fist": FIST,
                               "items": {"main": {"length": DAGGER["length"], "pivot": DAGGER["pivot"], "overlay": DAGGER["overlay"], "picture": DAGGER["picture"]},
                                         "off": {"length": CUTLASS["length"], "pivot": CUTLASS["pivot"], "overlay": CUTLASS["overlay"], "picture": CUTLASS["picture"]}},
                               "animations": [{"name": stem[:-len("_strip")] if stem.endswith("_strip") else stem, "frames": n, "columns": n, "fps": 10,
                                               "offItem": dict(CUTLASS),
                                               "tracks": {"main": main, "off": off}}]}]}
        text = json.dumps(doc, indent=None, separators=(", ", ": "))
        out = path.parent / "source" / (stem + ".hand-anchors.draft.json")
        out.parent.mkdir(exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))
        if promote:
            real = path.parent / (stem + ".hand-anchors.json")
            if real.exists():
                print("  not promoted: the marks", real.name, "exist already")
            else:
                real.write_text(text, encoding="utf-8")
                print("  promoted to", real.relative_to(ROOT))
