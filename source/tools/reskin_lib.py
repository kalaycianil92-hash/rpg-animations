#!/usr/bin/env python3
"""Shared helpers of the re-skin tools (make_pose_guides.py, check_reskin.py, reskin_strip.py); see docs/RESKIN_PILOT_PLAN.md.

A strip is a row of square-width cells (512 px wide, as tall as the strip). Strips repeat frames for timing (the pack has one frame time), so an animation has fewer UNIQUE images than frames:
`uniques` finds them by exact pixel equality, in order of first appearance, and the map position -> unique id that every tool shares.
"""
import hashlib
import json
import pathlib

import numpy as np
from PIL import Image

CW = 512                      # the width of a cell
GROUND_FROM_BOTTOM = 42       # the ground line is this many px above the bottom of a cell (all strips, tall cells too)


def load_frames(path, cw=CW):
    """-> (list of H x cw x 4 uint8 arrays, H)"""
    im = Image.open(path).convert("RGBA")
    n = im.width // cw
    return [np.array(im.crop((i * cw, 0, (i + 1) * cw, im.height))) for i in range(n)], im.height


def save_strip(frames, path):
    H = frames[0].shape[0]
    cw = frames[0].shape[1]
    out = Image.new("RGBA", (cw * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(Image.fromarray(f), (i * cw, 0))
    out.save(path)


def pad_to(f, H):
    """a frame shorter than H is put on the bottom of an empty H-tall cell (a standing frame of a 512 px cell inside a 768 px tall cell: the ground line is 42 px above the bottom in both)"""
    if f.shape[0] >= H:
        return f
    out = np.zeros((H, f.shape[1], 4), np.uint8)
    out[H - f.shape[0]:] = f
    return out


def frame_key(f):
    return hashlib.md5(f.tobytes()).hexdigest()


def uniques(frames):
    """-> (first, pos, groups): first[uid] = the first position of unique image uid, pos[i] = the uid at position i, groups[uid] = all its positions"""
    seen, first, pos = {}, [], []
    for i, f in enumerate(frames):
        k = frame_key(f)
        if k not in seen:
            seen[k] = len(first)
            first.append(i)
        pos.append(seen[k])
    groups = [[] for _ in first]
    for i, u in enumerate(pos):
        groups[u].append(i)
    return first, pos, groups


def mask(f):
    return f[..., 3] > 128


def bbox(m):
    """(x0, y0, x1, y1) inclusive of the True pixels, or None"""
    ys, xs = np.where(m)
    if not len(ys):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def ground_y(H):
    return H - GROUND_FROM_BOTTOM


def load_marks(path):
    p = pathlib.Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def marks_at(doc, pos):
    """The visible marks of frame `pos` (0-based) as [(track, x, y)] in fractions of the cell: main first, then off"""
    if not doc:
        return []
    try:
        tr = doc["characters"][0]["animations"][0]["tracks"]
    except (KeyError, IndexError):
        return []
    out = []
    for t in ("main", "off"):
        if t in tr and pos < len(tr[t]):
            m = tr[t][pos]
            if m and not m.get("hide"):
                out.append((t, float(m["x"]), float(m["y"])))
    return out


def default_marks_path(strip):
    s = pathlib.Path(strip)
    return s.with_name(s.name[:-len(".png")] + ".hand-anchors.json")


def default_placement_path(strip):
    s = pathlib.Path(strip)
    return s.with_name(s.name[:-len(".png")] + ".placement.json")


def char_and_anim(strip):
    s = pathlib.Path(strip).resolve()
    if s.parent.parent.parent.name == "Animations":
        return s.parent.parent.name, s.parent.name
    return s.parent.name, s.stem
