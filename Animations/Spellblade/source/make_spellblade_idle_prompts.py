#!/usr/bin/env python3
"""Writes the Spellblade's IDLE re-skin prompts (2026-11-06) from the Assassin's (reskin/Rogue_idle/prompt_assassin_sheet.txt and prompt_assassin_single.txt):
the character paragraph becomes the Spellblade's description (Animations/Spellblade/source/spellblade_description.txt), the Assassin-only words (mask, assassin, file names) are changed, and the files are
written next to the guides as prompt_spellblade_sheet.txt (method A, one sheet of six: the one used for the Assassin) and prompt_spellblade_single.txt (method B, six single images).
Run again after changing the description; then rebuild the kit:  python source/tools/make_reskin_kit.py --look Spellblade --ref Animations/Spellblade/reference_image.png --out Spellblade_reskin_kit --tag spellblade --only 01_idle

  python Animations/Spellblade/source/make_spellblade_idle_prompts.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
G = ROOT / "reskin" / "Rogue_idle"
DESC = (ROOT / "Animations/Spellblade/source/spellblade_description.txt").read_text(encoding="utf-8").strip()


def convert(text):
    n = 0

    def sub(old, new, count=1):
        nonlocal text
        assert text.count(old) >= 1, old[:70]
        text = text.replace(old, new)

    # the character paragraph: from "the exact same character as in image 1: " up to ". Keep the same painted"
    m = re.search(r"(CHARACTER: the exact same character as in image 1: )(.*?)(\. Keep the same painted)", text, re.S)
    assert m
    text = text[:m.start(2)] + DESC + text[m.end(2):]
    sub("ASSASSIN IDLE", "SPELLBLADE IDLE")
    sub("Made 2026-11-05 from reskin/Rogue_idle/prompt.txt with the Assassin's description filled in.", "Made 2026-11-06 from the Assassin's idle prompt with the Spellblade's description filled in.") if "Made 2026-11-05 from reskin" in text else None
    text = text.replace("Made 2026-11-05.", "Made 2026-11-06 from the Assassin's idle prompt with the Spellblade's description filled in.")
    text = text.replace("Animations/Assassin/reference_image.png", "Animations/Spellblade/reference_image.png")
    text = text.replace("inbox/assassin_idle_sheetA.png", "inbox/spellblade_idle_sheetA.png")
    text = re.sub(r"inbox/assassin_idle_B_", "inbox/spellblade_idle_B_", text)
    text = text.replace("prompt_assassin_single.txt", "prompt_spellblade_single.txt").replace("prompt_assassin_sheet.txt", "prompt_spellblade_sheet.txt")
    text = text.replace("with the face, the mask, the hair and the clothes identical in every panel", "with the face, the hair and the clothes identical in every panel")
    text = text.replace("(the mask, the hair, the cape)", "(the hair, the face, the cape)")
    text = text.replace("Her or his face looks the same in every panel.", "Her face looks the same in every panel: the same calm, slightly proud, faintly smiling look.")
    text = text.replace("in her or his own colours", "in her own colours").replace("her or his own colours", "her own colours")
    text = text.replace("Method B (six single images) is in prompt_spellblade_single.txt; the pilot compares the two.", "Method B (six single images) is in prompt_spellblade_single.txt; the Assassin's idle was made with this sheet, so use it first.")
    assert "assassin" not in text.lower().replace("the assassin's idle", ""), [l[:100] for l in text.splitlines() if "assassin" in l.lower()]
    return text


for src, dst in (("prompt_assassin_sheet.txt", "prompt_spellblade_sheet.txt"), ("prompt_assassin_single.txt", "prompt_spellblade_single.txt")):
    t = convert((G / src).read_text(encoding="utf-8"))
    (G / dst).write_text(t, encoding="utf-8")
    print("wrote", G / dst, len(t), "chars")
