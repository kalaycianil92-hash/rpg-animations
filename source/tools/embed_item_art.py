#!/usr/bin/env python3
"""Refreshes the item pictures embedded in hand-anchor-tool.html from source/assets/.

The tool is one standalone file, so its item pictures (sword, orb, staff...) are data inside it. Each such line ends with a marker
comment like /*ART:staff.png*/; this script rewrites the picture on every marked line from the file of that name in source/assets/.
Run it after changing an item picture (build.py needs no such step: the test page reads source/assets/ itself).

  python embed_item_art.py
"""
import base64
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[2]
tool = root / "hand-anchor-tool.html"
pattern = re.compile(r'(src = ")data:image/png;base64,[A-Za-z0-9+/=]+(";\s*)/\*ART:([A-Za-z0-9_.\-]+)\*/')

def repl(m):
    name = m.group(3)
    data = (root / "source" / "assets" / name).read_bytes()
    print("embedded", name, len(data), "bytes")
    return m.group(1) + "data:image/png;base64," + base64.b64encode(data).decode() + m.group(2) + "/*ART:" + name + "*/"

tool.write_text(pattern.sub(repl, tool.read_text(encoding="utf-8")), encoding="utf-8")
