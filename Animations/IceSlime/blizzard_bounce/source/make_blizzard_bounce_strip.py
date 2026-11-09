#!/usr/bin/env python3
"""Cuts the ice slime's Blizzard Bounce sheet (the user's Gemini JPG, 2752 x 1536, 4 x 2 panels) into the 8-frame strip (2026-11-08).

  python Animations/IceSlime/blizzard_bounce/source/make_blizzard_bounce_strip.py

The shared ice cutter (Animations/IceSlime/source/ice_panels.py and ice_cut.py): panels 1, 2, 5, 7, 8 grounded, 3, 4 and 6 at their real height above their row's floor (panel 3, a drop shape with a pointed
bottom, is raised if it would hang below the floor line; the SHADOW ELLIPSE the generator drew under panel 6 in spite of two warnings is a piece LOWER than the body and is dropped), one scale per row (panel 1 =
base 350 px, the bottom row from panel 8, the settle). Output: ../ice_blizzard_bounce_8frame_strip.png, ../ice_blizzard_bounce_check.png and the placement json (hit frame 5).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "source"))
import ice_cut as ic
ic.build_strip(os.path.join(HERE, "blizzard_bounce_sheet.jpg"), os.path.join(HERE, "..", "ice_blizzard_bounce_8frame_strip.png"), os.path.join(HERE, "..", "ice_blizzard_bounce_check.png"),
               os.path.join(HERE, "..", "ice_blizzard_bounce_8frame_strip.placement.json"), [4, 4], [0, 1, 4, 6, 7], "blizzard_bounce", 12, hit_frame=5,
               extra={"note": "frames: 1 rest, 2 crouch, 3 launch, 4 plummet, 5 CRASH (the hit frame), 6 bounce, 7 heavy landing, 8 settle. The page lifts and drops the unit itself; lift = body height above the floor in the cell."})
