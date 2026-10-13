"""Give the Ondine Gym Leaders, Elite Four, Champion and Team Riptide their teams.

- TEAMS rewrites whole parties (species + level); moves are picked from each species'
  level-up learnset (best same-type attacks, one coverage attack, one status move),
  skipping moves hg-engine marks unimplemented. The last Pokémon is the ace and holds
  a Sitrus Berry.
- RIPTIDE_SWAPS replaces Team Rocket's Pokémon in every Riptide grunt/admin team with
  sea-villain species (moved along their evolution line to fit the level). Their moves
  are re-picked the same way when the team has custom moves.
Re-runnable: TEAMS output only depends on the tables; swaps only match old species.

    python3 scripts/ondine_trainers.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAINERS = ROOT / "data/Trainers.c"
sys.path.insert(0, str(ROOT / "scripts"))
from ondine_encounters import fit  # noqa: E402

# trainer id -> [(species, level), ...]; last entry is the ace
TEAMS = {
    # Inner Isles gyms (first battles)
    20: [("PIKIPEK", 9), ("FLETCHLING", 10), ("ROOKIDEE", 13)],                                   # Kestrel, Flying
    21: [("CUTIEFLY", 15), ("NYMBLE", 15), ("DWEBBLE", 16), ("SCYTHER", 17)],                     # Lumi, Bug
    30: [("LECHONK", 17), ("SKWOVET", 17), ("LILLIPUP", 18), ("MILTANK", 19)],                    # Sunny, Normal
    31: [("SANDYGAST", 21), ("GREAVARD", 22), ("LITWICK", 22), ("HAUNTER", 23), ("MIMIKYU", 25)],  # Wren, Ghost
    34: [("CRABRAWLER", 29), ("MIENFOO", 29), ("HAWLUCHA", 30), ("LUCARIO", 31)],                 # Tomo, Fighting
    33: [("KLINK", 30), ("TINKATUFF", 30), ("MAGNETON", 32), ("BRONZONG", 33), ("STEELIX", 35)],  # Anvila, Steel
    32: [("CETODDLE", 30), ("CRYOGONAL", 31), ("SEALEO", 32), ("SNEASEL", 32), ("PILOSWINE", 34)],  # Yuki, Ice
    35: [("DRAGONAIR", 38), ("FRAXURE", 38), ("HAKAMO_O", 38), ("SLIGGOO", 40), ("KINGDRA", 41)],  # Ryla, Dragon
    # Elite Four + Champion (first run)
    245: [("AZUMARILL", 40), ("CLAWITZER", 41), ("BRUXISH", 41), ("TATSUGIRI", 41), ("SLOWBRO", 42), ("MILOTIC", 42)],   # Coral
    247: [("SALAZZLE", 40), ("SKUNTANK", 41), ("MUK", 42), ("DRAGALGE", 42), ("CROBAT", 43), ("TOXAPEX", 44)],          # Thorn
    418: [("HITMONTOP", 42), ("PASSIMIAN", 42), ("HAWLUCHA", 43), ("GURDURR", 43), ("MACHAMP", 44), ("LUCARIO", 46)],    # Brick
    246: [("UMBREON", 42), ("LIEPARD", 42), ("ZOROARK", 43), ("HONCHKROW", 44), ("HOUNDOOM", 45), ("HYDREIGON", 47)],   # Nyx
    244: [("GYARADOS", 46), ("NOIVERN", 48), ("HAXORUS", 48), ("GARCHOMP", 48), ("KINGDRA", 49), ("DRAGAPULT", 50)],    # Champion Soren
    # Team Riptide's boss
    700: [("SHARPEDO", 40), ("DREDNAW", 41), ("TOXAPEX", 42), ("KINGLER", 42), ("GYARADOS", 46)],                         # Wake
}

RIPTIDE_CLASSES = {"TRAINERCLASS_TEAM_ROCKET", "TRAINERCLASS_TEAM_ROCKET_F", "TRAINERCLASS_EXECUTIVE_ARIANA",
                   "TRAINERCLASS_EXECUTIVE_ARCHER", "TRAINERCLASS_EXECUTIVE_PROTON", "TRAINERCLASS_EXECUTIVE_PETREL"}
RIPTIDE_SWAPS = {
    "RATTATA": "CARVANHA", "RATICATE": "SHARPEDO", "ZUBAT": "WINGULL", "GOLBAT": "PELIPPER",
    "KOFFING": "MAREANIE", "WEEZING": "TOXAPEX", "GRIMER": "SKRELP", "MUK": "DRAGALGE",
    "EKANS": "CHEWTLE", "ARBOK": "DREDNAW", "DROWZEE": "CROAGUNK", "HYPNO": "TOXICROAK",
    "GLOOM": "TENTACOOL", "VILEPLUME": "TENTACRUEL", "MURKROW": "WINGULL",
    "HOUNDOUR": "CLAUNCHER", "HOUNDOOM": "CLAWITZER", "ONIX": "BINACLE", "MACHOP": "CRABRAWLER",
    "GEODUDE": "BINACLE", "VENONAT": "MAREANIE", "RATTATA_ALOLAN": "CARVANHA",
}


def load_moves():
    src = (ROOT / "data/Moves.c").read_text(encoding="utf-8")
    moves = {}
    for m in re.finditer(r"\[MOVE_(\w+)\] = \{(.*?)\n    \},", src, re.S):
        body = m.group(2)
        get = lambda k: (re.search(r"\." + k + r" = ([^,\n]+)", body) or [None, ""])[1]
        # some values are config expressions like ((X) ? (95) : (90)); the last number is the default
        num = lambda k: int((re.findall(r"\d+", get(k)) or ["0"])[-1])
        moves[m.group(1)] = {
            "power": num("power"), "type": get("type"), "split": get("split"),
            "accuracy": num("accuracy"), "blocked": "FLAG_UNUSABLE_UNIMPLEMENTED" in body,
        }
    return moves


def load_types():
    src = (ROOT / "data/Species.c").read_text(encoding="utf-8")
    types = {}
    for m in re.finditer(r"\[SPECIES_(\w+)\] = \{(.*?)\n    \},", src, re.S):
        t = re.search(r"\.types = \{\s*(TYPE_\w+),\s*(TYPE_\w+)\s*\}", m.group(2))
        if t:
            types[m.group(1)] = set(t.groups())
    return types


MOVES = load_moves()
TYPES = load_types()
LEARNSETS = json.loads((ROOT / "data/learnsets/learnsets.json").read_text(encoding="utf-8"))

# moves that make an auto-picked set bad (self-KO, two-turn charge, recoil-only gimmicks)
AVOID = {"SELF_DESTRUCT", "EXPLOSION", "MEMENTO", "FINAL_GAMBIT", "HEALING_WISH", "LUNAR_DANCE",
         "SOLAR_BEAM", "SKY_ATTACK", "SKULL_BASH", "RAZOR_WIND", "FOCUS_PUNCH", "STRUGGLE",
         "SPLASH", "CELEBRATE", "HOLD_HANDS", "TELEPORT", "TRANSFORM",
         "FLAIL", "REVERSAL", "ENDEAVOR", "LAST_RESORT", "BELCH", "DREAM_EATER", "SNORE", "FAKE_OUT"}

GOOD_STATUS = {"DRAGON_DANCE", "SWORDS_DANCE", "CALM_MIND", "NASTY_PLOT", "BULK_UP", "QUIVER_DANCE",
               "SHELL_SMASH", "SHIFT_GEAR", "COIL", "HONE_CLAWS", "CURSE", "AGILITY", "AUTOTOMIZE",
               "STEALTH_ROCK", "SPIKES", "TOXIC_SPIKES", "STICKY_WEB", "TOXIC", "WILL_O_WISP",
               "THUNDER_WAVE", "GLARE", "STUN_SPORE", "SLEEP_POWDER", "SPORE", "HYPNOSIS", "YAWN",
               "CONFUSE_RAY", "LEECH_SEED", "ROOST", "RECOVER", "SLACK_OFF", "SOFT_BOILED", "MILK_DRINK",
               "MOONLIGHT", "MORNING_SUN", "SYNTHESIS", "SHORE_UP", "REST", "PROTECT", "SUBSTITUTE",
               "REFLECT", "LIGHT_SCREEN", "TAILWIND", "TRICK_ROOM", "RAIN_DANCE", "SUNNY_DAY",
               "HAIL", "SANDSTORM", "SNOWSCAPE", "IRON_DEFENSE", "AMNESIA", "COTTON_GUARD",
               "GROWTH", "WORK_UP", "HOWL", "MEDITATE", "SHARPEN", "TAIL_GLOW", "COSMIC_POWER"}


def pick_moves(species, level):
    learned = []
    for e in LEARNSETS.get("SPECIES_" + species, {}).get("LevelMoves", []):
        mv = e["Move"].removeprefix("MOVE_")
        if e["Level"] <= level and mv in MOVES and not MOVES[mv]["blocked"] and mv not in AVOID and mv not in learned:
            learned.append(mv)
    stab = TYPES.get(species, set())

    def score(mv):
        d = MOVES[mv]
        power = d["power"] if d["power"] > 1 else 60
        return power * (1.5 if d["type"] in stab else 1) * (d["accuracy"] or 100) / 100

    attacks = sorted((m for m in learned if MOVES[m]["split"] != "SPLIT_STATUS"), key=score, reverse=True)
    # only status moves that actually help a trainer's mon; latest-learned first
    status = [m for m in reversed(learned) if MOVES[m]["split"] == "SPLIT_STATUS" and m in GOOD_STATUS]
    chosen = []
    for t in sorted(stab):   # best attack of each of the species' own types
        chosen += [m for m in attacks if MOVES[m]["type"] == t][:1]
    if len(chosen) < 2:      # single type: a second, different same-type attack
        chosen += [m for m in attacks if MOVES[m]["type"] in stab and m not in chosen][:1]
    coverage = [m for m in attacks if m not in chosen and MOVES[m]["type"] not in {MOVES[c]["type"] for c in chosen}]
    chosen += coverage[:1]
    chosen += status[:1]
    other_status = [m for m in reversed(learned) if MOVES[m]["split"] == "SPLIT_STATUS" and m not in GOOD_STATUS]
    for m in attacks + status + other_status:   # fill what's left, weaker choices last
        if len(chosen) >= 4:
            break
        if m not in chosen:
            chosen.append(m)
    chosen = chosen[:4]
    return chosen + ["NONE"] * (4 - len(chosen))


def mon_block(indent, ivs, species, level, item, moves, has_items, has_moves):
    lines = [f"{indent}{{", f"{indent}    .ivs = {ivs},", f"{indent}    .abilitySlot = TRAINER_POKEMON_ABILITY_1,",
             f"{indent}    .level = {level},", f"{indent}    .species = SPECIES_{species},"]
    if has_items:
        lines.append(f"{indent}    .item = ITEM_{item},")
    if has_moves:
        lines.append(f"{indent}    .moves = {{ {', '.join('MOVE_' + m for m in moves)} }},")
    lines += [f"{indent}    .ballSeal = 0,", f"{indent}}},"]
    return "\n".join(lines)


ENTRY = re.compile(r"(\n    \[(\d+)\] = \{\n        \.name = \"[^\"]*\",\n        \.data = \{(.*?)\n        \},\n"
                   r"        \.party = \{\n)(.*?)(\n        \},\n)", re.S)


def rewrite(m):
    head, tid, data, party, tail = m.group(1), int(m.group(2)), m.group(3), m.group(4), m.group(5)
    has_items = "TRAINER_DATA_TYPE_ITEMS" in data
    has_moves = "TRAINER_DATA_TYPE_MOVES" in data
    if tid in TEAMS:
        ivs = re.search(r"\.ivs = (\d+)", party).group(1)
        team = TEAMS[tid]
        blocks = []
        for i, (sp, lv) in enumerate(team):
            item = "SITRUS_BERRY" if i == len(team) - 1 else "NONE"
            blocks.append(mon_block("            ", ivs, sp, lv, item, pick_moves(sp, lv), has_items, has_moves))
        return head + "\n".join(blocks) + tail
    cls = re.search(r"trainerClass = (\w+)", data).group(1)
    if cls in RIPTIDE_CLASSES:
        def swap(mm):
            lv, sp = int(mm.group(2)), mm.group(3)
            if sp not in RIPTIDE_SWAPS:
                return mm.group(0)
            new = fit(RIPTIDE_SWAPS[sp], lv)
            return mm.group(1) + f".species = SPECIES_{new},"
        new_party = re.sub(r"(\.level = (\d+),\n\s*)\.species = SPECIES_(\w+),", swap, party)
        if has_moves and new_party != party:
            # re-pick moves for every mon whose species changed
            out = []
            for mon_old, mon_new in zip(party.split("\n            },"), new_party.split("\n            },")):
                if mon_old != mon_new:
                    lv = int(re.search(r"\.level = (\d+)", mon_new).group(1))
                    sp = re.search(r"\.species = SPECIES_(\w+)", mon_new).group(1)
                    mv = ", ".join("MOVE_" + x for x in pick_moves(sp, lv))
                    mon_new = re.sub(r"\.moves = \{[^}]*\}", f".moves = {{ {mv} }}", mon_new)
                out.append(mon_new)
            new_party = "\n            },".join(out)
        return head + new_party + tail
    return m.group(0)


def main():
    src = TRAINERS.read_text(encoding="utf-8")
    known = set(re.findall(r"#define SPECIES_(\w+)\b", (ROOT / "include/constants/species.h").read_text()))
    for team in TEAMS.values():
        for sp, _ in team:
            assert sp in known, sp
    for sp in RIPTIDE_SWAPS.values():
        assert sp in known, sp
    out, n = ENTRY.subn(rewrite, src)
    TRAINERS.write_text(out, encoding="utf-8")
    found = {int(t) for t in re.findall(r"\n    \[(\d+)\] = \{\n        \.name", src)}
    print(f"scanned {n} trainers; rewrote {len(set(TEAMS) & found)} teams" +
          (f"; missing ids {sorted(set(TEAMS) - found)}" if set(TEAMS) - found else ""))
    for tid, team in TEAMS.items():
        sp, lv = team[-1]
        print(f"  {tid}: ace {sp.title()} L{lv} -> {', '.join(m.title() for m in pick_moves(sp, lv) if m != 'NONE')}")


if __name__ == "__main__":
    main()
