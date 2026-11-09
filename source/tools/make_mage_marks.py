#!/usr/bin/env python3
"""Writes first-draft hand marks (hand-anchors/3) for the mage's strips by finding her two hands in every frame.

The mage's hands: the near hand (the character's right) is always a closed fist holding the staff, the far hand
(the character's left) is always open with an orb floating above it. In the file format the far arm is the "main"
track (here: the orb) and the near arm is the "off" track (here: the staff, offItem kind "other").

How the hands are found: skin-coloured regions (hue 6 to 24 degrees) in each frame; the largest is the face, the next
two big ones are the hands, the left one is the near fist and the right one the far hand. The staff angle per frame is
set below (pose by pose); the orb hangs just above the top of the far hand.  These are drafts: open the json in the
Hand Anchor Tool to nudge any frame, or edit ANGLES here and run it again.

  python make_mage_marks.py [animation ...]   (writes Animations/Mage/<animation>/source/<strip>.hand-anchors.draft.json for the four strips;
                                        the marks you made in the tool live next to the strips and are never touched)

Needs pillow, numpy and scipy.
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]
# Item settings (character name, hand size, orb and staff length and grip) are copied from the marks made by hand for her idle, so drafts match them.
_ref = json.load(open(ROOT / "Animations" / "Mage" / "idle" / "robed_idle_strip.hand-anchors.json", encoding="utf-8"))["characters"][0]
CHAR = _ref["name"]
FIST = _ref.get("fist", 0.04)                                  # radius of the hand search circle, share of the frame width
ORB = dict(_ref["items"]["main"])                              # far hand: the orb's picture bottom sits on the mark (just above the hand)
STAFF = dict(_ref["animations"][0]["offItem"])                 # near hand: the staff, the fist drawn over it
# A hand the colour rule misses (in shadow) is given by hand: (animation, frame) -> the fist's centre in px of the 512 px frame. The detected hand is then the far hand.
OVERRIDE_FIST = {("cast", 6): (348, 217)}
# The far hand when the colour rule misses it (run, a fist swung forward): (animation, frame) -> (centre x, centre y, top y) in px of the 512 px frame.
OVERRIDE_FAR = {("run", 3): (370, 225, 213), ("run", 4): (334, 265, 258), ("run", 5): (326, 279, 271)}
ORB_GAP = 6                                                    # px between the top of the far hand and the orb (in a 512 px wide frame)

# animation folder -> strip file, and the staff angle per frame (degrees, 0 = crystal up, clockwise positive = the top leans toward the enemy).
# Standing, the staff leans back across her body (-26): the crystal ends up behind her head, so the shaft never covers her face and never
# runs into the orb. Hit and fall frames swing it further back with the body; the last death frames lay it on the ground.
ANIMS = {
    "idle":  ("robed_idle_strip.png",        [-26, -26, -26, -26, -26, -26]),
    "hit":   ("robed_hit_6frame_strip.png",  [-26, -40, -34, -28, -24, -26]),
    "death": ("robed_death_6frame_strip.png", [-26, -26, -55, -70, -85, -90]),
    "dodge": ("robed_dodge_6frame_strip.png", [-26, -30, -26, -26, -30, -26]),
    # cast: rest, then the staff is cocked back (leaning back keeps the crystal off her face), on the release frame (5) it points at the enemy along the extended arm
    "cast":  ("robed_cast_8frame_strip.png",  [21, -8, -14, -20, 80, 72, 40, 21]),
    # run: the staff stays in the near fist swinging back at her hip, pointing up and back (the far hand, a fist swung forward, carries the orb)
    "run":   ("robed_run_5frame_strip.png",   [-35, -35, -35, -35, -35]),
}

def hands_in(frame):
    r, g, b = [frame[..., i] / 255.0 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0)
    skin = (frame[..., 3] > 200) & (h > 6) & (h < 24) & (s > 0.2) & (s < 0.55) & (mx > 0.72)
    lab, n = ndi.label(ndi.binary_closing(skin, iterations=1))
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) >= 60:
            comps.append(dict(area=len(ys), cx=float(xs.mean()), cy=float(ys.mean()), y0=int(ys.min())))
    comps.sort(key=lambda c: -c["area"])
    face = comps[0]
    big = [c for c in comps[1:] if c["area"] >= 100 and (c["cx"] - face["cx"]) ** 2 + (c["cy"] - face["cy"]) ** 2 > 45 ** 2][:2]   # comps[0] is the face; ears and bits of neck are close to it
    big.sort(key=lambda c: c["cx"])
    return big                                                       # [near fist, far hand] (or just the near fist when the far hand is hidden)

def orb_offset():
    """How the orb was placed in the marks made by hand for the idle, relative to the top of the open hand: the median of (mark - (hand x, hand top))."""
    path = ROOT / "Animations" / "Mage" / "idle" / "robed_idle_strip.png"
    im = np.array(Image.open(path).convert("RGBA")).astype(int)
    H = im.shape[0]
    marks = _ref["animations"][0]["tracks"]["main"]
    dx, dy = [], []
    for k in range(min(len(marks), im.shape[1] // 512)):
        hs = hands_in(im[:, 512 * k:512 * (k + 1)])
        if len(hs) > 1 and marks[k] and not marks[k].get("hide"):
            dx.append(marks[k]["x"] * 512 - hs[1]["cx"]); dy.append(marks[k]["y"] * H - hs[1]["y0"])
    return (float(np.median(dx)), float(np.median(dy))) if dx else (0.0, -ORB_GAP)
ORB_DX, ORB_DY = orb_offset()
print("orb sits %+.0f px sideways and %+.0f px from the top of the open hand (copied from the idle marks)" % (ORB_DX, ORB_DY))

for folder, (strip_name, angles) in ANIMS.items():
    if sys.argv[1:] and folder not in sys.argv[1:]:
        continue                                                  # python make_mage_marks.py cast  = only the named animations
    path = ROOT / "Animations" / "Mage" / folder / strip_name
    im = np.array(Image.open(path).convert("RGBA")).astype(int)
    H = im.shape[0]
    n = im.shape[1] // 512
    main, off = [], []
    for k in range(n):
        hs = hands_in(im[:, 512 * k:512 * (k + 1)])
        ov = OVERRIDE_FIST.get((folder, k + 1))
        if ov:
            hs = [{"cx": ov[0], "cy": ov[1]}] + hs
        ovf = OVERRIDE_FAR.get((folder, k + 1))
        if ovf and len(hs) < 2:
            hs.append({"cx": ovf[0], "cy": ovf[1], "y0": ovf[2]})
        fist = hs[0]
        off.append({"x": round(fist["cx"] / 512, 3), "y": round(fist["cy"] / H, 3), "a": angles[k], "front": True, "hide": False, "w": 1})
        if len(hs) > 1:
            far = hs[1]
            main.append({"x": round((far["cx"] + ORB_DX) / 512, 3), "y": round((far["y0"] + ORB_DY) / H, 3), "a": 0, "front": False, "hide": False, "w": 1})
        else:
            main.append({"x": 0.5, "y": 0.5, "a": 0, "front": False, "hide": True, "w": 1})      # the far hand is hidden behind the body: no orb
        print(folder, k + 1, "fist (%.0f, %.0f)" % (fist["cx"], fist["cy"]), "far hand" if len(hs) > 1 else "far hand hidden: orb hidden")
    doc = {"format": "hand-anchors/3",
           "note": "Draft marks made by source/tools/make_mage_marks.py. Two tracks per frame: main (the far arm: here the orb floating above the open hand) and off (the near arm: here the staff held in the fist, offItem kind other). x and y are fractions of one frame from its top left. a is degrees, 0 = item points up, clockwise is positive. front=false means the item is drawn behind the body. hide=true means no item on that frame.",
           "characters": [{"name": CHAR, "fist": FIST,
                           "items": {"main": {"length": ORB["length"], "pivot": ORB["pivot"], "overlay": ORB["overlay"], "picture": ORB["picture"]},
                                     "off": {"length": STAFF["length"], "pivot": STAFF["pivot"], "overlay": STAFF["overlay"], "picture": STAFF["picture"]}},
                           "animations": [{"name": strip_name[:-len("_strip.png")], "frames": n, "columns": n, "fps": 10,
                                           "offItem": {"kind": STAFF["kind"], "picture": STAFF["picture"], "length": STAFF["length"], "pivot": STAFF["pivot"], "overlay": STAFF["overlay"]},
                                           "tracks": {"main": main, "off": off}}]}]}
    out = path.parent / "source" / (strip_name[:-len(".png")] + ".hand-anchors.draft.json")   # never over the marks you made in the tool
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(doc, indent=None, separators=(", ", ": ")), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
