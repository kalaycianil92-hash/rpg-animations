#!/usr/bin/env python3
"""Writes the Spellblade's re-skin prompts for every animation after the idle (2026-11-06), from the Assassin's.

A) The sheet prompts that make_assassin_prompts.py writes (hit, death, dodge, run, umbral_shroud, abyssal_backstab, shadow_shiv, static_stiletto, dagger_throw): this script reads that file's pose table
   (ANIMS), so the poses stay in one place, and writes reskin/Rogue_<animation>/prompt_spellblade_sheet.txt with the Spellblade's description (Animations/Spellblade/source/spellblade_description.txt).
   The Assassin's poses speak of a mask and 'no mouth': for the Spellblade the whole face is visible (eyes, brow AND mouth show the expression). Winter's Kiss panel 5 says in words which arm catches
   (the REAR arm: the Assassin's sheet raised the wrong one).
B) The prompts that were written by hand for the Assassin (Permafrost Execution sheet + the retreat single, Winter's Kiss pose 4 with the Rogue's own frame as the example, Winter's Kiss pose 5 with the
   arm sides spelled out) are converted: her description replaces the Assassin's, the file names and colours change.
The idle's prompts come from make_spellblade_idle_prompts.py. Run again after changing the description or a pose text, then rebuild the kit:
   python source/tools/make_reskin_kit.py --look Spellblade --ref Animations/Spellblade/reference_image.png --out Spellblade_reskin_kit --tag spellblade

  python Animations/Spellblade/source/make_spellblade_prompts.py [animation ...]     (only the named ones, e.g. hit; none = all)
"""
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
DESC = (ROOT / "Animations/Spellblade/source/spellblade_description.txt").read_text(encoding="utf-8").strip()
SRC = (ROOT / "Animations/Assassin/source/make_assassin_prompts.py").read_text(encoding="utf-8")
ANIMS = ast.literal_eval(re.search(r"^ANIMS = (\{.*?^\})$", SRC, re.S | re.M).group(1))

FACE = ("Her face is fully visible (no mask, nothing over her mouth): show every expression with the eyes, the brow AND the mouth (clenched teeth or a grimace in pain, a calm faint smile at rest). "
        "Image 1's ready stance (the low calm stance, the far fist swung back behind the hip, the near fist low in front of the thigh) is what 'the ready stance' means below.")

KISS5 = ("Catch. The REAR arm (the far-side arm, the thrower: the arm with the blue dot) comes out of her chest toward the enemy, bent at the elbow, the forearm angled up at about chest height, the hand OPEN with the "
         "palm up and the fingers spread (no dot), reaching to catch something that is coming back. The FRONT arm (the near arm, the red dot) keeps its closed fist low in front of her hip on the enemy's side. "
         "NOTHING hangs behind her back: on the side away from the enemy there is only her cape. The torso leans back about 5 degrees, the eyes on the open hand. The cape sweeps back a little.")

EXPRESSION = "Her face, hair and clothes are the same in every panel; only her expression changes, as the poses say."


def cleanup(text):
    """changes every Assassin-only word and file name"""
    text = text.replace("Her or his face looks the same in every panel.", EXPRESSION)
    text = text.replace("in her or his own colours", "in her own colours").replace("her or his own colours", "her own colours")
    text = text.replace("Animations/Assassin/reference_image.png", "Animations/Spellblade/reference_image.png")
    text = text.replace("ASSASSIN ", "SPELLBLADE ").replace("assassin_", "spellblade_")
    text = text.replace("the Assassin's description", "the Spellblade's description").replace("(the Assassin: her look)", "(the Spellblade: her look)")
    text = text.replace("Made 2026-11-05", "Made 2026-11-06")
    text = text.replace("the Assassin's idle", "the Spellblade's idle")
    return text


def character(text):
    m = re.search(r"(CHARACTER: the exact same character as in image 1: )(.*?)(\. Keep the same painted)", text, re.S)
    assert m, "no CHARACTER paragraph"
    return text[:m.start(2)] + DESC + text[m.end(2):]


def check(text, name):
    low = text.lower()
    bad = [w for w in ("assassin", "mask", "scarf", "violet", "ebony", "silver-white", "gunmetal") if w in low]
    allowed = {"mask": ["no mask"], "scarf": ["her scarf, her trousers"], "violet": ["black, violet, blue"]}
    for w in list(bad):
        rest = low
        for ok in allowed.get(w, []):
            rest = rest.replace(ok, "")
        if w not in rest:
            bad.remove(w)
    assert not bad, (name, bad, [l[:120] for l in text.splitlines() if any(b in l.lower() for b in bad)])


ONLY = sys.argv[1:]

# ---- A) the sheets
for anim, (save, poses, extra) in ANIMS.items():
    if ONLY and anim not in ONLY:
        continue
    g = ROOT / "reskin" / ("Rogue_" + anim)
    text = (g / "prompt.txt").read_text(encoding="utf-8")
    n = len(poses)
    if anim == "dagger_throw":
        poses = poses[:4] + [KISS5]
    title = "SPELLBLADE %s, SHEET OF %d (pose-guided). Made 2026-11-06 from make_pose_guides.py's prompt with the Spellblade's description and the poses filled in. Works with Gemini or ChatGPT." % (anim.upper().replace("_", " "), n)
    text = re.sub(r"^RE-SKIN PROMPT.*$", title, text, count=1, flags=re.M)
    ratio = re.search(r"Ask for a (\S+) image", text).group(1)
    shape = (" (ChatGPT: 1536 x 1024)" if ratio == "3:2" else " (ChatGPT: 1024 x 1024)" if ratio == "1:1" else "")
    save = save.replace("assassin_", "spellblade_")
    text = re.sub(r"- Attach TWO images: .*?\n", "- Attach TWO images: (1) reference_image.png (her look), (2) guide_sheet_1.png (%d pose silhouettes). Ask for a %s image%s. Paste everything between the two lines of equals signs (nothing is left to fill in).\n- Save the result as inbox/%s and tell me.\n" % (n, ratio, shape, save), text, count=1)
    text = text.replace("[PASTE THE NEW LOOK'S DESCRIPTION HERE]", DESC)
    pose_par = "THE %s POSES, in the order of the panels (the silhouettes show the legs, the body and the head; the arms, the hands and the eyes are described here, because a silhouette cannot show which arm is where or whether a hand is open):\n" % {3: "THREE", 5: "FIVE", 6: "SIX"}.get(n, str(n))
    pose_par += "\n".join("%d. %s" % (i + 1, p) for i, p in enumerate(poses)) + "\n" + FACE + (("\n" + extra) if extra else "")
    text = text.replace("\n\nVIEW: strict side view", "\n\n" + pose_par + "\n\nVIEW: strict side view", 1)
    text = text.replace("In every panel draw the character of image 1 in EXACTLY the pose of the matching panel of image 2.", "In every panel draw the character of image 1 in EXACTLY the pose of the matching panel of image 2 (the poses are described below).")
    text = text.replace("Its grey silhouettes show where the head, body, arms, legs and cloak must be in each panel:", "Its grey silhouettes show where the head, body, arms, legs and the cloak of the OLD character must be in each panel (draw the NEW character's own cape, hanging or flying the way the pose needs it):")
    text = cleanup(text)
    assert "The dots are for positioning ONLY" in text, anim
    check(text, anim)
    (g / "prompt_spellblade_sheet.txt").write_text(text, encoding="utf-8")
    print(anim, "->", g.name, "prompt_spellblade_sheet.txt,", len(text.split()), "words,", n, "poses")

# ---- B) the hand-written Assassin prompts, converted
CONVERT = [
    ("permafrost", "Rogue_permafrost_execution", "prompt_assassin_sheet.txt", "prompt_spellblade_sheet.txt", []),
    ("permafrost_retreat", "Rogue_permafrost_execution", "prompt_assassin_single_retreat.txt", "prompt_spellblade_single_retreat.txt", []),
    ("kiss_pose4", "Rogue_dagger_throw", "prompt_assassin_single_pose4_rogue.txt", "prompt_spellblade_single_pose4_rogue.txt", [
        ("in her own black and deep violet", "in her own ivory-white and gold"),
        ("Her short cape hangs behind her", "Her cape hangs behind her"),
        ("The cape and the scarf-like cape tails settle behind her.", "The cape settles behind her."),
    ]),
    ("kiss_pose5", "Rogue_dagger_throw", "prompt_assassin_single_pose5_hands.txt", "prompt_spellblade_single_pose5_hands.txt", [
        ("POSE 5 (THE CATCH) REDRAWN BECAUSE THE WRONG ARM CATCHES, ONE IMAGE", "POSE 5 (THE CATCH), ONE IMAGE"),
        ("Keep her colours exactly as in image 1: ebony black, deep violet, boots with a violet top edge and dark-brown straps, dark gunmetal metal, silver-white only in the hair.",
         "Keep her colours exactly as in image 1: ivory-white and gold, cream boots with a gold-edged cuff, copper-scarlet red only in the hair."),
        ("inbox/spellblade_winters_kiss_pose5_v2.png", "inbox/spellblade_winters_kiss_pose5.png"),
    ]),
]
WHY5 = ("WHY: the animation's throwing and catching arm is the REAR arm (the arm on the far side of her body, whose fist hangs behind her hip in her stance). A sheet of this pose can raise the FRONT arm instead "
        "and leave the rear fist hanging behind her back (that happened in an earlier re-skin of this pose), so this single image spells out which arm is which.")
for key, folder, src, dst, repls in CONVERT:
    if ONLY and not any(o in key or o in folder for o in ONLY):
        continue
    g = ROOT / "reskin" / folder
    text = (g / src).read_text(encoding="utf-8")
    text = character(text)
    text = cleanup(text)
    for old, new in repls:
        assert old in text, (key, old[:60])
        text = text.replace(old, new)
    if key == "kiss_pose5":
        text, k = re.subn(r"WHY \(the user\):.*?\n\nHOW TO USE", WHY5 + "\n\nHOW TO USE", text, count=1, flags=re.S)
        assert k == 1
    if key == "kiss_pose4":
        text = text.replace("inbox/spellblade_winters_kiss_pose4.png", "inbox/spellblade_winters_kiss_pose4.png")
    check(text, key)
    (g / dst).write_text(text, encoding="utf-8")
    print(key, "->", g.name, dst, len(text.split()), "words")
