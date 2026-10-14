# Ondine Archipelago — Region Design (v0.1)

A chain of tropical-to-arctic islands in a warm southern sea. You hop island to island
by ferry, sandbar and bridge, and later by Surf and Fly. Pokémon from **every generation (1–9)** live
here together. Every island has a gym: **8 Inner Isles** for the badge quest and
**8 Outer Isles** after the League (16 gyms total, using all of HeartGold's gyms).

## Build rule: reuse HeartGold's slots
Each new place **replaces** an HGSS town or route (like High Hill Island did with Sinnoh), so
story flags, gym scripts, badge checks and the Kanto post-game unlock keep working.
Gym types follow the gym **buildings** they reuse, so the interiors don't need rebuilding (they can still change later).

## Map

```
                         ~~ OUTER ISLES (post-game) ~~
     Basalt  Coralline  Stormcap  Bloomhaven  Mire   Mirage   Cinder   Tidecrown
     (Rock)  (Water)    (Elec)    (Grass)   (Poison)(Psychic) (Fire)   (Final)
        \________\________\_________|_________/_______/________/________/
                                    |  Ferry: S.S. Gull
                          ▲ CROWN ISLE ▲  (Pokémon League, volcano peak)
                                    |
        FROSTVEIL ─── sea route ─── DRAKESPIRE
        (Gym 7 Ice)                 (Gym 8 Dragon)
            |                            |
       RIVETPORT ─── sea route ─── PALEMOON ISLE
       (Gym 6 Steel)               (Gym 5 Fighting)
            |                            |
       LANTERN KEY ── bridge ──── MISTVEIL
       (Gym 4 Ghost)                     |
            |                     CORALCROSS CITY
       BLOOMREEF ─── jungle path ─ (Gym 3 Normal, biggest city)
       (Gym 2 Bug)                       |
            |                     WINDRIFT TOWN
            └──────── sandbar ──── (Gym 1 Flying)
                                         |
                                 PEBBLECOVE
                                         |
                                 SALTBLOOM TOWN (home, Prof. Maren's lab)
                          ~~~~~~~~ open sea ~~~~~~~~
```

## Inner Isles → HG slot they replace

| # | New town | Replaces | Gym type | Leader | Theme |
|---|---|---|---|---|---|
| — | Saltbloom Town | New Bark Town | — | — | Beach hometown; lab with starters from every region |
| — | Pebblecove | Cherrygrove City | — | — | Fishing village, first Pokémon Center |
| 1 | Windrift Town | Violet City | Flying | **Kestrel** | Cliff-top town, windmills, gliders |
| 2 | Bloomreef | Azalea Town | Bug | **Lumi** | Jungle island, bug-catching festival |
| 3 | Coralcross City | Goldenrod City | Normal | **Sunny** | Big port city; Radio Tower → Surf Shop Tower |
| 4 | Lantern Key | Ecruteak City | Ghost | **Wren** | Lighthouse ruins; Burned Tower → Sunken Shrine |
| 5 | Palemoon Isle | Cianwood City | Fighting | **Tomo** | Surf-only island, beach dojo |
| 6 | Rivetport | Olivine City | Steel | **Anvila** | Shipyard; sick Ampharos → sick Lapras |
| 7 | Frostveil | Mahogany Town | Ice | **Yuki** | Snowy north island, villain hideout under the souvenir shop |
| 8 | Drakespire | Blackthorn City | Dragon | **Ryla** | Volcanic sea stacks; Dragon's Den → Dragon Reef |
| — | Crown Isle | Indigo Plateau | League | Elite Four + Champion | Volcano-peak League |

## Outer Isles (post-game, replace Kanto)
In game text the Outer Isles are called the **Ostra** region (Kanto → Ostra), and Johto → **Ondine**.

| # | Island | Replaces | Type | Leader |
|---|---|---|---|---|
| 9 | Basalt Isle | Pewter City | Rock | **Flint** |
| 10 | Coralline | Cerulean City | Water | **Nerissa** |
| 11 | Stormcap | Vermilion City | Electric | **Volt** |
| 12 | Bloomhaven | Celadon City | Grass | **Ivy** |
| 13 | Mire Isle | Fuchsia City | Poison | **Nox** |
| 14 | Mirage Isle | Saffron City | Psychic | **Sable** |
| 15 | Cinder Isle | Seafoam Islands (Blaine) | Fire | **Ember** |
| 16 | Tidecrown | Viridian City | Mixed (strongest) | **Captain Reef** (former Champion) |
| ★ | Mt. Apex | Mt. Silver | — | Final secret battle |

## Elite Four & Champion (Crown Isle)

| Trainer | Replaces | Type | Ace |
|---|---|---|---|
| Coral | Will | Water | Milotic |
| Thorn | Koga | Poison | Toxapex |
| Brick | Bruno | Fighting | Lucario |
| Nyx | Karen | Dark | Hydreigon |
| **Champion Soren** | Lance | Mixed | Dragapult + Kingdra |

## Story
- **Team Riptide** (replaces Team Rocket) believe the islands should "return to the sea".
  They want to wake **Kyogre** and flood the archipelago so only their ships rule the waves.
- Their admins **Siren, Hook, Brine and Squall** replace Ariana, Archer, Proton and Petrel. Their boss, **Admiral Wake** (just "Wake" in the game text), replaces Giovanni.
- **Lugia** (already in HeartGold) is the islands' guardian. The Whirl Islands become the
  **Abyssal Isles**, where you meet it.
- Climax: Team Riptide's flagship at the Abyssal Isles. Kyogre wakes, and Lugia (with you) calms the storm.
- The Ho-Oh / Bell Tower story becomes the **Sun Shrine**. Ho-Oh stays as the second legend.
- Raikou, Entei and Suicune roam the sea routes. Tapu Koko, Lele, Bulu and Fini guard four Outer Isles.

## Characters
- **Prof. Maren**: marine biologist, replaces Prof. Elm (uses Elm's sprite at first). Has a starter from every region.
- **Rival Kai**: cheerful, cocky island kid. Takes the starter **strong against yours, from the same region**
  (needs a code change; the rival is still Johto-based right now).
- **Kurt → Shipwright Nemo**: makes special Poké Balls from shells.

## Pokémon by island (draft, all gens mixed)

| Area | Pokémon |
|---|---|
| Saltbloom / beach route | Wingull, Pikipek, Wooloo, Crabrawler, Corphish, Skwovet, Lechonk |
| Windrift cliffs | Rookidee, Hoppip, Swablu, Fletchling, Bunnelby, Flittle |
| Bloomreef jungle | Grubbin, Cutiefly, Nymble, Sewaddle, Aipom, Fomantis, Tarountula |
| Coralcross city/coast | Alolan Rattata, Galarian Meowth, Trubbish, Yamper, Tandemaus |
| Lantern Key ruins | Gastly, Litwick, Sandygast, Greavard, Shuppet, Phantump |
| Sea routes (Surf/fishing) | Tentacool, Wailmer, Finizen, Mareanie, Wishiwashi, Clauncher, Skrelp, Bruxish |
| Palemoon / Rivetport | Machop, Riolu, Mienfoo, Klink, Tinkatink, Pawniard, Magnemite |
| Frostveil | Snorunt, Cetoddle, Snom, Cubchoo, Bergmite, Hisuian Sneasel |
| Drakespire volcano | Larvesta, Salandit, Charcadet, Axew, Deino, Goomy, Frigibax, Jangmo-o |
| Rare / hidden | Dratini, Larvitar, Beldum, Gible, Dreepy, Rotom, Zorua, Eevee |

## Build order
1. ✅ Engine + starters from every region (tested: More → Alola → Litten)
2. ✅ Text pass: towns, Prof. Maren, Team Riptide, all 16 leaders + E4 renamed (`scripts/ondine_renames.py`; maps unchanged)
3. ✅ Wild encounters for the Inner Isles: 62 areas by zone (`scripts/ondine_encounters.py`; Kanto/Outer Isles still vanilla)
4. ✅ Gym Leaders, Elite Four, Champion, Boss Wake and all Team Riptide teams (`scripts/ondine_trainers.py`); rival's starter follows your region (`src/starters.c` + `src/field/enemy_party.c`). Regular trainers still vanilla.
5. 🔶 Battle sprites from Black 2 (`scripts/ondine_trainer_gfx.py`): Sunny=Lenora, Tomo=Marshal, Ryla=Iris, Coral=Marlon, Brick=Clay, Nyx=Caitlin, Soren=Drayden, Wake=Ghetsis, Riptide grunts=Plasma grunts, Hook=Colress, rival=Hugh. Still HeartGold art: Kestrel, Lumi, Wren, Anvila, Yuki, Thorn, Siren/Brine/Squall, Maren. Overworld: rival recoloured to Hugh, Riptide grunts to Plasma teal (`scripts/ondine_overworld_recolors.py`); Black 2's own walking sprites weren't found in a usable format.
6. Map work in DSPRE: beaches, sea routes, island shapes (the biggest job)
7. Story events: the Kyogre / Lugia climax
8. Outer Isles post-game
