# Block (all characters and monsters), 2026-11-10

The user noticed that the game has a **Block** that no character has an animation for. The game rule (the user's words): *"Blocked hit cannot crit and block reduces the damage taken by 20% (may change in the future)."* The numbers are the engine's; the test page only DRAWS a block (like the statuses). `BLOCK_REDUCE = 0.2` is one constant in the page.

## Decisions (the user, 2026-11-10)

- **A block is a REACTION, like the Dodge** (not a stance): when a hit lands, it may be blocked; the block animation plays for about half a second INSTEAD of the Hit animation. The page times it so that the guard is already up when the blow lands (the pack's `idx`: the block frame, like the dodge's `evadeFrame`).
- **One look for everybody: a short, subtle HALF CIRCLE OF GLASS** in front of the blocker, on the side the blow comes from (the look of the mage's Barrier, `BR_RGB`), with a ripple ring and a few sparks where the blow lands. For the Mage her existing Barrier flares (to do when her block exists). No white hit flash and no hit pose for a blocked blow, only a small recoil and a faint brighten.
- **The guard, by hand or by weapon** (the user's idea): the blocker raises its main-hand or off-hand weapon, or the shield.
- **Start with the Elite Slime**, from frames it already has (no new art), to prove the timing and the effect; then the other characters.

## What the page does (built 2026-11-10)

- The turn flag `block: true` (scenario **"Warrior wins, the monster blocks two strikes"**, `MBLOCK`: a crit that is blocked, then a plain hit that is blocked, then the finish). A blocked hit: `blockAmount` = amount x (1 - BLOCK_REDUCE), never a crit (`CRIT` is dropped, the log says "the critical hit is cancelled" and there is no crit shake), the number reads **BLOCK 16** (class `.num.block`), the log says "(blocked: 20% less damage)".
- `blockFx(T, sd, tHit)`: the half circle (a radial glow clipped to the attacker's half, a rim arc, a highlight, a glow on the ground in front of it), fading in 70 ms, held to 180 ms, gone by 560 ms; at the blow a flash, a ring spreading on the glass and eight sparks. It sizes itself from the blocker's sprite (a monster: `monEl`, radius 0.46 of its cell) or its unit (a fighter: 0.5).
- `blockSpec()` / `blockPre()` / `monBlock()`: a monster's block comes from `MONSTERS[key].block = { pack, order, holds, fps, idx }`. The pack may be a strip of its own (`slot block`, not built yet) or **frames of another pack played in an order**: **the Elite's Block = the Stone Guard's frames 2, 3, 4, 5, 3, 6 at 14 fps** (the shield floats up in front of the face; the face frame is the block frame, the 3rd played; it lands about 165 ms after the start). While it plays `MON.blocking` stops `monOnHp` from playing the hit pack.
- A **Block (loops)** preview button in the monster preview row (shown for a monster that has `block`).
- **Wired so far:** the warrior's BASIC attack on a monster with a block (`act()`). **Not wired yet (each needs the same few lines: start the block pack early, `blockAmount`, `blockFx`, no crit):** the Mage's cast (`castAct`), the Rogue/Assassin/Spellblade skills (`rogueAct`), the Elite's own attacks and the other monsters' attacks on a character, and a character BLOCKING (the Warrior has no block pack yet, so a blocked monster blow on him would only show the glass, the number and the log).
- Tested in the browser pane (clock stubbed): the preview's frame order (2, 3, 4, 5, 3, 6 of the guard strip), a look at the glass at the blow (a rim arc, the ring, the shield up at the face), the scenario ("slashes Elite Slime for 18 (blocked: 20% less damage, the critical hit is cancelled)", "for 16 (blocked: ...)", then the defeat), no console errors.

## What is still to do (not started)

1. **A block sheet per character** (6 frames, 12 to 14 fps, the block frame marked): proposed poses, the user to correct: **Warrior** the sword held across the body; **Rogue, Assassin, Spellblade** both blades crossed in front; **Mage** the staff across the body (and her Barrier flares); the Elite is done from its Stone Guard frames (a real strip of its own is optional). Prompts to write per character (the ChatGPT lessons in `docs/MONSTERS.md` apply: say what each part does, ask a small creature with margins). Each pack gets a slot `block` in `build.py` and a placement with `blockFrame`.
2. **Wire the block into every attack path** (the list above) and into a character's own defence (the character is the target: `T === FIGHTERS.W`: play his block pack at the right moment instead of the hit pack).
3. Other monsters' blocks (which monsters can block is the user's decision; the Elite fits).
4. Engine questions: the chance to block, whether Block stacks with Dodge or other defences, what weapon is needed (the user's idea: main-hand or off-hand weapon), whether a blocked hit still applies statuses (Burn, Chill...): see `docs/SKILL_BEHAVIOR_LATER.md`.
