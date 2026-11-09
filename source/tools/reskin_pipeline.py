#!/usr/bin/env python3
"""One step from a generated re-skin sheet to a finished strip (cut -> check and align -> rebuild), see docs/RESKIN_PILOT_PLAN.md.

  python source/tools/reskin_pipeline.py --anim run --sheet inbox/assassin_run_sheet1.png \\
      --orig Animations/Rogue/run/cloaked_run_8frame_strip.png --map reskin/Rogue_run/frame_map.json \\
      --out-dir Animations/Assassin/run --stem assassin_run_8frame_strip --shared Animations/Assassin/idle/assassin_idle_strip.png

  --count N   the sheet has N drawn panels (3 x 2 grid read left to right, top row first)
  --cols/--rows  the grid (default 3 x 2); --height  the figure height of the first panel after the cut (default: the original's first image)
  --extra-new f.png   more new frames (single images, already cut: use slice_keypose_sheet.py) appended after the sheet's, in the order of the guides

It writes its work files to reskin/work/<stem>/ (the cut, the aligned frames, the check report and overlays) and the strip, marks and path file to --out-dir.
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reskin_lib as L

ROOT = pathlib.Path(__file__).resolve().parents[2]
T = pathlib.Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--anim", required=True)
ap.add_argument("--sheet", required=True)
ap.add_argument("--orig", required=True)
ap.add_argument("--map", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--stem", required=True)
ap.add_argument("--shared", nargs="*", default=[])
ap.add_argument("--count", type=int, default=0)
ap.add_argument("--cols", type=int, default=3)
ap.add_argument("--rows", type=int, default=2)
ap.add_argument("--height", type=float, default=0)
ap.add_argument("--extra-new", nargs="*", default=[])
ap.add_argument("--char-name", default="Assassin")
ap.add_argument("--no-build", action="store_true", help="cut and check only")
a = ap.parse_args()

work = ROOT / "reskin" / "work" / a.stem
work.mkdir(parents=True, exist_ok=True)
mp = json.loads(pathlib.Path(a.map).read_text(encoding="utf-8"))
frames, H = L.load_frames(a.orig)
first, pos, groups = L.uniques(frames)
bb = L.bbox(L.mask(frames[first[mp["guided"][0]]])) if mp["guided"] else None
height = a.height or (bb[3] - bb[1] + 1 if bb else 408)
cut = work / "cut.png"
if mp["guided"]:
    cmd = [sys.executable, str(T / "slice_keypose_sheet.py"), a.sheet, str(cut), "--cols", str(a.cols), "--rows", str(a.rows), "--height", str(height), "--scale-from", "panel1", "--modes", "center"]
    if a.count:
        cmd += ["--count", str(a.count)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    print(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-400:])
    if out.returncode:
        sys.exit(out.stderr)
news = ([str(cut)] if mp["guided"] else []) + a.extra_new
aligned = work / "aligned.png"
if mp["guided"]:
    cmd = [sys.executable, str(T / "check_reskin.py"), "--orig", a.orig, "--new"] + news + ["--map", a.map, "--align", str(aligned), "--out", str(work)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    print(out.stdout)
    if out.returncode:
        sys.exit(out.stderr)
if a.no_build:
    sys.exit(0)
cmd = [sys.executable, str(T / "reskin_strip.py"), "--orig", a.orig, "--map", a.map, "--stem", a.stem, "--out-dir", a.out_dir, "--char-name", a.char_name]
if mp["guided"]:
    cmd += ["--new", str(aligned)]
if a.shared:
    cmd += ["--shared"] + a.shared
out = subprocess.run(cmd, capture_output=True, text=True)
print(out.stdout.strip() or out.stderr)
