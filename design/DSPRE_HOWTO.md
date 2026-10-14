# Editing Ondine's maps with DSPRE

**ROM to open in DSPRE:** `C:\Users\Erick\RomHacking\NewRegion\Ondine_DSPRE.nds`
(DSPRE: `C:\Users\Erick\RomHacking\DSPRE2\DSPRE.exe`)

## The loop
1. Open `Ondine_DSPRE.nds` in DSPRE, make your edits, then **Save ROM** (overwrite the same file).
2. Tell Claude "pull my DSPRE edits". Claude runs `python3 scripts/dspre.py pull`, rebuilds, and commits.
3. Before your next DSPRE session Claude runs `python3 scripts/dspre.py push`, which gives you a
   fresh `Ondine_DSPRE.nds` containing everything (your maps + all scripted changes).
   Always pull before the next push, or unpulled edits are lost (push refuses to overwrite them).

## Safe to edit in DSPRE
- Map editor: terrain, permissions/collisions, buildings, models, textures
- Matrix editor: island layout, which maps sit where
- Header editor: map music, weather, camera, map type, name (location) id, flags
- Event editor: warps, NPCs/overworlds, signs, triggers
- Script and text editors work too (they come back into the source), but tell Claude what
  you changed so nothing gets mixed up.

## Don't edit in DSPRE (made by Claude's scripts — the build would undo it)
- Trainers, wild encounters, Pokémon data, starters, moves, items
- Trainer/overworld sprites
- DSPRE's "Patches" / "Expand" menus (they change game code)

If you do, `pull` prints a WARNING naming what will be lost.
