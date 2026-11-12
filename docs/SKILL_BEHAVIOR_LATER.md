# What the skills actually do: decided later, with the game engine

**Decision (the user, 2026-11-03):** the skill effects and what they actually do (damage, statuses, durations, chances, costs, cooldowns, who they hit) will be implemented much later, with the game engine, and decided then. Until then the test page only DRAWS the skills. **Every number the page uses is a placeholder, not a decision.** The art, the animations and the `skill-fx/1` jsons (`docs/FORMATS.md`) are the visual spec only.

This file lists, skill by skill, what is drawn, what the user has actually said about its behaviour (their own words, kept as they were given), what the test page pretends so that the effects have something to show, and what the engine has to decide. When the engine work starts, read this file first.

## How to read the tables

- **User's text** = the user wrote it as the skill's design. Treat as the starting point of the real rules.
- **Placeholder** = I (Claude) made it up so the test page could show the effect. Not confirmed by the user. Replace freely.
- Where a placeholder lives in the page is given in `code` names (search `source/src/warrior-vs-goblin-test.src.html`).

## The skills

### Warrior

| Skill | Drawn | User's text | Placeholder in the test page | Open |
|---|---|---|---|---|
| Thunderclap Guillotine (the jump attack) | The first version is in the page (blade crackle, a sky strike at the apex, a trail, the impact on frame 7, shake, a shock on the target; settings: the `skill-fx/1` example in `docs/FORMATS.md`). **2026-11-12: being rebuilt** with new art (the first jump looked like a monkey); the plan is in `docs/WARRIOR_SKILLS.md`. | "Jumps and crashes down with full force, dealing heavy Lightning Damage and 50% chance to apply Shocked for 3 turns." (2026-11-12) | The damage is whatever the fight scenario gives (`e.amount`); the 50% Shocked for 3 turns is drawn as the existing Shocked status (the page does not apply the numbers). | Damage formula (heavy: one of the strongest skills), lightning vs other resistances, what Shocked does, cost and cooldown. |

### Mage

| Skill | Drawn | User's text | Placeholder in the test page | Open |
|---|---|---|---|---|
| Firebolt | Done (painted look default, code look kept). | None recorded. | Sets Burn: one stack per hit, up to 3, 3 turns, refreshed (`burns: true`, the "Firebolt sets the target ablaze" box). Damage is the scripted amount (x1). | Does it apply Burn at all? Chance? Damage. |
| Ice Shard | Done (painted look default since 2026-11-01, code look kept). | None recorded. | Applies Chilled for 2 turns (the "Ice Shard chills the target for 2 turns" box, `applyChilled(T, 2)`). Damage x1. | Does it chill? Chance? Duration? |
| Deep Freeze | Done (painted default). | None recorded. | Freeze chance 100% (`fbChance`). A frozen target loses its next turn (`frozenTurn`), then the block shatters; when the target resists, the build-up stops at 62% and the ice breaks. If the frozen target dies the block shatters first. No damage. | Chance and who can resist, duration, bosses immune?, diminishing returns, whether damage breaks it. |
| Shatter Lance | Done (painted default): four beats on four frames, the charge frames held longer. | "hurls a massive spire of crystallized magic for heavy magical damage; on a Frozen target +100% damage and Reduce Magic Def (-25% for 2 turns); on a target that is only Chilled a guaranteed critical hit". | Damage x1.8 (`castAct`), x2 on top on a Frozen target (so x3.6), on a Chilled target a forced crit and x1.5; on a Frozen target the lance breaks the block and ENDS the freeze (my assumption); Magic Def reduced shown for 2 turns (`applyWard(T, 2)`, the -25% is from the user's text). | Does the lance end the freeze? Is the +100% on top of "heavy" or on the base? Crit multiplier. Magic Def -25% of what, does it stack? |
| Cinderburst (the user's "Combustion Bolt") | Done (painted default). | "Blasts the target with explosive Magical Damage. If the target is suffering from Burn, instantly detonates all remaining burns". | Damage x1.7; on a burning target every stack pops and the remaining burn damage (stacks x turns left x `BURN_TICK`) is added to the number; the burns end. | Detonation formula, whether it consumes the burns, bonus per stack. |
| Pyroclasm | Done (painted default). The aura levels (30% / 60% / 100%, held until the release, frame 3 held 350 ms) are a visual choice of mine copied from the ice skills, not confirmed. | "Strikes the target with a towering inferno, dealing heavy Magical Damage and applying a potent 3 stacks of Burn." | Damage x2, sets 3 Burn stacks at once. | "Heavy" in numbers, what "potent" means (stronger stacks or just 3). |
| Barrier (passive) | Done: since 2026-11-03 a half circle of glass in front of her (it was a full bubble); cast when combat starts, half visible while combat is active, ripple on a hit, breaks when she falls, drops when the fight ends. Mirrored for the arena (tested 2026-11-03). | "a barrier that is being cast by mage at the start of combat, while combat Active I want protective Barrier, halfway visible" (the user's words; "surrounding the game" was read as "surrounding the mage"). | Only a visual. The ripple on a hit, the break and the hook list (`combat_start`, `combat_active`, `mage_hit`, `mage_defeated`, `combat_end`) are my additions. It absorbs nothing in the test. | Does it absorb damage or reduce it? How much, does it break, does it recast, does it cover only the mage or allies, does it block statuses. |

### Statuses (the page draws them, the game decides them)

| Status | Drawn | Placeholder | Open |
|---|---|---|---|
| Burn | Flames licking up the body and the ground, embers, a warm tint, a BURN xN number. | A stack lasts 3 turns (`BURN_TURNS`), up to 3 stacks (`BURN_MAX`), 3 damage per stack per turn (`BURN_TICK`). | Tick timing (start or end of turn), stacking and refresh rules, damage type, can it be removed. |
| Chilled | Frost on the ground, a faint aura, a cool tint, a CHILLED number. | 2 turns (`T.chilled.turns`). | What it does itself (slows? lowers speed or defence?). Today it only matters for the Lance's guaranteed crit. |
| Frozen | Deep Freeze's block; the target shows through it. | The target loses its next turn; thaws after it. | See Deep Freeze. |
| Magic Def reduced | The cracked ward (a ring of broken arcs and runes) round the target. | -25% for 2 turns (from the user's Lance text). | Stacking with itself, applies to which damage. |

## Questions the engine has to settle for all of it

1. The damage formula: base, scaling with a stat, magic versus physical, resistances, a crit chance and a crit multiplier, a damage range.
2. Turn order and speed, and when "a turn" counts down a status (before or after the holder acts).
3. Costs and limits: mana or energy, cooldowns, charges, the number of skills per fight.
4. Targeting: single target only today, are there area, party or random targets (the party of four is planned).
5. Resisting: chances, immunities (bosses), diminishing returns on freeze, cleanse and dispel.
6. Interactions: Burn on a Chilled target, a Frozen target taking fire damage, a Barrier against statuses.
7. What the Barrier does (see the table) and what the passive is called in the skill list.
8. PvP and the arena: the mage can be the enemy and then faces left; everything is mirrored. The visuals handle it (the Barrier was tested mirrored on 2026-11-03; the other skills use `T.dir` and the stage rectangles, but were not all tested with the mage on the right). Rules for two player characters facing each other are open.
9. Where the numbers live in the game: data files per skill, not code, so they can be tuned without touching the animation.

## Where the placeholders are in the test page

`BURN_TURNS`, `BURN_MAX`, `BURN_TICK` (before `applyBurn`); the damage multipliers and the Frozen, Chilled and Burn rules in `castAct`; `frozenTurn`; `applyChilled`, `applyWard`, `clearChilled`, `clearWard`, `clearBurn`; `afterHit` (what each skill leaves on the target); the skill list `SKILLS`; the boxes "Firebolt sets the target ablaze", "Ice Shard chills the target for 2 turns" and the "Freeze chance" slider in the skill panel. The `skill-fx/1` jsons written by the panel carry the same placeholders in their `rules`, `statuses` and `hooks` (marked as notes there).

## The Rogue's Backstab (placeholder numbers, 2026-11-04)

In the test page the Rogue's attack is the Backstab (`backstabAct`, constants in `BS`): damage is the scripted amount x1.5 (`BS.damage`), always shown as a critical hit; it only misses when the scenario says the target dodges (then it plays and the target slips away). What the skill really does (damage, whether it ignores defence, a bonus from behind or against a debuffed target, cost, cooldown, what happens to a target that is already facing away, whether she stays behind the target after the strike) is for the game's designer. The visuals: she dissolves into shadow at home, steps out of the shadow behind the target (mirrored), stabs on the hit frame, dissolves again and steps out at home. The user's idea was only "disappears, then reappears behind the target"; stepping back to her place is my recommendation, nothing about it is decided.

## The Rogue's Shadow Shiv (placeholder, 2026-11-04)

The user's text: "A quick stab that automatically Critical Hits a target suffering Reduce Physical Def." In the test page the Rogue's attack select can use it: a quick dash, a stab and a slide back (0.42 s). The page has no Reduce Physical Def status, so the box "The target suffers Reduce Physical Def" stands in for it: ticked, the stab is an automatic critical hit worth the scripted amount x1.5 (`SHIV.crit`); unticked, it is the scripted amount (a normal hit, or the script's own critical hit). Open: how long the status lasts, whether it is shown on the target (the mage's Magic Def ward is the model), what a critical hit is worth, the damage of a normal Shadow Shiv, cost and cooldown.

## The Rogue's Static Stiletto (placeholder, 2026-11-04)

The user's text: "A lightning-charged stab dealing Lightning Damage and 25% chance to apply Shocked." In the test page: the scripted amount as damage (a lightning-coloured number, no bonus), a 25% roll (`Math.random() < 0.25`, or always with the box "Static Stiletto always applies Shocked") to apply Shocked for 2 turns (`applyShocked`: only drawn, a faint blue glow and small arcs on the target). Open: what Shocked does (a stun, a speed or accuracy reduction, a chance to lose the turn, extra damage from lightning), how long it lasts, whether it stacks or refreshes (the page refreshes), whether Lightning Damage is a separate damage type with resistances, the damage of the skill, cost and cooldown. The skill names are placeholders (the user: only the effects must stay).

## The Rogue's Umbral Shroud and Abyssal Backstab (2026-11-04)

**Umbral Shroud** (the user's text: "Cloaks you in shadow, dealing Dark Damage and granting Elusive (+20% Dodge, +10% Speed for 2 turns)"): the animation of the first Backstab (she dissolves at home, reappears behind the target, strikes, dissolves, steps out at home). In the page: the scripted amount as Dark Damage (a violet-glow number, class "dark", no bonus), a dark bloom with violet shards and a ring on the target, and the Elusive status on HER: drawn only (a faint dark mist and wisps round her, a dark pool on the ground, a slightly darker sprite, an ELUSIVE number), ticked by `tickStatuses` and lasting through her next two turns (the turn that applied it does not count). The +20% Dodge and +10% Speed are NOT simulated: the fight script decides the dodges. Open: do Dark Damage and Elusive stack or refresh (the page refreshes), does Elusive's dodge apply to every attack, the damage of the skill, cost and cooldown, whether the strike can miss.

**Abyssal Backstab** (the user's text: "A brutal strike from the dark dealing bonus damage against Blinded or Reduce-Physical-Def targets"; "more powerful and dramatic", a strike from the air with both weapons on the target's upper back): BUILT in the page 2026-11-04 (`Animations/Rogue/abyssal_backstab/`). Placeholders in the page: damage x2 the scripted amount, x1.5 more against a Blinded or Reduce-Physical-Def target (the page has neither status: two boxes would stand in, like the Shadow Shiv's), a bigger number, a heavy shake and a hit-stop. Open: how much bonus damage, what Blinded is (a status the page does not have yet), whether it also applies the target's Reduce Physical Def, cost and cooldown.

## The Rogue's Winter's Kiss, the dagger throw (was "Glacial Flurry", name chosen by the user 2026-11-04, built in the page the same day with placeholder numbers; the dagger counts as ONE hit on arrival, the way back is only drawn: the user agreed)

The user's text: "A flurry of frost-coated strikes dealing Ice Damage and 25% chance to apply Chilled", changed by the user into a thrown frozen dagger that flies to the target and back (same effects). Plan for the page: the scripted amount as Ice Damage (an ice-coloured number), a 25% roll (or always with a box) for `applyChilled(T, 2)`, the status the mage's Ice Shard and Shatter Lance already use (a Chilled target takes a guaranteed critical from the Lance). Open: what Chilled does besides that, damage of the skill, cost and cooldown, whether the dagger hitting twice (there and back) counts as one hit or two (my default: one hit on arrival, the way back is only drawn), whether Ice Damage is a separate damage type with resistances.

## The Rogue's Permafrost Execution, her sixth and last skill (2026-11-05, BUILT in the page the same day with the placeholders below)

The user's text: "A finishing blow of Ice Damage. If the target is Chilled, consumes it for a chance to Freeze them (skips their next action); otherwise, or if that fails, applies Chilled instead." Plan for the page (placeholders): the scripted amount x1.5 as Ice Damage (the frost-coloured number), then: IF the target is Chilled (the page's real status, `applyChilled`, or a box standing in) the Chilled is consumed (`clearChilled`) and a roll (placeholder 50%) decides whether the target is Frozen (the mage's freeze look, `startFreeze`; the fight script already skips a frozen target's next action, check); otherwise, or if the roll fails, `applyChilled(T, 2)`. Open: the chance to Freeze (and whether it rises with something), what "finishing blow" means in numbers (a bonus against low HP? a flat bonus?), whether the consumed Chilled still deals the damage, how long Frozen lasts, whether a Frozen target can be Chilled again at once, immunity of bosses to Freeze, cost and cooldown.

## The fire slime's skills (2026-11-08; every number is a placeholder, the game design decides)

The game design's list: Ember Spit (basic), Molten Drip, Cinder Burst, Magma Slam (replaces Flame Splash), Magma Eruption, Inferno Bounce. In the page:
- **Ember Spit** (BUILT): ranged Fire Damage with a 25% chance of Burn (one stack, 3 turns).
- **Cinder Burst** (BUILT, the mage's Cinderburst on the spit's animation): Fire Damage x1.7 plus what every Burn on the target had left (stacks x turns left x 3), the burns are consumed; it does not set Burn.
- **Magma Slam** (BUILT): melee Fire Damage x1.6 with a 50% chance of Burn; a target that dodges lets it land on empty ground.
- **Magma Eruption** (BUILT 2026-11-08; 2-turn cooldown): Fire Damage x2.4 and 2 Burn stacks; the target is thrown up and falls back but is NOT stunned (the user: "only damage and Burn, no stun").
- **Inferno Bounce** (BUILT 2026-11-08; 2-turn cooldown): Fire Damage x3.0 from above (the slime's strongest) plus a second hit of x0.5 on the bounce (the user KEPT it, 2026-11-08), 1 Burn stack; the warning shadow gives the target a chance to dodge (a dodge avoids both hits).
- **Molten Drip**: not designed yet.

## The ice slime's skills (2026-11-08; every number is a placeholder, the game design decides; names are mine)

The five slots mirror the fire slime's: **Frost Spit** (basic, ranged, 25% Chilled for 2 turns), **Glacial Lance** (the mage's Shatter Lance on the spit animation, x1.7, a guaranteed critical x1.5 more on a Chilled target and that chill is consumed; it does not chill), **Glacier Slam** (melee, x1.6, 50% Chilled), **Permafrost Eruption** (2-turn cooldown, x2.4, always Chilled, no stun, the target is thrown up), **Blizzard Bounce** (2-turn cooldown, x3.0 plus a second hit x0.5, always Chilled; a dodge avoids both). All BUILT in the test page.

### Block (added 2026-11-10, the user's rule; details in docs/BLOCK.md)

"Blocked hit cannot crit and block reduces the damage taken by 20% (may change in the future)." In the test page: `BLOCK_REDUCE = 0.2` (one constant), a blocked hit is never a crit, the number reads BLOCK n, the blocker plays a short block pack and a half circle of glass meets the blow. The page only draws it. Open for the engine: the chance to block (and whether it stacks with Dodge), which weapon or item is needed (main hand, off hand, shield), whether statuses (Burn, Chill, Shock...) still apply through a block, whether a block can be broken, how it works against skills that cannot be blocked (area spells, the Elite's Rockfall Drop and Earthbreaker?).

## The Slime King's numbers (2026-11-11, placeholders in the page: KING_POW, KING_HEAL)

Damage is relative to the turn's damage: Radiant Ooze x1.0, Royal Decree x1.18 (the element's own status chances), Crown Slam x1.6 then x0.3, Kingdom's Wrath x3.18 split in four hits (fire, ice, lightning, dark, no statuses yet), Absolute Judgment x3.55 (one holy hit); Royal Restoration heals 20% of the maximum HP; the 'alternate' order (ooze, decree, crown slam, ooze, decree, wrath, heal below 70% HP, judgment) stands in for the cooldowns (0, 0, 1, 2, 2). The engine decides all of it.
