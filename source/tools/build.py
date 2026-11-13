#!/usr/bin/env python3
"""Builds the two standalone HTML pages by inlining the images in ../assets
into the templates in ../src.  Each template contains tokens like
__ASSET:sword.png__ which are replaced by a base64 data URI.

The test page also gets the warrior's built-in animations: the token
__DEFAULT_ANIMS__ becomes a JSON list with one entry per folder in
../../Animations/Warrior/<animation>/ : the strip (as a data URI), its
.hand-anchors.json and, if it has one, its .placement.json.  A new animation
folder needs a slot in SLOTS (and in the page's POSES) to show up.

Usage:  python tools/build.py          (writes ../dist/*.html)
"""
import base64, json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "dist"
out.mkdir(exist_ok=True)

ANIM_DIR = root.parent / "Animations" / "Warrior"
MAGE_DIR = root.parent / "Animations" / "Mage"
ROGUE_DIR = root.parent / "Animations" / "Rogue"
ASSASSIN_DIR = root.parent / "Animations" / "Assassin"
SPELLBLADE_DIR = root.parent / "Animations" / "Spellblade"
SLIME_DIR = root.parent / "Animations" / "Slime"          # the fire slime (monsters, 2026-11-07): the right-hand fighter's art; only the idle so far
ICESLIME_DIR = root.parent / "Animations" / "IceSlime"       # the ice slime (2026-11-08): the cold twin of the fire slime, same slots
DARKSLIME_DIR = root.parent / "Animations" / "DarkSlime"                  # the dark slime (2026-11-09): violet, horns, a green key
LIGHTNINGSLIME_DIR = root.parent / "Animations" / "LightningSlime"   # the lightning slime (2026-11-09): yellow with blue-white arcs, same slots
ELITESLIME_DIR = root.parent / "Animations" / "EliteSlime"           # the Elite slime (2026-11-10): grey stone in armour with a shield and a floating sword fist, physical attacks, no element
SLIMEKING_DIR = root.parent / "Animations" / "SlimeKing"               # the Slime King (2026-11-11): the boss, an ivory slime with a golden crown and a golden staff held by a floating glove, drawn about twice the size of the others
SLOTS = {"idle": "idle", "jump_attack": "attack", "sunder_strike": "attack", "cast": "attack", "umbral_shroud": "attack", "abyssal_backstab": "attack", "shadow_shiv": "attack", "static_stiletto": "attack", "dagger_throw": "attack", "permafrost_execution": "attack", "ember_spit": "attack", "sword_slash": "attack", "shield_bash": "slam", "rockfall_drop": "bounce", "earthbreaker": "eruption", "stone_guard": "guard", "block": "block", "magma_slam": "slam", "magma_eruption": "eruption", "inferno_bounce": "bounce", "frost_spit": "attack", "spark_spit": "attack", "gloom_spit": "attack", "umbral_slam": "slam", "nightfall_bounce": "bounce", "abyssal_eruption": "eruption", "thunder_slam": "slam", "voltaic_eruption": "eruption", "skybolt_bounce": "bounce", "glacier_slam": "slam", "permafrost_eruption": "eruption", "blizzard_bounce": "bounce","radiant_ooze": "attack", "royal_decree": "decree", "staff_raise": "raise", "crown_slam": "bounce", "heal": "heal", "hit": "hit", "death": "death", "dodge": "dodge", "run": "run"}  # folder -> pack slot in the test page

def inline(text):
    def repl(m):
        data = (root / "assets" / m.group(1)).read_bytes()
        return "data:image/png;base64," + base64.b64encode(data).decode()
    return re.sub(r"__ASSET:([^_][^ \"']*?\.png)__", repl, text)

def fx_textures():
    """The optional painted fire textures in ../assets/fx/*.png as {name: data URI} (empty when there are none: the page then has only the code look)."""
    d = root / "assets" / "fx"
    files = sorted(d.glob("*.png")) if d.is_dir() else []
    for f in files:
        print("texture", f.name)
    return json.dumps({f.stem: "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode() for f in files}, separators=(",", ":"))

def bg_scenes():
    """The stage pictures in ../assets/bg/<scene>/ (far, ground, props, mid; .jpg or .png, made by make_bg_layer.py) as {scene: {layer: data URI}}.
    A folder that holds a file standin.txt is made of test pictures (the page says so); a file horizon.txt (one number, e.g. 0.758) says where the far picture's wall meets the floor when it is not at the usual 62%; a file centered.txt (layer names, e.g. props) marks layers that are one fixed composition, drawn once and centred. Folders starting with _ are skipped. Empty: the stage stays a plain gradient."""
    d = root / "assets" / "bg"
    scenes = {}
    for s in (sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith("_")) if d.is_dir() else []):
        files = sorted(s.glob("*.jpg")) + sorted(s.glob("*.png"))
        if not files:
            continue
        scenes[s.name] = {f.stem: "data:image/%s;base64," % ("jpeg" if f.suffix == ".jpg" else "png") + base64.b64encode(f.read_bytes()).decode() for f in files}
        if (s / "standin.txt").exists():
            scenes[s.name]["standin"] = True
        if (s / "horizon.txt").exists():                                   # where the far picture's wall meets the floor, as a share of its height (default .62)
            hz = (s / "horizon.txt").read_text().split()                    # one number (the far picture), or two (and the floor's far edge, for a composed floor)
            scenes[s.name]["horizon"] = float(hz[0])
            if len(hz) > 1:
                scenes[s.name]["groundHorizon"] = float(hz[1])
        if (s / "centered.txt").exists():                                  # layers (names, e.g. props) drawn once and centred on the stage instead of repeating: a fixed composition
            scenes[s.name]["centered"] = (s / "centered.txt").read_text().split()
        if (s / "gate.txt").exists():                                      # where an entrance's gate stands, as a share of the far picture's width (the page's Enter preview walks there)
            scenes[s.name]["gateX"] = float((s / "gate.txt").read_text().split()[0])
        print("scene", s.name, ", ".join(f.stem for f in files), "(STAND-IN)" if (s / "standin.txt").exists() else "")
    return json.dumps(scenes, separators=(",", ":"))

def default_anims(anim_dir):
    entries = []
    if not anim_dir.is_dir():
        return "[]"
    for folder in sorted(p for p in anim_dir.iterdir() if p.is_dir()):
        if folder.name not in SLOTS:
            print("skipped", folder.name, "(no slot in the test page yet)")
            continue
        strips = sorted(folder.glob("*_strip.png"))
        if not strips:
            print("skipped", folder.name, "(no *_strip.png)")
            continue
        if len(strips) > 1:
            print("note:", folder.name, "has several strips, using", strips[-1].name)
        strip = strips[-1]
        stem = strip.name[:-len(".png")]
        def load(suffix):
            f = folder / (stem + suffix)
            return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
        entries.append({
            "slot": SLOTS[folder.name],
            "file": strip.name,
            "src": "data:image/png;base64," + base64.b64encode(strip.read_bytes()).decode(),
            "anchors": load(".hand-anchors.json"),
            "placement": load(".placement.json"),
            "squash": load(".squash.json"),
            "mouth": load(".mouth.json"),                                     # a monster's glowing mouth per frame (the Ember Spit's start point), when there is one                                   # per-frame proportions of a monster's idle (the page's Squash and stretch slider), when there are any
        })
        print("animation", folder.name, "->", SLOTS[folder.name], strip.name,
              "| hand marks" if entries[-1]["anchors"] else "| NO hand marks",
              "| path" if entries[-1]["placement"] else "")
    return json.dumps(entries, separators=(",", ":"))

def slime_candidates():
    """Candidate idle strips of the fire slime (2026-11-07), Animations/Slime/idle/candidates/<tag>_fire_idle_strip.png, as [{key, file, src}]:
    the page lists each one in its Monster select so the looks can be compared in a fight (the page names them from the tag)."""
    d = SLIME_DIR / "idle" / "candidates"
    out = []
    for f in (sorted(d.glob("*_fire_idle_strip.png")) if d.is_dir() else []):
        sq = f.with_suffix(".squash.json")                             # per-frame proportions (face height, base width) measured by make_candidate_strip.py: the page's Squash and stretch slider uses them
        out.append({"key": f.name.split("_")[0], "file": f.name, "src": "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode(),
                    "squash": json.loads(sq.read_text(encoding="utf-8")) if sq.exists() else None})
        print("slime candidate", f.name)
    return json.dumps(out, separators=(",", ":"))

for src in sorted((root / "src").glob("*.src.html")):
    name = src.name.replace(".src.html", ".html")
    text = src.read_text(encoding="utf-8")
    if "__DEFAULT_ANIMS__" in text:
        text = text.replace("__DEFAULT_ANIMS__", default_anims(ANIM_DIR))
    if "__FX_TEXTURES__" in text:
        text = text.replace("__FX_TEXTURES__", fx_textures())
    if "__BG_SCENES__" in text:
        text = text.replace("__BG_SCENES__", bg_scenes())
    if "__MAGE_ANIMS__" in text:
        text = text.replace("__MAGE_ANIMS__", default_anims(MAGE_DIR))
    if "__ROGUE_ANIMS__" in text:
        text = text.replace("__ROGUE_ANIMS__", default_anims(ROGUE_DIR))
    if "__ASSASSIN_ANIMS__" in text:
        text = text.replace("__ASSASSIN_ANIMS__", default_anims(ASSASSIN_DIR))
    if "__SPELLBLADE_ANIMS__" in text:
        text = text.replace("__SPELLBLADE_ANIMS__", default_anims(SPELLBLADE_DIR))
    if "__SLIME_ANIMS__" in text:
        text = text.replace("__SLIME_ANIMS__", default_anims(SLIME_DIR))
    if "__ICESLIME_ANIMS__" in text:
        text = text.replace("__ICESLIME_ANIMS__", default_anims(ICESLIME_DIR))
    if "__DARKSLIME_ANIMS__" in text:
        text = text.replace("__DARKSLIME_ANIMS__", default_anims(DARKSLIME_DIR))
    if "__LIGHTNINGSLIME_ANIMS__" in text:
        text = text.replace("__LIGHTNINGSLIME_ANIMS__", default_anims(LIGHTNINGSLIME_DIR))
    if "__ELITESLIME_ANIMS__" in text:
        text = text.replace("__ELITESLIME_ANIMS__", default_anims(ELITESLIME_DIR))
    if "__SLIMEKING_ANIMS__" in text:
        text = text.replace("__SLIMEKING_ANIMS__", default_anims(SLIMEKING_DIR))
    if "__SLIME_CANDIDATES__" in text:
        text = text.replace("__SLIME_CANDIDATES__", slime_candidates())
    (out / name).write_text(inline(text), encoding="utf-8")
    print("built", out / name)
