#!/usr/bin/env python3
"""Cuts the holy glow sheet (the user's, Animations/SlimeKing/holy_fx/..., moved to inbox/SPELL VFX/holy_fx_glow_sheet.png, 1254 x 1254, 3 x 3, pure black) into source/assets/fx/hl_*.png for the Cleric's painted layer (2026-11-22).

  python Animations/Cleric/vfx/source/cut_holy_pieces.py

Same tool and settings as the dark slime's glow pieces (Animations/DarkSlime/source/cut_fx_sheets.py): brightness becomes transparency, the pieces are drawn ADDITIVELY.
Names (left to right, top row first): hl_comet, hl_swirl, hl_pillar, hl_halo, hl_veil, hl_flames, hl_star, hl_motes, hl_burst.
The dark pieces (dk_*) already exist in source/assets/fx; the crimson of the Spiteful Covenant is made in code by tinting the gold ones (pcImg in the page), so there is no crimson sheet.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SHEET = os.path.join(HERE, "holy_fx_glow_sheet.png")
if not os.path.exists(SHEET):
    shutil.copy(os.path.join(ROOT, "inbox", "SPELL VFX", "holy_fx_glow_sheet.png"), SHEET)
NAMES = "hl_comet,hl_swirl,hl_pillar,hl_halo,hl_veil,hl_flames,hl_star,hl_motes,hl_burst"
subprocess.run([sys.executable, os.path.join(ROOT, "source", "tools", "cut_fx_sheet.py"), SHEET, os.path.join(ROOT, "source", "assets", "fx"), "--cols", "3", "--rows", "3",
                "--min", "40", "--pad", "12", "--names=" + NAMES], check=True)
