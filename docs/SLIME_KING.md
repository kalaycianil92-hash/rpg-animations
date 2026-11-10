# The Slime King (the boss of the slimes), design 2026-11-10

The user's design, discussed with Claude on 2026-11-10 (the numbers of the game are the engine's; the page only draws them).

## The creature (the user's decisions)

- **Considerably bigger** than the player characters (the page draws it about 2x the size of the other monsters, roughly 1.5 to 1.7 times the Warrior's height; one per-monster size value, adjustable with the Monster size slider).
- **IVORY-WHITE**, **wearing a golden crown** and **holding a big staff suitable to its size, GOLDEN, matching the crown** (the user, in the answers: "his staff should also be golden matching the crown").
- **The staff is held by a FLOATING GLOVE** (no arm, no stalk), the same idea as the Elite's floating fist: the glove and the staff move as one rigid piece in every animation. A white glove with a gold cuff.
- **Face: calm and regal** (half-lidded eyes, a gentle confident closed smile, a slow heavy breath), the opposite of the grumpy Elite.
- **The body never changes colour for a skill** (the user's earlier idea was dropped as too much work): the elements are shown by the EFFECTS only. A cheap option for later: the staff's crystal glowing in the element's colour while it charges (a small code glow, like the Stone Guard's shield light).
- **Treasure:** defeating the Slime King unlocks the game's **treasures feature**, so the boss stage gets **a pile of treasure behind the slime as a prop**. The user: "we can do that prop after the animations". It belongs to the boss room look (the dungeon's Throne of Roots, `docs/STAGES.md`).
- It keeps the family construction (a low dome wider than tall, a wavy skirt on the floor, the face in the same place, three-quarter view turned right, matte hand-painted style, a thin dark outline); the earlier decision 'no holy slime' (docs/MONSTERS.md, 2026-11-09) stands: the King is the one creature that is holy, and it is the boss.

## The skills (the user's table, and the plan the user agreed to)

The first design (all holy except one):

| Power | CD | Attack | Type |
|---|---|---|---|
| 44% | 0 | Radiant Ooze | Holy magic |
| 52% | 0 | Royal Decree | Holy magic |
| 84% | 1 | Crown Slam | Physical |
| 92% | 1 | Sovereign Splash | Holy magic |
| 140% | 2 | Kingdom's Wrath | Holy magic |
| 156% | 2 | Absolute Judgment | Holy magic |

**Second thought (the user): the King can use ALL elements, with holy added, and one skill becomes a HEAL.** The plan Claude proposed and the user accepted ("my proposal", 2026-11-10):

| Power / CD | Skill | Type | What the page shows |
|---|---|---|---|
| 44% / 0 | **Radiant Ooze** | Holy | a spit of golden-white ooze from its mouth (a projectile) |
| 52% / 0 | **Royal Decree** | Elemental, rotating | the King points its staff and a bolt of the element flies: **fire, ice, lightning, dark in turn** (the effect changes, not the body) |
| 84% / 1 | **Crown Slam** | Physical | it leaps and slams its crown down on the target (heavy dust and debris like the Elite's Rockfall Drop) |
| (92% / 1) | **Sovereign Splash becomes the HEAL** | Heal (holy) | it douses itself in holy ooze: a golden glow, sparkles, the HP bar goes up, a green +N number (the heal amount is the engine's) |
| 140% / 2 | **Kingdom's Wrath** | All four elements | the staff is raised and fire, ice, lightning and dark strike in turn as one combo |
| 156% / 2 | **Absolute Judgment** | Holy | the staff is raised: a pillar of light from the sky and a judgment ring, the finale |

The King then has two basic skills, one heavy physical, one heal and two ultimates. Names are placeholders (the heal may be renamed, e.g. 'Royal Restoration').

## The animations needed (about nine body sheets; blocks later)

Idle (a slow heavy breath), Hit, Death (a dramatic collapse: the crown, the glove and the staff fall), Dodge, **Spit** (Radiant Ooze), **Staff point** (Royal Decree), **Staff raise** (Kingdom's Wrath and Absolute Judgment: one pose, different effects), **Crown Slam** (the leap), **Heal** (a self-buff pose like the Stone Guard). The Block (a reaction like the Elite's, `docs/BLOCK.md`) comes later, with the other characters'.

## The effects (what exists and what is new)

- **Reused from the four elemental slimes** (painted effects and act code exist): the fire, ice, lightning and dark bolts and bursts, for the Royal Decree and the Kingdom's Wrath. The acts read the element from the monster (`MONSTERS[key].vfx`), so they need a per-skill element (`e.elem`) instead.
- **Reused from the Elite:** the physical dust, debris and ground cracks (the painted `eb_*` pieces) for the Crown Slam.
- **New, painted:** the HOLY set (the only element with no pieces yet, besides `holy_aura.png`): the Radiant Ooze projectile, a holy impact burst, the pillar of light, the judgment ring, the heal's glow and sparkles. A glow sheet on pure black, drawn additively like the fire, lightning and dark sets.

## What the page needs (engineering, not started)

- A **size per monster** beyond 140% (the slider's limit) and a per-monster size default (planned since 2026-11-01).
- The **Warrior's approach distance and the dodge x** measured to the King's FRONT EDGE, not its middle (its body is 2x as wide), and the effects of the King's own attacks scaled by its size (they use the character width today).
- A **per-skill element** for the acts; a **heal** (a self-buff act, HP goes up, a green +N number); a boss HP bar.
- The tall staff must fit the 512 cell: the base is drawn 350 px wide as for every slime, the staff about 1.4 x the dome plus the crown.
- The stage has about 3.5 character widths of height above the floor, so a King of about 2 widths with its staff fits; check the staff against the top edge.

## Steps

1. **The look: `Animations/SlimeKing/source/slime_king_reference_prompt.txt` (WRITTEN 2026-11-10, waiting for the user's picture).**
2. The idle prompt (from the Elite's), then hit, death, dodge, then the six skills' sheets; the holy effect sheet; the boss stage prop (the treasure pile) last.
