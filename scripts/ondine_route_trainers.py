"""Give ordinary trainers island Pokémon: families that don't live in the Ondine Archipelago
are swapped for a newer family of the same type and role, moved along its evolution line
to suit each Pokémon's level. Families that do live on the islands, starters and story
Pokémon (Slowpoke) are left alone. Special trainers (leaders, E4, rival, Riptide...) are
skipped; they are handled by ondine_trainers.py. Custom movesets are re-picked for every
swapped Pokémon. Re-runnable: only old species are matched.

    python3 scripts/ondine_route_trainers.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from ondine_encounters import PRE, fit  # noqa: E402
import ondine_trainers as T  # noqa: E402

FAMILY_SWAPS = {   # first stage -> first stage
    "GEODUDE": "ROGGENROLA", "GOLDEEN": "ARROKUDA", "KOFFING": "MAREANIE", "CATERPIE": "GRUBBIN",
    "VOLTORB": "PAWMI", "PSYDUCK": "DUCKLETT", "HORSEA": "SKRELP", "PIDGEY": "ROOKIDEE",
    "SENTRET": "SKWOVET", "MAGBY": "CHARCADET", "SPEAROW": "PIKIPEK", "WEEDLE": "NYMBLE",
    "BELLSPROUT": "FOMANTIS", "RATTATA": "LECHONK", "MAREEP": "YAMPER", "POLIWAG": "TYMPOLE",
    "SEEL": "SPHEAL", "QWILFISH": "WISHIWASHI", "SANDSHREW": "DRILBUR", "PARAS": "DWEBBLE",
    "DIGLETT": "WIGLETT", "ZUBAT": "NOIBAT", "TEDDIURSA": "LILLIPUP", "SHELLDER": "BINACLE",
    "MANKEY": "MIENFOO", "DODUO": "FLETCHLING", "PONYTA": "LITLEO", "ODDISH": "BOUNSWEET",
    "REMORAID": "CLAUNCHER", "SNUBBULL": "TANDEMAUS",
}

SPECIAL = re.compile(r"LEADER|ELITE|CHAMPION|RIVAL|LANCE|_RED|ROCKET|EXECUTIVE|BOSS|PASSERBY|PKMN_TRAINER")


def family_of(species):
    while species in PRE:
        species = PRE[species][0]
    return species


def swap_party(party, has_moves):
    mons = party.split("\n            },")
    out, changed = [], 0
    for mon in mons:
        m = re.search(r"\.level = (\d+),\n(\s*)\.species = SPECIES_(\w+),", mon)
        if m and family_of(m.group(3)) in FAMILY_SWAPS:
            lv = int(m.group(1))
            new = fit(FAMILY_SWAPS[family_of(m.group(3))], lv)
            mon = mon[:m.start()] + f".level = {lv},\n{m.group(2)}.species = SPECIES_{new}," + mon[m.end():]
            if has_moves:
                mv = ", ".join("MOVE_" + x for x in T.pick_moves(new, lv))
                mon = re.sub(r"\.moves = \{[^}]*\}", f".moves = {{ {mv} }}", mon)
            changed += 1
        out.append(mon)
    return "\n            },".join(out), changed


def main():
    known = set(re.findall(r"#define SPECIES_(\w+)\b", (ROOT / "include/constants/species.h").read_text()))
    for a, b in FAMILY_SWAPS.items():
        assert a in known and b in known, (a, b)
    src = T.TRAINERS.read_text(encoding="utf-8")
    stats = {"trainers": 0, "mons": 0}

    def rewrite(m):
        head, tid, data, party, tail = m.group(1), int(m.group(2)), m.group(3), m.group(4), m.group(5)
        cls = re.search(r"trainerClass = (\w+)", data).group(1)
        if tid in T.TEAMS or cls in T.RIPTIDE_CLASSES or SPECIAL.search(cls):
            return m.group(0)
        new_party, n = swap_party(party, "TRAINER_DATA_TYPE_MOVES" in data)
        if n:
            stats["trainers"] += 1
            stats["mons"] += n
        return head + new_party + tail

    T.TRAINERS.write_text(T.ENTRY.sub(rewrite, src), encoding="utf-8")
    print(f"swapped {stats['mons']} Pokémon on {stats['trainers']} trainers")


if __name__ == "__main__":
    main()
