#!/usr/bin/env python3
"""Cuts the ice slime's Glacier Slam sheet (the user's Gemini JPG, 2752 x 1536, 4 x 2 panels) into the 8-frame airborne strip (2026-11-08).

  python Animations/IceSlime/glacier_slam/source/make_glacier_slam_strip.py

The shared ice cutter (Animations/IceSlime/source/ice_panels.py and ice_cut.py): the creatures are found as pieces (the leap's apex, panel 5, stands above the sheet's middle line), the tall crystal of panel 4 that
touched the TOP EDGE of the sheet is repaired, panels 1, 2, 7 and 8 are on the floor and 3 to 6 keep their real height above their row's floor, one scale per row (panel 1 = base 350 px, the bottom row from panel 8 =
the rebound, nearly the rest pose). Output: ../ice_glacier_slam_8frame_strip.png, ../ice_glacier_slam_check.png and ../ice_glacier_slam_8frame_strip.placement.json (the Magma Slam's path: hit frame 7, x as
fractions of the way to the landing spot).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "source"))
import ice_cut as ic
fire = json.load(open(os.path.join(HERE, "..", "..", "..", "Slime", "magma_slam", "fire_magma_slam_8frame_strip.placement.json")))
ic.build_strip(os.path.join(HERE, "glacier_slam_sheet.jpg"), os.path.join(HERE, "..", "ice_glacier_slam_8frame_strip.png"), os.path.join(HERE, "..", "ice_glacier_slam_check.png"),
               os.path.join(HERE, "..", "ice_glacier_slam_8frame_strip.placement.json"), [4, 4], [0, 1, 6, 7], "glacier_slam", 12, hit_frame=7,
               extra={"x": fire["x"], "smooth": True, "xUnit": fire["xUnit"], "note": "The ice slime's Glacier Slam path: the Magma Slam's (it stays home through the crouch, crosses most of the way while rising and at the top, lands at the start of frame 7 = the hit frame, the page slides it home). The height of the leap is drawn in the strip."})
