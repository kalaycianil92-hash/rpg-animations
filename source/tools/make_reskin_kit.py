#!/usr/bin/env python3
"""Collects everything needed to send an animation to an image generator into ONE folder per animation: the look's reference picture, the pose-guide sheets (and the single guides the prompts name),
and the prompt files, with the file names inside the prompts changed to the plain names of the files next to them (see docs/RESKIN_PILOT_PLAN.md).

  python source/tools/make_reskin_kit.py                       (rebuilds Assassin_reskin_kit/ from the list KIT below)
  python source/tools/make_reskin_kit.py --look Spellblade --ref Animations/Spellblade/reference_image.png --out Spellblade_reskin_kit

To add an animation: make its guides with make_pose_guides.py (reskin/<Character>_<animation>/), write its prompt file(s) beside them, and add a line to KIT. Re-run it after a prompt, a guide or the
reference changes (the kit is a copy: the files in reskin/ and Animations/ are the real ones, the kit is rebuilt from scratch, the folder is emptied first).
"""
import argparse
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]

# (kit folder, guides folder in reskin/, [(prompt file in the guides folder, name in the kit)], what it is)
KIT = [
    ("01_idle", "Rogue_idle", [("prompt_assassin_sheet.txt", "prompt_sheet.txt"), ("prompt_assassin_single.txt", "prompt_single_one_pose_at_a_time.txt")], "6 idle poses (DONE: the sheet was used; the single-image prompt is the alternative)"),
    ("02_permafrost_execution", "Rogue_permafrost_execution", [("prompt_assassin_sheet.txt", "prompt_sheet.txt"), ("prompt_assassin_single_retreat.txt", "prompt_single_retreat.txt")], "sheet of 6 + the retreat as a single image (DONE)"),
    ("03_run", "Rogue_run", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "6 run poses (DONE)"),
    ("04_hit", "Rogue_hit", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "6 hit poses (DONE)"),
    ("05_death", "Rogue_death", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "6 death poses (DONE)"),
    ("06_dodge", "Rogue_dodge", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "6 dodge poses (DONE; the hop frames 3-4 are the weakest)"),
    ("07_shadow_shiv", "Rogue_shadow_shiv", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "3 poses (DONE; the Static Stiletto only re-uses its stab frame)"),
    ("08_umbral_shroud", "Rogue_umbral_shroud", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "6 poses (DONE)"),
    ("09_abyssal_backstab", "Rogue_abyssal_backstab", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "5 TALL poses, in the air (BUILT from the vertical sheet as a test; regenerate if the emerge or the strike frame looks wrong)"),
    ("10_winters_kiss", "Rogue_dagger_throw", [("prompt_assassin_sheet.txt", "prompt_sheet.txt"), ("prompt_assassin_single_pose4_rogue.txt", "prompt_single_pose4_rogue_reference.txt"), ("prompt_assassin_single_pose5_hands.txt", "prompt_single_pose5_REDRAW_catch.txt")], "5 poses; only pose 5 (the catch) is to be REDRAWN as a single image: the wrong arm catches. prompt_single_pose5_REDRAW_catch.txt + ref_uid04.png (+ reference_image.png). Poses 1-4 are fine (pose 4 was redone earlier)."),
    ("11_static_stiletto", "Rogue_static_stiletto", [("prompt_assassin_sheet.txt", "prompt_sheet.txt")], "6 poses, 3:2 (DONE 2026-11-06: the sheet came out right first time; the Rogue's Spark Streak Stab version; its stab frame comes from the Shadow Shiv, its last frame from the idle; panel 5 is in the air)"),
]

# what the folder holds for a look other than the Assassin (the Assassin's notes above are her progress; the first sheets of a new look are generated fresh)
NEW_LOOK_WHAT = {
    "02_permafrost_execution": "sheet of 6 + the retreat as a single image (the eighth image of the animation is the idle's first frame: nothing to draw)",
    "09_abyssal_backstab": "5 TALL poses, in the air: ask for a SQUARE 1:1 image (the Assassin's came out as a vertical sheet; that still worked, tell me what you got)",
    "10_winters_kiss": "5 poses. Use the sheet for poses 1-3, and draw poses 4 and 5 as SINGLE images (they went wrong in the Assassin's sheet: the head angle of pose 4, the wrong arm catching in pose 5): prompt_single_pose4_rogue_reference.txt + ref_uid03.png, and prompt_single_pose5_REDRAW_catch.txt + ref_uid04.png (each with reference_image.png). If the sheet's panels 4 and 5 come out right, the singles are not needed.",
    "11_static_stiletto": "6 poses, 3:2 (panel 5 is in the air; its stab frame comes from the Shadow Shiv, its last frame from the idle)",
}

ap = argparse.ArgumentParser()
ap.add_argument("--look", default="Assassin")
ap.add_argument("--ref", default="Animations/Assassin/reference_image.png")
ap.add_argument("--out", default="Assassin_reskin_kit")
ap.add_argument("--tag", default="assassin", help="the look's name in the prompt file names: reskin/<guides>/prompt_<tag>_sheet.txt (default assassin)")
ap.add_argument("--only", default="", help="comma list of the kit folders to make, e.g. 01_idle (default: all; the other looks get their folders one by one as their prompts are written)")
a = ap.parse_args()
only = [x.strip() for x in a.only.split(",") if x.strip()]

out = ROOT / a.out
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
ref = ROOT / a.ref
lines = ["%s RE-SKIN KIT (made by source/tools/make_reskin_kit.py: a copy, rebuilt whenever a prompt, a guide or the reference picture changes)." % a.look.upper(), "",
         "One folder per animation. Every folder holds everything for one generation: the look's reference picture, the pose guide(s), and the prompt file(s).",
         "To generate: attach reference_image.png and the guide named in the prompt (guide_sheet_1.png, or guide_uidNN.png for one pose), paste the prompt file's text, ask for the picture size the prompt says;",
         "save the result in the project's inbox/ folder with the name the prompt says, and tell Claude.", ""]
for folder, src, prompts, what in KIT:
    if only and folder not in only:
        continue
    prompts = [(pf.replace("prompt_assassin_", "prompt_%s_" % a.tag), name) for pf, name in prompts]
    if a.tag != "assassin":
        what = NEW_LOOK_WHAT.get(folder) or re.sub(r"\(DONE[^)]*\)", "", what).strip()   # the Assassin's progress notes do not belong to another look
    d = out / folder
    d.mkdir()
    g = ROOT / "reskin" / src
    shutil.copy2(ref, d / "reference_image.png")
    for s in sorted(g.glob("guide_sheet_*.png")):
        shutil.copy2(s, d / s.name)
    need = set()
    for pf, name in prompts:
        text = (g / pf).read_text(encoding="utf-8")
        for src_name, kit_name in prompts:                                 # the prompts name each other: use the names in the kit
            text = text.replace(src_name, kit_name)
        need |= set(re.findall(r"(?:guide|ref)_uid\d+\.png", text))
        text = re.sub(r"reskin/[A-Za-z_]+/", "", text)
        text = re.sub(r"Animations/[A-Za-z]+/(?=reference_image\.png)", "", text)
        (d / name).write_text(text, encoding="utf-8")
    for n in sorted(need):
        shutil.copy2(g / n, d / n)
    lines.append("%s: %s" % (folder, what))
    lines.append("   files: " + ", ".join(sorted(p.name for p in d.iterdir())))
(out / "README.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print("->", out)
