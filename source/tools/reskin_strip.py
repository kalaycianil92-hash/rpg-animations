#!/usr/bin/env python3
"""Rebuilds an animation strip from the re-skinned frames, in the ORIGINAL's frame order, and copies its hand marks, path and fps (see docs/RESKIN_PILOT_PLAN.md).

The generated sheet gives each unique image once; the original strip repeats frames for timing and shares some frames with other animations. This puts every new image back where the original had it:
  <out>/<stem>.png                 the new strip (as many frames as the original, the repeats restored)
  <out>/<stem>.hand-anchors.json   the original's marks, copied frame by frame (the animation renamed; --char-name renames the character): the poses are the same, so the fists are where they were
  <out>/<stem>.placement.json      the original's path file (fps, hit frame, x, y), the file name changed
The marks are the ORIGINAL's: if a new frame's fists are a few px away, refine them in the hand tool (the check_reskin.py overlay shows where they sit).

  python source/tools/reskin_strip.py --orig Animations/Rogue/permafrost_execution/cloaked_permafrost_execution_19frame_strip.png --map reskin/Rogue_permafrost_execution/frame_map.json \\
      --new aligned_permafrost.png --shared Animations/Spellblade/idle/spellblade_idle_strip.png --stem spellblade_permafrost_execution_19frame_strip --out-dir Animations/Spellblade/permafrost_execution

--new     the corrected new frames, in the order of the guides (check_reskin.py --align writes them)
--shared  the new version of each strip the original shares frames with (the idle...), in the order of --share-with when the guides were made
--override UID=STRIP:FRAME   take unique image UID from frame FRAME (1-based) of STRIP instead (for example a frame drawn separately)
"""
import argparse
import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reskin_lib as L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orig", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--new", nargs="*", default=[], help="the corrected new frames (none when every image of the animation is shared, like the Static Stiletto)")
    ap.add_argument("--shared", nargs="*", default=[])
    ap.add_argument("--override", action="append", default=[])
    ap.add_argument("--stem", required=True, help="the new file name without .png (ends in _strip)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--char-name", help="the character's name in the marks file (default: unchanged)")
    ap.add_argument("--overwrite-marks", action="store_true", help="write the copied marks even when the folder already has a marks file (by default the user's own marks are never overwritten)")
    a = ap.parse_args()
    if not a.stem.endswith("_strip"):
        sys.exit("the stem must end in _strip, like the page's file names")

    of, H = L.load_frames(a.orig)
    first, pos, groups = L.uniques(of)
    mp = json.loads(pathlib.Path(a.map).read_text(encoding="utf-8"))
    if len(first) != len(mp["uniques"]):
        sys.exit("the map was made for another strip (%d unique images there, %d here)" % (len(mp["uniques"]), len(first)))
    new = []
    for p in a.new:
        fr, h = L.load_frames(p)
        if h != H:
            sys.exit("%s is %d px tall, the original %d px" % (p, h, H))
        new += fr
    if len(new) != len(mp["guided"]):
        sys.exit("%d new frames, but the guides had %d images" % (len(new), len(mp["guided"])))
    shared = []
    for p in a.shared:
        fr, h = L.load_frames(p)
        if h > H:
            sys.exit("%s is %d px tall, the original only %d px" % (p, h, H))
        shared.append([L.pad_to(f, H) for f in fr])                      # (a 512 px cell goes on the bottom of a tall one)
    ov = {}
    for o in a.override:
        uid, rest = o.split("=", 1)
        sp, fn = rest.rsplit(":", 1)
        fr, h = L.load_frames(sp)
        ov[int(uid)] = L.pad_to(fr[int(fn) - 1], H)

    by_uid = {uid: new[k] for k, uid in enumerate(mp["guided"])}
    for u in mp["uniques"]:
        uid = u["id"]
        if uid in ov:
            by_uid[uid] = ov[uid]
        elif u["shared"]:
            si, fi = u["shared"]["strip"], u["shared"]["frame"]
            if si >= len(shared):
                sys.exit("unique image %d is shared with strip %d (%s): give its new version with --shared (in the order of --share-with), or --override %d=STRIP:FRAME" % (uid, si, mp["share_with"][si], uid))
            by_uid[uid] = shared[si][fi]
    strip = [by_uid[u] for u in pos]

    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    L.save_strip(strip, out / (a.stem + ".png"))
    anim = a.stem[:-len("_strip")]

    marks = L.load_marks(mp.get("marks") or L.default_marks_path(a.orig))
    existing = out / (a.stem + ".hand-anchors.json")
    kept = existing.exists() and not a.overwrite_marks
    if marks and not kept:
        m2 = copy.deepcopy(marks)
        m2["characters"][0]["animations"][0]["name"] = anim
        if a.char_name:
            m2["characters"][0]["name"] = a.char_name
        (out / (a.stem + ".hand-anchors.json")).write_text(json.dumps(m2, indent=1), encoding="utf-8", newline="\n")
    pl = L.load_marks(L.default_placement_path(a.orig))
    if pl:
        pl["file"] = a.stem + ".png"
        (out / (a.stem + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")
    print("wrote %s (%d frames, %d unique images)%s%s" % (out / (a.stem + ".png"), len(strip), len(first), ", marks KEPT (the folder's own marks file is not overwritten)" if kept else ", marks copied" if marks else ", NO marks found", ", path copied" if pl else ", no path file"))


if __name__ == "__main__":
    main()
