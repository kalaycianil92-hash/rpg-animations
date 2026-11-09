#!/usr/bin/env python3
"""Makes a PLACEHOLDER cast animation for the mage so the Firebolt can be built and judged before the real cast sheet exists.

The strip is her idle frame 1 leaned back and forward around her feet (8 frames, 512 x 512), the hand marks move the fist, the orb and the
staff the way the real cast should (staff cocked back, then thrust forward and pointing at the enemy on the release frame, frame 5), and
the placement file keeps her in place (all zeros) with fps 12 and the release on frame 5.

Files written to Animations/Mage/cast/ under the real names, so the real strip and marks simply replace them:
  robed_cast_8frame_strip.png, robed_cast_8frame_strip.hand-anchors.json, robed_cast_8frame_strip.placement.json

  python make_placeholder_cast.py
"""
import json
import math
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "Animations" / "Mage" / "cast"
OUT.mkdir(parents=True, exist_ok=True)
NAME = "robed_cast_8frame"

idle = Image.open(ROOT / "Animations" / "Mage" / "idle" / "robed_idle_strip.png").convert("RGBA").crop((0, 0, 512, 512))
FEET = (293, 470)
LEAN = [0, -3, -5, -9, 12, 9, 3, 0]                         # degrees, clockwise = forward (toward the enemy)
FIST = [(0, 0), (-10, 10), (10, -25), (-30, -55), (95, -45), (85, -30), (30, -5), (0, 0)]      # near fist offsets in px from the idle fist (before the lean)
ORB = [(0, 0), (-5, -20), (0, -45), (0, -75), (60, -35), (55, -30), (15, -10), (0, 0)]
STAFF = [21, 5, -10, -25, 78, 70, 45, 21]                    # staff angle: cocked back, then pointing at the enemy on frame 5

strip = Image.new("RGBA", (512 * 8, 512), (0, 0, 0, 0))
for k, lean in enumerate(LEAN):
    strip.alpha_composite(idle.rotate(-lean, resample=Image.BICUBIC, center=FEET), (512 * k, 0))
strip.save(OUT / (NAME + "_strip.png"))

src = json.load(open(ROOT / "Animations" / "Mage" / "idle" / "robed_idle_strip.hand-anchors.json", encoding="utf-8"))
ch = src["characters"][0]; an = ch["animations"][0]
fist0, orb0 = an["tracks"]["off"][0], an["tracks"]["main"][0]

def rot(x, y, deg):                                          # rotate a point (px) about the feet like the picture, clockwise = forward
    a = math.radians(deg); dx, dy = x - FEET[0], y - FEET[1]
    return FEET[0] + dx * math.cos(a) - dy * math.sin(a), FEET[1] + dx * math.sin(a) + dy * math.cos(a)

def track(base, offs, angles, front, orb):
    out = []
    for k in range(8):
        x, y = base["x"] * 512 + offs[k][0], base["y"] * 512 + offs[k][1]
        x, y = rot(x, y, LEAN[k])
        out.append({"x": round(x / 512, 3), "y": round(y / 512, 3), "a": 0 if orb else angles[k], "front": front, "hide": False, "w": 1})
    return out

doc = {"format": "hand-anchors/3", "note": "PLACEHOLDER marks for the placeholder cast (made by source/tools/dev/make_placeholder_cast.py); replace with marks made in the hand tool.",
       "characters": [{"name": ch["name"], "fist": ch.get("fist", 0.04), "items": ch["items"],
                       "animations": [{"name": NAME, "frames": 8, "columns": 8, "fps": 12, "offItem": an["offItem"],
                                       "tracks": {"main": track(orb0, ORB, [0] * 8, False, True), "off": track(fist0, FIST, STAFF, True, False)}}]}]}
(OUT / (NAME + "_strip.hand-anchors.json")).write_text(json.dumps(doc, separators=(", ", ": ")), encoding="utf-8")

place = {"format": "frame-placement/1", "animation": "attack", "file": NAME + "_strip.png", "frames": 8, "fps": 12, "hitFrame": 5, "smooth": True,
         "x": [0] * 8, "y": [0] * 8,
         "note": "PLACEHOLDER: the cast plays in place (x and y all 0). hitFrame is the RELEASE frame of the cast: the frame on which the projectile leaves the top of the staff."}
(OUT / (NAME + "_strip.placement.json")).write_text(json.dumps(place, separators=(",", ":")), encoding="utf-8")
print("wrote the placeholder cast to", OUT)
