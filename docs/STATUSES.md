# Buffs and debuffs: the full list (2026-11-26)

The user asked for every buff and debuff in the game before the animation side covers them. **This file is only the list; nothing new is drawn yet.** The source is the game itself (the sibling project `C:\Users\Anil\Desktop\InfinityTower`): `game_design.md` sections 8, 13.2, 26 and 27.2, checked against the code in `src/App.jsx` (`STATUS_BASE`, `BUFF_STATUSES`, `DEBUFF_STATUSES`, `countDebuffs`, `cleanseRandomDebuff`, `dispelRandomBuff`, `applyBuff`, `applyDebuff`). The game doc's own section 8 says "see v2 section 8" for the older statuses; that v2 file is not in the project, so their effects below are read from the code.

**Drawn in the test page today** (each has an icon under the HP bar, `HUD_STATUS` / `HUD_ORDER`, see `docs/HUD.md`): Burn, Chilled, Frozen, Shocked, Magic Def down, Elusive, Defense up (the Elite's Stone Guard). The barrier glass (the Mage's Barrier, the Cleric's Aegis and Covenant) is drawn but has no icon. Everything else below has neither a look nor an icon.

## The rule: what stays on a fighter (the user, 2026-11-26)

"I don't want all the buffs and debuffs visible all the time." **The look stays on the fighter for the whole status only for:** the Barrier and shield effects (the Mage's Barrier glass, the Cleric's Aegis and Covenant), the Rogue class's Elusive (Rogue, Assassin, Spellblade), Burn, Chilled, Frozen and Shocked. **Every other status shows its look once, when it is applied, then the look goes**; the status itself, its turns and its icon under the HP bar stay until it runs out.

- Done in the page: **Magic Def down** (the cracked ward flashes, cracks and fades about 1 s later, `WARD_FADE`), **Defense up** (the Elite's Stone Guard: the shield's light fades when the cast ends instead of pulsing for 2 turns; the user confirmed 2026-11-27: it is a Defense up, not a shield effect, keep it fading).
- For the statuses still to be drawn: give each an application effect only, unless it is one of the kept list above.

Numbers are the game's base values; skills scale them with rarity. Timed statuses count down on the bearer's own turn.

## Buffs (14)

| # | Buff | What it does | Who gives it today | In the page |
|---|---|---|---|---|
| 1 | Barrier (shield) | Absorbs damage, capped at 2x max HP; ends after 2 turns or when used up | Cleric (Aegis of Retribution, Spiteful Covenant, ally shelters), Mage's Mana Shield and Warrior's Colossus Fortitude at battle start | glass, no icon |
| 2 | Reflect | Part of a Cleric barrier: sends a share of the damage back | Cleric barriers | no |
| 3 | Mana Shield | Mage passive: a barrier at battle start and +15% action-bar speed | Mage | no (the Barrier glass) |
| 4 | Iron Faith | +healing received and less critical damage taken, 2 turns | Cleric (Blessed Resilience) | no |
| 5 | Elusive | +20 Dodge and x1.10 speed | Rogue | yes |
| 6 | Momentum (Juggernaut) | +speed per stack (max 3), a stack for every debuff the Warrior lands | Warrior passive | no |
| 7 | Alacrity | Action bar fills x1.25 faster, 2 turns | branch skills | no |
| 8 | Surge | Next damaging cast +30% damage and +25% crit chance per stack (max 3), then consumed | branch skills (Elementalist) | no |
| 9 | Fortified | +20 Damage Resistance and +20 Block Rate, 2 turns | branch skills (Knight) | "Defense up" is the nearest |
| 10 | Regeneration | Heals 1% max HP per stack each turn (max 3 stacks), 3 turns | branch skills | no |
| 11 | Warded | Can't be debuffed, 2 turns | branch skills (Arcanist's Hallowed Ward) | no |
| 12 | Taunt | Enemies must target this hero (party fights), 1 turn | branch skills (Knight) | no |
| 13 | Bonded | A share of the bearer's damage goes to the Templar instead, 2 turns | Templar's Sacred Bond | no |
| 14 | Hidden | +30 Dodge; the next damaging cast is a sure, unavoidable crit, then it ends | Assassin's Vanish | no |

Boss only: **Defiant Stance** (the Orc Warlord's Blood Debt phase, can't be stripped; a full boss mechanic, `game_design.md` 13.6).

## Debuffs (22)

| # | Debuff | What it does | In the page |
|---|---|---|---|
| 1 | Burn | 0.33% of the bearer's max HP per stack each turn, max 5 stacks, goes through shields | yes |
| 2 | Bleed | Physical twin of Burn (own stacks, so both can be on at once) | no |
| 3 | Chilled | -20% speed | yes |
| 4 | Frozen | Skips its next turn (then can't be Frozen again on the very next one) | yes |
| 5 | Shocked | Takes +15% damage from everything | yes |
| 6 | Magic Def down | Magical DEF reduced (Shatter Lance: -25%, 2 turns) | yes |
| 7 | Physical Def down | Physical DEF reduced | no (only a test box in the Rogue's panel) |
| 8 | Blind | -20% accuracy | no (only a test box) |
| 9 | Weaken | -20% speed and accuracy | no |
| 10 | Slowed | -10% speed (comes with Physical Def down from the Rogue's Conductive Hypothermia: "chilled to the bone") | no |
| 11 | Purified | Deals 15% less damage | no |
| 12 | Condemned | Takes back a share of the damage it deals (stacks only with Lingering Malice, up to 3) | no |
| 13 | Decay | -30% healing received, and dark damage after every cast it makes, 3 turns | no |
| 14 | Stasis | Its cooldowns don't tick on its next turn | no |
| 15 | Doomed | Can't be buffed, 2 turns | no |
| 16 | Nullified | Strips one random buff, then Doomed for 2 turns | no |
| 17 | Rooted | -20 Dodge, 2 turns | no |
| 18 | Guard Break | -12 Block Rate, 2 turns | no |
| 19 | Pinned | -10 Dodge and -10 Block Rate, 2 turns | no |
| 20 | Leech (Leeching Curse) | Whoever hurts the bearer heals 10% of it, 2 turns | no |
| 21 | Marked | The marker's crits on it deal +25% crit damage, 2 turns | no |
| 22 | Trapped | Springs at the start of its next turn: 60% of the trapper's ATK, Pinned, pushed back on the action bar | no |

Not shown to the player (internal timers): Freeze immunity, Stasis immunity.

Not combat statuses, so not in the list: the dungeon rest-point buffs (+15% ATK, +15% HP and DEF, +10% speed, ... for the rest of a dungeon run) and the passives' one-shot "pending" bonuses (Heavy Impact, Spellweaver's Flow, Pyromancy Focus, Lethal Cadence).

## What is left to decide

28 of the 36 statuses (and Defiant Stance) have no look and no icon in the page yet. The user's rule from 2026-11-13 still holds until they say otherwise: the looks and icons of the statuses are done in one pass, later, so this list is the starting point for that pass; the rule above says which of them get a lasting look: none of the 28 needs one of its own (Reflect and Mana Shield already show through the barrier glass).
