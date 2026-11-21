#!/usr/bin/env python3
"""Cuts the Cleric's three TAILORED VFX sheets (the user's, 2026-11-22, 1254 x 1254, 3 x 3, pure black; prompts in Cleric_vfx_kit/) into source/assets/fx.

  python Animations/Cleric/vfx/source/cut_tailored_sheets.py

Same tool and settings as the earlier glow sheets (source/tools/cut_fx_sheet.py: brightness becomes transparency, the pieces are drawn ADDITIVELY), with --grow 60 (the default 24 keeps only the main body of a piece: it
would drop one of the two ribbons of dd_veil and the scattered feathers, motes, embers and drops).
  holy_judgment_sheet.png : hj_sky, hj_beam, hj_pillar, hj_seal, hj_cross, hj_nimbus, hj_wing, hj_feathers, hj_shock
  dark_drain_sheet.png    : dd_rope, dd_claws, dd_fissure, dd_seal, dd_wisp, dd_implode, dd_smoke, dd_veil, dd_motes
  crimson_pact_sheet.png  : cp_seal, cp_chains, cp_heart, cp_flames, cp_shield, cp_embers, cp_roar, cp_cracked, cp_rain
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FX = os.path.join(ROOT, "source", "assets", "fx")
SHEETS = [("holy_judgment_sheet.png", "hj_sky,hj_beam,hj_pillar,hj_seal,hj_cross,hj_nimbus,hj_wing,hj_feathers,hj_shock"),
          ("dark_drain_sheet.png", "dd_rope,dd_claws,dd_fissure,dd_seal,dd_wisp,dd_implode,dd_smoke,dd_veil,dd_motes"),
          ("crimson_pact_sheet.png", "cp_seal,cp_chains,cp_heart,cp_flames,cp_shield,cp_embers,cp_roar,cp_cracked,cp_rain")]
for sheet, names in SHEETS:
    subprocess.run([sys.executable, os.path.join(ROOT, "source", "tools", "cut_fx_sheet.py"), os.path.join(HERE, "tailored", sheet), FX, "--cols", "3", "--rows", "3",
                    "--min", "40", "--pad", "12", "--grow", "60", "--names=" + names], check=True)
# the two seals are one connected body: the default --grow (24) keeps it clean (--grow 60 pulled in a stray speck of the panel below)
for sheet, names in [("holy_judgment_sheet.png", "-,-,-,hj_seal,-,-,-,-,-"), ("dark_drain_sheet.png", "-,-,-,dd_seal,-,-,-,-,-")]:
    subprocess.run([sys.executable, os.path.join(ROOT, "source", "tools", "cut_fx_sheet.py"), os.path.join(HERE, "tailored", sheet), FX, "--cols", "3", "--rows", "3",
                    "--min", "40", "--pad", "12", "--grow", "24", "--names=" + names], check=True)
