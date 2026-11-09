#!/usr/bin/env python3
"""Makes a PLACEHOLDER backstab strip (6 frames) out of the Rogue's other animations, so the backstab mechanics in the test page can be tried before the real
frames are generated (the prompt is backstab_gemini_prompt.txt next to this file). The marks of each placeholder frame are copied from the same frame of its
source animation (the user's own marks), so the dagger and the cutlass show too.

  frame 1 gather      <- dodge 2   (knees bent)
  frame 2 dissolve    <- dodge 5   (deep landing crouch)
  frame 3 emerge      <- hit 4     (low, leaning forward)
  frame 4 strike      <- run 1     (the wide diagonal of the arms: the strike arm forward)  = the hit frame
  frame 5 follow      <- run 2
  frame 6 recover     <- idle 1

Writes Animations/Rogue/umbral_shroud/cloaked_umbral_shroud_6frame_strip.png, its .hand-anchors.json and its .placement.json (fps 12, hit frame 4).
Delete the three files when the real strip is cut (same names).
"""
import json
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "Animations" / "Rogue"
SRC = {"dodge": ("dodge", "cloaked_dodge_6frame_strip"), "hit": ("hit", "cloaked_hit_6frame_strip"), "run": ("run", "cloaked_run_8frame_strip"), "idle": ("idle", "cloaked_idle_strip")}
PICK = [("dodge", 2), ("dodge", 5), ("hit", 4), ("run", 1), ("run", 2), ("idle", 1)]
NAME = "cloaked_umbral_shroud_6frame_strip"

strips, marks = {}, {}
for k, (folder, stem) in SRC.items():
    strips[k] = Image.open(R / folder / (stem + ".png")).convert("RGBA")
    marks[k] = json.load(open(R / folder / (stem + ".hand-anchors.json"), encoding="utf-8"))
out = Image.new("RGBA", (512 * len(PICK), 512), (0, 0, 0, 0))
main, off = [], []
for i, (k, f) in enumerate(PICK):
    s = strips[k]
    assert s.size[1] == 512, "expects 512 px high strips"
    out.alpha_composite(s.crop(((f - 1) * 512, 0, f * 512, 512)), (i * 512, 0))
    tr = marks[k]["characters"][0]["animations"][0]["tracks"]
    main.append(tr["main"][f - 1]); off.append(tr["off"][f - 1])
out.save(R / "umbral_shroud" / (NAME + ".png"))

doc = json.loads(json.dumps(marks["idle"]))
an = doc["characters"][0]["animations"][0]
an["name"] = NAME[:-len("_strip")]
an["frames"] = an["columns"] = len(PICK)
an["tracks"] = {"main": main, "off": off}
doc["note"] = "PLACEHOLDER marks: copied frame by frame from the Rogue's other animations (see make_placeholder_backstab.py). Replace with marks made in the hand tool for the real strip."
(R / "umbral_shroud" / (NAME + ".hand-anchors.json")).write_text(json.dumps(doc, ensure_ascii=False, separators=(", ", ": ")), encoding="utf-8", newline="\n")

pl = {"format": "frame-placement/1", "animation": "attack", "file": NAME + ".png", "frames": len(PICK), "fps": 12, "hitFrame": 4, "smooth": True,
      "x": [0] * len(PICK), "y": [0] * len(PICK),
      "note": "The backstab plays in place (x and y all 0): the page moves her itself (it dissolves her at home, brings her behind the target, mirrored, and back). It carries the fps (12) and the hit frame (4, the strike). PLACEHOLDER strip until the real frames are cut."}
(R / "umbral_shroud" / (NAME + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")
print("wrote the placeholder strip, marks and placement in", R / "umbral_shroud")
