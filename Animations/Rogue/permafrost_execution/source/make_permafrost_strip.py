#!/usr/bin/env python3
"""NOTE 2026-11-05: this makes the FIRST (14-frame) version. It is archived in old_14frame/ (with the user's own hand marks, which replaced this script's drafts); the FINAL 19-frame strip (the first five frames
twice as long) is made from that archive by make_permafrost_19frame.py. Re-running THIS script writes a 14-frame strip into the animation folder next to the final one (the build uses the last by name, the
19-frame one, but delete the 14-frame files from the folder after a re-run).

Builds the Rogue's Permafrost Execution strip (14 frames, 512 x 512 cells) from the user's ChatGPT sheet (rogue_permafrost_sheet_3x2.png, 6 panels), the user's own picture of the
finishing pose (end_pose.png) and the first frame of her idle, and writes its path file and hand marks.

  sheet panel 1 settle   (she straightens out of her stance, eyes closing, the fists coming up)
  sheet panel 2 focus    (the forearms crossed on her chest, eyes closed)
  sheet panel 3 dash     (mid-flight, the arms still crossed, the eyes open)
  sheet panel 4 arrive   (a deep lunge next to the enemy, the arms still crossed)
  sheet panel 5 slash    (the arms thrown apart: the HIT frame)
  end_pose.png  finish   (the user's picture: the lunge, fists low at her sides, held while the X freezes)
  sheet panel 6 retreat  (a back-leap, still facing the enemy)
  idle frame 1           (she is home again)

The strip repeats frames for timing (the pack-and-path attack has one frame time for all): ORDER below (2 x settle, 4 x focus, dash, arrive, slash, 3 x finish, retreat, idle) = 14 frames at
12 fps = 1.17 s; the page's fx follow these frame numbers (settle and focus 1-6: the frost gathers, 7 dash, 8 arrive, 9 slash = the hit, 10-12 the X freezes, 13 retreat, 14 home).
The cut: scale 0.9555 (panel 1 = 408 px tall, like her idle), the standing panels by their feet (middle of the feet at x 293), the lunges by the front toe (x 410, so the arrival, the slash
and the finish share one planted front foot), the airborne ones centred and on the ground line (the path lifts them: y). The end pose is scaled by 1.0447 (her face matched to the sheet's:
the picture was drawn about 9% smaller), then by its front toe like the other lunges.

The marks are DRAFTS made here (the fists found by skin colour on the cut frames, found once by hand: the dict FISTS below); the user's convention: main = the cutlass in the FRONT fist,
off = the dagger in the REAR fist; the angles are in ANG (0 = up, clockwise positive). Refine them in the hand tool; do not re-run this over marks the user made (the marks file is
only written when it does not exist, or with --marks).

  python make_permafrost_strip.py [--marks]
"""
import copy
import json
import pathlib
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "Animations" / "Rogue"
D = R / "permafrost_execution"
S = D / "source"
NAME = "cloaked_permafrost_execution_14frame_strip"
SLICE = ROOT / "source" / "tools" / "slice_keypose_sheet.py"
FPS = 12
# source ids: s1..s6 = the sheet's panels, e = the end pose, i = the idle's first frame
ORDER = ["s1", "s1", "s2", "s2", "s2", "s2", "s3", "s4", "s5", "e", "e", "e", "s6", "i"]
HIT = 9
X = [0, 0, 0, 0, 0, 0, 0.5, 1, 1, 1, 1, 1, 0.5, 0]
Y = [0, 0, 0, 0, 0, 0, 0.1, 0, 0, 0, 0, 0, 0.08, 0]
# fists found on the cut frames (px in the 512 cell): (rear fist, front fist)
FISTS = {"s1": ((306, 200), (358, 214)), "s2": ((283, 170), (333, 168)), "s3": ((323, 224), (369, 238)), "s4": ((275, 253), (323, 264)),
         "s5": ((117, 311), (433, 317)), "s6": ((84, 334), (282, 296)), "e": ((172, 412), (415, 407))}
# item angles: (cutlass at the front fist, dagger at the rear fist, cutlass in front of the body, dagger in front of the body)
ANG = {"s1": (40, -70, False, True), "s2": (215, 145, True, True), "s3": (205, 155, True, True), "s4": (215, 145, True, True),
       "s5": (105, -105, True, True), "s6": (110, -115, True, True), "e": (115, -115, True, True)}

cut_png, end_png = S / "permafrost_6panel_cut.png", S / "permafrost_endpose_cut.png"
subprocess.check_call([sys.executable, str(SLICE), str(S / "rogue_permafrost_sheet_3x2.png"), str(cut_png), "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "panel1",
                       "--modes", "feet,feet,center,toe,toe,center", "--feet-x", "293", "--toe-x", "410"])
subprocess.check_call([sys.executable, str(SLICE), str(S / "end_pose.png"), str(end_png), "--cols", "1", "--rows", "1", "--height", "304", "--modes", "toe", "--toe-x", "410"])
cut = Image.open(cut_png).convert("RGBA")
end = Image.open(end_png).convert("RGBA")
idle = Image.open(R / "idle" / "cloaked_idle_strip.png").convert("RGBA")
src = {"s%d" % (k + 1): cut.crop((k * 512, 0, (k + 1) * 512, 512)) for k in range(6)}
src["e"] = end
src["i"] = idle.crop((0, 0, 512, 512))
strip = Image.new("RGBA", (512 * len(ORDER), 512), (0, 0, 0, 0))
for i, k in enumerate(ORDER):
    strip.alpha_composite(src[k], (i * 512, 0))
strip.save(D / (NAME + ".png"))
a = np.array(strip)[..., 3] > 128
print("wrote", NAME + ".png", strip.size, "frames", len(ORDER))

pl = {"format": "frame-placement/1", "animation": "attack", "file": NAME + ".png", "frames": len(ORDER), "fps": FPS, "hitFrame": HIT, "moveFrom": 7, "smooth": True, "x": X, "y": Y,
      "note": "Permafrost Execution (2026-11-05): frames 1-2 settle and 3-6 focus at home (hands crossed on her chest, eyes closed; the frost gathers), 7 the dash (half way: x 0.5, a small arc), 8 the arrival (x 1 = 0.8 character widths in front of the target), 9 the SLASH (the hit: the arms burst apart, the X), 10-12 the finishing pose (the X freezes), 13 the retreat (x 0.5), 14 home in the idle stance. x is a share of the way to the strike point, y an arc in character widths. 12 fps makes it 1.17 s."}
(D / (NAME + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")

marks_path = D / (NAME + ".hand-anchors.json")
if marks_path.exists() and "--marks" not in sys.argv:
    print("marks exist, not overwritten (use --marks to rewrite the drafts)")
else:
    idle_doc = json.load(open(R / "idle" / "cloaked_idle_strip.hand-anchors.json", encoding="utf-8"))
    ch = copy.deepcopy(idle_doc["characters"][0])
    ia = ch["animations"][0]
    idle_main, idle_off = copy.deepcopy(ia["tracks"]["main"][0]), copy.deepcopy(ia["tracks"]["off"][0])
    main, off = [], []
    for k in ORDER:
        if k == "i":
            main.append(copy.deepcopy(idle_main)); off.append(copy.deepcopy(idle_off)); continue
        rear, front = FISTS[k]
        ca, da, cf, df = ANG[k]
        main.append({"x": round(front[0] / 512, 3), "y": round(front[1] / 512, 3), "a": ca, "front": cf, "hide": False, "w": 1})
        off.append({"x": round(rear[0] / 512, 3), "y": round(rear[1] / 512, 3), "a": da, "front": df, "hide": False, "w": 1})
    ia["name"] = NAME[:-len("_strip")]
    ia["frames"] = ia["columns"] = len(ORDER)
    ia["fps"] = FPS
    ia["tracks"] = {"main": main, "off": off}
    doc = {"format": "hand-anchors/3", "note": "Draft marks made by Animations/Rogue/permafrost_execution/source/make_permafrost_strip.py in the user's convention: main = the cutlass in the front fist, off = the dagger in the rear fist, both visible in every frame (the last frame is the idle's). Refine in the hand tool.", "characters": [ch]}
    marks_path.write_text(json.dumps(doc, separators=(", ", ": ")), encoding="utf-8", newline="\n")
    print("wrote the draft marks")
