#!/usr/bin/env python3
"""Cuts the ice slime's Permafrost Eruption sheet (the user's Gemini JPG, 2752 x 1536) into the 7-frame strip (2026-11-08).

  python Animations/IceSlime/permafrost_eruption/source/make_permafrost_eruption_strip.py

The prompt asked for 6 panels (3 x 2) and the generator drew SEVEN: three on the top row and four on the bottom row, in reading order: 1 rest, 2 a second rest-sized pose, 3 about half size, 4 a tiny faceless
ball of ice with a few crystal points, 5 the re-form at about 57% with a tall crown, 6 about 88%, 7 the full-size rest. Same scale logic as the fire eruption: ONE scale per row (the top row from panel 1 = base
350 px, the bottom row from panel 7 = the rest-sized last panel), every panel on its own floor, the base centred on x 256. Output: ../ice_permafrost_eruption_7frame_strip.png, the check picture and the placement
json (the size of every frame against the idle).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "source"))
import ice_cut as ic
ic.build_strip(os.path.join(HERE, "permafrost_eruption_sheet.jpg"), os.path.join(HERE, "..", "ice_permafrost_eruption_7frame_strip.png"), os.path.join(HERE, "..", "ice_permafrost_eruption_check.png"),
               os.path.join(HERE, "..", "ice_permafrost_eruption_7frame_strip.placement.json"), [3, 4], [0, 1, 2, 3, 4, 5, 6], "permafrost_eruption", 12,
               extra={"slideFrame": 4, "note": "7 frames: the shrink plays 1, 2, 3, 4 (the tiny ball), the re-forming plays 4, 3, 5, 6, 7; frame sizes by base width against the idle's 350 px"})
