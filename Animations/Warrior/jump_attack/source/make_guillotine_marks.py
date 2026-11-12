#!/usr/bin/env python3
"""DRAFT hand marks and the placement file for the new Thunderclap Guillotine strip (2026-11-12).

The fists were picked by eye on gridded 3x zoom crops of every frame (cell coordinates in px, cells 512 x 640); the blade angles are mine (a = degrees, 0 = the blade
points up, clockwise is positive). near = the arm in front (the "off" track, drawn in front of the body), far = the arm behind (the "main" track, drawn behind).
Frame 11 is the idle's first frame, so its marks are the idle's (moved down 128 px into the tall cell). The user refines everything in hand-anchor-tool.html.

Writes next to the strip:
  armored_thunderclap_guillotine_11frame_strip.hand-anchors.json   (hand-anchors/3)
  armored_thunderclap_guillotine_11frame_strip.placement.json      (frame-placement/1: fps 14, hit frame 7, holds, the path)

  NOTE 2026-11-13: the user's OWN marks and path are filed now (from inbox/warrior_armored_thunderclap_guillotine_11frame.json and ...placement.json, made in the hand tool and in the page's
  frame position tool); my drafts are kept in this folder as *.DRAFT-claude.json. The script therefore writes nothing unless a file is missing or you pass --marks / --placement
  (do not: they would overwrite the user's work).
  python make_guillotine_marks.py                       (writes only what is missing)
  python make_guillotine_marks.py --marks --placement   (rewrites both drafts)
"""
import json
import pathlib

D = pathlib.Path(__file__).resolve().parent.parent
STEM = "armored_thunderclap_guillotine_11frame_strip"
W, H = 512, 640

# frame: (near fist x, y, a), (far fist x, y, a)
FISTS = {
    1:  ((220, 435, -25), (357, 428, 20)),     # crouch, charging: blades up and a little apart
    2:  ((220, 435, -25), (357, 428, 20)),
    3:  ((240, 277, -12), (363, 287, 12)),     # launch: fists at the shoulders, blades straight up
    4:  ((255, 247, -18), (313, 238, 14)),     # rising arch: fists above the head
    5:  ((207, 305, -20), (238, 287, 8)),      # APEX ARCH: fists above and behind the head, blades up and splayed (the thunderbolt strikes their tips)
    6:  ((262, 173, -14), (305, 177, 12)),     # plunge: fists high above the head
    7:  ((393, 437, 118), (418, 433, 112)),    # STRIKE: both fists together at the front, blades along the arms, forward and down
    8:  ((433, 478, 125), (457, 473, 120)),    # strike landed
    9:  ((335, 497, 115), (433, 495, 112)),    # follow-through: fists low by the front knee
    10: ((338, 375, 0), (390, 378, -40)),      # recover: back toward the guard, like the idle
}
# the idle's first frame (Animations/Warrior/idle marks): main (far) x .781 y .350 a -42, off (near) x .545 y .381 a 0, in a 512 frame; the cell here is 128 px taller
IDLE_FAR = (0.781, (0.350 * 512 + 128) / 640, -42)
IDLE_NEAR = (0.545, (0.381 * 512 + 128) / 640, 0)


def mark(x, y, a, front):
    return {"x": round(x, 3), "y": round(y, 3), "a": a, "front": front, "hide": False, "w": 1}


main, off = [], []
for f in range(1, 12):
    if f == 11:
        main.append(mark(IDLE_FAR[0], IDLE_FAR[1], IDLE_FAR[2], False)); off.append(mark(IDLE_NEAR[0], IDLE_NEAR[1], IDLE_NEAR[2], True))
        continue
    near, far = FISTS[f]
    main.append(mark(far[0] / W, far[1] / H, far[2], False))
    off.append(mark(near[0] / W, near[1] / H, near[2], True))

marks = {
    "format": "hand-anchors/3",
    "characters": [{
        "name": "Warrior", "fist": 0.09,
        "items": {"main": {"length": 0.42, "pivot": 0.81, "overlay": True}, "off": {"length": 0.42, "pivot": 0.81, "overlay": True}},
        "animations": [{
            "name": "armored_thunderclap_guillotine_11frame", "frames": 11, "columns": 11, "fps": 14,
            "offItem": {"kind": "other", "length": 0.42, "pivot": 0.81, "overlay": True},
            "tracks": {"main": main, "off": off},
        }],
    }],
}
import sys
if "--marks" in sys.argv or not (D / (STEM + ".hand-anchors.json")).exists():       # never overwrite marks the user may have refined: pass --marks to rewrite the draft
    (D / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n")
else:
    print("hand marks kept (pass --marks to rewrite the draft)")

# timing: the base frame is 1000/14 = 71.4 ms; holds = extra ms per frame at 100% speed
TARGET_MS = [200, 200, 100, 130, 300, 90, 90, 110, 150, 100, 70]     # v2 (2026-11-13): a longer climb (launch 100, rising arch 130) because the jump is now about 2.3 times higher; v3 (2026-11-13): the crouch 300 + 300 ms (was 100 + 100) so a lightning aura can form round him; v4 (2026-11-13): the user: 200 ms per frame (400 in all)
BASE = 1000 / 14
holds = [max(0, round(t - BASE)) for t in TARGET_MS]
place = {
    "format": "frame-placement/1", "animation": "attack", "file": STEM + ".png", "frames": 11, "fps": 14, "hitFrame": 7, "smooth": True,
    "holds": holds,
    "x": [0, 0, 0.03, 0.18, 0.45, 0.75, 1.0, 1.05, 1.08, 1.08, 1.08],
    "y": [0, 0, 0.45, 0.95, 1.35, 0.80, 0.08, 0, 0, 0, 0],               # v2: the apex was 0.62 (the user: "he should jump much higher"), now 1.35 frame widths (1.45 put the blade tips against the HUD bars)
    "note": ("Thunderclap Guillotine (2026-11-12). x: 0 = home, 1 = strike point (target centre minus 0.8 character widths); y: lift in frame widths. holds[i] = extra ms for frame i+1 at 100% speed "
             "(frames 1-2 crouch and charge 100 ms each, the launch 100 and the rising arch 130 ms, the apex arch (frame 5) 300 ms, the plunge 90, the strike (frame 7) 90 ms with the hit at the end, the landing lunge, the follow-through, the recover). "
             "Frame 7 is the swords hitting the target. DRAFT path: tune it in the page's path editor.")
}
if "--placement" in sys.argv or not (D / (STEM + ".placement.json")).exists():       # since 2026-11-13 the filed placement is the USER's own path (made in the page's frame position tool): never overwritten without --placement
    (D / (STEM + ".placement.json")).write_text(json.dumps(place, ensure_ascii=False), encoding="utf-8", newline="\n")
    print("wrote placement")
else:
    print("placement kept (the user's own path; pass --placement to rewrite the draft)")
print("draft holds", holds, "total ms", sum(round(BASE) + h for h in holds))
