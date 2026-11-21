CLERIC SKILLS: THE PROMPTS (started 2026-11-21)

One folder per skill (01_radiant_smite_v2 first: the first Radiant Smite sheet had the arms swapped, so it is being redone), each with the picture to attach, the prompt to paste and what to check. The Cleric has six base skills (docs/CLERIC_SKILLS.md); they are sent one by one, as the Warrior's and the Rogue's were: I propose the choreography, write the prompt, you generate the sheet, I cut it, build its effects in code and put it in the test page, you judge it in motion.

The prompts are built by Animations/Cleric/source/make_cleric_skill_prompts.py from the character paragraph Animations/Cleric/source/cleric_description.txt (rerun it after a change). What is special about the Cleric's skills:
- ONE weapon: the mace (Templar) or the wand (Occultist) in the FAR hand; the shield or the orb in the NEAR hand, which stays in its guard at the chest. Every base skill must work for BOTH branches, so the gestures work with a mace and with a wand.
- The sheet is bare fists in poses: no weapon, no shield, no light. The items are layers (you mark the hands later) and the effects (holy light, the heal, the barriers) are code.
- Buffs and debuffs (Purified, Condemned, Weaken and the rest) are NOT drawn: they come later.

Save the sheets as inbox/cleric_<skill>_sheet.png (the exact name is in each kit's check file).
