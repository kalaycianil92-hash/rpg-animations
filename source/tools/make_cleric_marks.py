#!/usr/bin/env python3
"""Writes DRAFT hand marks (hand-anchors/3) for the Cleric's strips: the far fist holds the MACE (or the wand: the page swaps the picture on the same marks).

The Cleric (2026-11-22): the FAR fist (the weapon hand, the arm that comes out from behind his torso, the right-hand fist in the guard stance) is track "main",
the item drawn BEHIND the body, named "mace" (the page's "Cleric's main hand carries" select swaps it for the wand: same marks, other picture and settings). The near fist
(shield or orb) has no item yet (the near item is a later step: offItem kind "none"); the user can add it in hand-anchor-tool.html.

Where the fists are: found by colour for idle, hit, dodge, death, run and block (the rightmost fist-sized skin blob, face and tabard excluded; checked by eye on contact
sheets), and for the six skills the FAR-FIST tables that the page's effects already use (SMITE, PEN, AEG, SIP, JUD, COV in warrior-vs-goblin-test.src.html, measured by eye).
The angle of the item per frame (degrees, 0 = it points up, clockwise positive = the head leans toward the enemy) is a guess from the pose: they are DRAFTS. Check them with
preview_marks.py, then refine them in hand-anchor-tool.html (the hand tool has the mace and the wand in its item list) or edit the tables here and run it again.

  python source/tools/make_cleric_marks.py [animation ...]   writes Animations/Cleric/<animation>/source/<strip>.hand-anchors.draft.json (to look at; compare with preview_marks.py)
                                                              --promote writes <strip>.hand-anchors.json next to the strip INSTEAD (the page and the build read that one), UNLESS it
                                                              exists (the user's own marks are never overwritten). Done 2026-11-22 for all 12 strips; the SAME DAY the user made their own marks in the hand tool
(inbox/Cleric_Animations/hand_marks/) and those replaced these drafts: they are the files next to the strips now, so this script only writes where a file is missing.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHAR = "Cleric"
FIST = 0.05                                                    # radius of the hand circle, share of the frame width (his fists are about 27 px across)
MACE = dict(length=0.3, pivot=0.79, overlay=True, picture="mace")

IDLE_FIST = (390, 243)
IDLE_A = 18
# folder -> (strip file, cell height, far fist (x, y) per frame in px of the 512-wide cell, angle per frame, frames whose hand is hidden)
ANIMS = {
    "idle":  ("mailed_idle_strip.png", 512, [(390, 244), (390, 243), (390, 243), (388, 242), (389, 242), (390, 242)], [18] * 6, []),
    # hit: the fists fly up and out with the blow (frames 2-3), the mace trails them
    "hit":   ("mailed_hit_6frame_strip.png", 512, [(394, 251), (399, 125), (400, 168), (397, 240), (392, 240), (395, 243)], [18, 55, 38, 25, 20, 18], []),
    # dodge: a small hop back, frames 3-4 in the air
    "dodge": ("mailed_dodge_6frame_strip.png", 512, [(385, 238), (391, 232), (386, 189), (402, 201), (377, 260), (385, 237)], [18, 18, 30, 35, 20, 18], []),
    # death: the far fist is thrown back (3-4), lies up on the ground (5); on the last frame he lies flat and the far hand is under him (no mace, like the Rogue's)
    "death": ("mailed_death_6frame_strip.png", 512, [(383, 210), (389, 207), (344, 151), (305, 206), (197, 271), (300, 386)], [25, 30, -20, -60, 10, 90], [6]),
    # run: the far arm swings forward and up (1, 2, 5, 6) and passes the belly (3, 4); frames 7 and 8 are frames 2 and 3 again
    "run":   ("mailed_run_8frame_strip.png", 512, [(365, 189), (361, 218), (328, 274), (327, 256), (365, 171), (360, 195), (361, 218), (328, 274)], [32, 28, 15, 15, 32, 30, 28, 15], []),
    # block: frames 1 and 6 are the idle's guard, 2-5 the shield guard with the far fist up at the right
    "block": ("mailed_block_6frame_strip.png", 512, [(390, 244), (358, 189), (360, 175), (344, 176), (358, 176), (390, 244)], [18, 25, 25, 25, 25, 18], []),
    # the six skills: the far-fist tables of the page's effects (strip px, the cell is 512 wide; y from the top of the cell)
    "radiant_smite": ("mailed_radiant_smite_7frame_strip.png", 640, [(193, 405), (367, 194), (346, 118), (443, 257), (480, 401), (421, 380), (390, 370)], [225, 15, 25, 105, 125, 60, 50], []),
    "dark_penance": ("mailed_dark_penance_7frame_strip.png", 512, [(368, 294), (312, 450), (311, 450), (442, 295), (458, 143), (407, 218), (389, 243)], [18, 55, 55, 60, 20, 20, 18], []),
    "aegis_of_retribution": ("mailed_aegis_of_retribution_7frame_strip.png", 640, [(390, 370), (432, 470), (448, 243), (353, 134), (395, 409), (367, 367), (390, 370)], [18, 70, 40, 0, 20, 15, 18], []),
    "unholy_siphon": ("mailed_unholy_siphon_7frame_strip.png", 512, [(375, 278), (463, 162), (481, 127), (178, 273), (390, 205), (380, 223), (390, 242)], [20, 50, 55, -70, 30, 20, 18], []),
    "sanctified_judgment": ("mailed_sanctified_judgment_7frame_strip.png", 640, [(384, 416), (360, 194), (376, 157), (436, 385), (434, 349), (370, 357), (390, 370)], [30, 15, 0, 120, 110, 40, 18], []),
    "spiteful_covenant": ("mailed_spiteful_covenant_7frame_strip.png", 640, [(300, 345), (312, 358), (358, 404), (381, 191), (363, 226), (351, 350), (390, 370)], [40, 40, 30, 10, 20, 20, 18], []),
}


def mark(x, y, a, front, hide, H):
    return {"x": round(x / 512, 3), "y": round(y / H, 3), "a": a, "front": front, "hide": bool(hide), "w": 1}


def build(folder):
    strip, H, fists, angles, hidden = ANIMS[folder]
    n = len(fists)
    assert len(angles) == n, (folder, "angles", len(angles), n)
    main = [mark(fists[k][0], fists[k][1], angles[k], False, (k + 1) in hidden, H) for k in range(n)]
    off = [mark(300, 250, 0, True, True, H) for _ in range(n)]                    # the near hand has no item yet: hidden on every frame
    stem = strip[:-len(".png")]
    doc = {"format": "hand-anchors/3",
           "note": "DRAFT marks made by source/tools/make_cleric_marks.py (2026-11-22). main = the far fist: the MACE (the page's select swaps it for the wand), drawn behind the body. off = the near hand, no item yet. "
                   "The positions are found by colour or measured by eye, the angles are guesses from the pose: refine them in hand-anchor-tool.html.",
           "characters": [{"name": CHAR, "fist": FIST,
                           "items": {"main": dict(MACE), "off": {"length": 0.3, "pivot": 0.5, "overlay": False, "picture": "shield"}},
                           "animations": [{"name": stem[:-len("_strip")] if stem.endswith("_strip") else stem, "frames": n, "columns": n, "fps": 10,
                                           "offItem": {"kind": "none", "length": 0.3, "pivot": 0.5, "overlay": False},
                                           "tracks": {"main": main, "off": off}}]}]}
    return strip, stem, json.dumps(doc, indent=None, separators=(", ", ": "))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    promote = "--promote" in sys.argv
    for folder in ANIMS:
        if args and folder not in args:
            continue
        strip, stem, text = build(folder)
        base = ROOT / "Animations" / CHAR / folder
        out = base / "source" / (stem + ".hand-anchors.draft.json")
        if not promote:                                       # (promoting writes the real file only: no duplicate draft next to it)
            out.parent.mkdir(exist_ok=True)
            out.write_text(text, encoding="utf-8", newline="\n")
            print("wrote", out.relative_to(ROOT))
        if promote:
            real = base / (stem + ".hand-anchors.json")
            if real.exists():
                print("  not promoted: the marks", real.name, "exist already")
            else:
                real.write_text(text, encoding="utf-8", newline="\n")
                print("  promoted to", real.relative_to(ROOT))
