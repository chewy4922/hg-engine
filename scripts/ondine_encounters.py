"""Fill the Inner Isles' (Johto's) wild encounters with mixed-generation Ondine Pokémon.

Every listed area is rebuilt from its zone's pools; levels and encounter rates stay
HeartGold's. Each slot's species is moved up or down its evolution line to suit the
slot's level, so a pool can name a whole family by its first stage.
Re-runnable: the output depends only on the tables below.

    python3 scripts/ondine_encounters.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENC = ROOT / "data/Encounters.c"

# Land pools: 7 species, common -> rare. Grass slots 0..11 (20,20,10,10,10,10,5,5,4,4,1,1 %)
# take pool entries LAND_PATTERN[slot]. "night" replaces entries 0 and 2 at night.
LAND_PATTERN = [0, 1, 2, 3, 0, 1, 4, 5, 4, 5, 6, 6]
ZONES = {
    "beach":     {"land": ["WINGULL", "PIKIPEK", "WOOLOO", "SKWOVET", "CRABRAWLER", "LECHONK", "CORPHISH"],
                  "night": ["POOCHYENA", "NICKIT"], "water": "sea", "rock": ["DWEBBLE", "BINACLE"]},
    "cliffs":    {"land": ["ROOKIDEE", "HOPPIP", "FLETCHLING", "BUNNELBY", "SWABLU", "FLITTLE", "NOIBAT"],
                  "night": ["HOOTHOOT", "NOIBAT"], "water": "fresh", "rock": ["NOSEPASS", "ROGGENROLA"]},
    "sea_cave":  {"land": ["ZUBAT", "ROGGENROLA", "WOOBAT", "BINACLE", "NOSEPASS", "DWEBBLE", "CARBINK"],
                  "water": "sea", "rock": ["DWEBBLE", "ROGGENROLA"]},
    "jungle":    {"land": ["GRUBBIN", "CUTIEFLY", "NYMBLE", "SEWADDLE", "AIPOM", "FOMANTIS", "PASSIMIAN"],
                  "night": ["TAROUNTULA", "SPINARAK"], "water": "fresh", "rock": ["DWEBBLE", "SHUCKLE"]},
    "coast":     {"land": ["YAMPER", "TANDEMAUS", "LILLIPUP", "TRUBBISH", "PAWMI", "ROCKRUFF", "EEVEE"],
                  "night": ["MEOWTH", "NICKIT"], "water": "sea", "rock": ["ROLYCOLY", "NOSEPASS"]},
    "dusk":      {"land": ["SHUPPET", "NOIBAT", "LITWICK", "GREAVARD", "MURKROW", "ZORUA", "MIMIKYU"],
                  "night": ["GASTLY", "MISDREAVUS"], "water": "fresh", "rock": ["ROGGENROLA", "SANDYGAST"]},
    "ghost":     {"land": ["GASTLY", "LITWICK", "SANDYGAST", "SHUPPET", "PHANTUMP", "SINISTEA", "DREEPY"],
                  "water": "fresh", "rock": ["SANDYGAST", "ROGGENROLA"]},
    "dojo":      {"land": ["MACHOP", "MIENFOO", "KLINK", "TINKATINK", "PAWNIARD", "MAGNEMITE", "RIOLU"],
                  "night": ["SCRAGGY", "PAWNIARD"], "water": "sea", "rock": ["ROGGENROLA", "NACLI"]},
    "mortar":    {"land": ["ROGGENROLA", "MAKUHITA", "TIMBURR", "BRONZOR", "DRILBUR", "HAWLUCHA", "CARBINK"],
                  "water": "fresh", "rock": ["NACLI", "ROLYCOLY"]},
    "frost":     {"land": ["SNORUNT", "CETODDLE", "SNOM", "CUBCHOO", "BERGMITE", "SNOVER", "SNEASEL"],
                  "night": ["SNEASEL", "SNOM"], "water": "fresh", "rock": ["BERGMITE", "NACLI"]},
    "ice_cave":  {"land": ["SWINUB", "SNORUNT", "BERGMITE", "SNOM", "SPHEAL", "SNEASEL", "FRIGIBAX"],
                  "water": "fresh", "rock": ["BERGMITE", "NACLI"]},
    "volcano":   {"land": ["NUMEL", "SALANDIT", "CHARCADET", "SLUGMA", "AXEW", "GOOMY", "LARVESTA"],
                  "night": ["HOUNDOUR", "SALANDIT"], "water": "dragon", "rock": ["ROLYCOLY", "SLUGMA"]},
    "dragon_cave": {"land": ["ROLYCOLY", "SALANDIT", "AXEW", "DEINO", "JANGMO_O", "ROGGENROLA", "FRIGIBAX"],
                  "water": "dragon", "rock": ["ROLYCOLY", "NACLI"]},
    "abyss":     {"land": ["WOOBAT", "BINACLE", "SPHEAL", "CORSOLA", "KRABBY", "DWEBBLE", "DHELMISE"],
                  "water": "sea", "rock": ["BINACLE", "DWEBBLE"]},
}

# Water pools, 5 slots each (surf 60/30/5/4/1, rods 40/40/15/4/1).
WATER = {
    "sea":    {"surf": ["TENTACOOL", "WINGULL", "FINIZEN", "MAREANIE", "LAPRAS"],
               "old": ["MAGIKARP", "FINNEON", "MAGIKARP", "FINNEON", "WISHIWASHI"],
               "good": ["WISHIWASHI", "CLAUNCHER", "SKRELP", "FINNEON", "BRUXISH"],
               "super": ["WAILMER", "CLAUNCHER", "BRUXISH", "SKRELP", "DHELMISE"]},
    "fresh":  {"surf": ["MARILL", "WOOPER", "DUCKLETT", "ARROKUDA", "BASCULIN"],
               "old": ["MAGIKARP", "ARROKUDA", "MAGIKARP", "ARROKUDA", "FEEBAS"],
               "good": ["CHEWTLE", "ARROKUDA", "TYMPOLE", "WOOPER", "FEEBAS"],
               "super": ["CHEWTLE", "TYMPOLE", "BASCULIN", "DREDNAW", "FEEBAS"]},
    "dragon": {"surf": ["TENTACOOL", "SKRELP", "FINIZEN", "GOOMY", "DRATINI"],
               "old": ["MAGIKARP", "SKRELP", "MAGIKARP", "SKRELP", "DRATINI"],
               "good": ["SKRELP", "DRATINI", "CLAUNCHER", "SKRELP", "DRATINI"],
               "super": ["SKRELP", "DRATINI", "DRATINI", "TATSUGIRI", "DRATINI"]},
}

AREAS = {
    # Saltbloom / beach routes
    "T20_NEW_BARK_TOWN": "beach", "R29_ROUTE_29": "beach", "T21_CHERRYGROVE_CITY": "beach",
    "R46_ROUTE_46": "beach",
    # Windrift cliffs
    "R30_ROUTE_30": "cliffs", "R31_ROUTE_31": "cliffs", "T22_VIOLET_CITY": "cliffs",
    "D15R0102_SPROUT_TOWER_2F": "cliffs", "D15R0103_SPROUT_TOWER_3F": "cliffs", "R32_ROUTE_32": "cliffs",
    # sea caves
    "D25R0101_UNION_CAVE_1F": "sea_cave", "D25R0102_UNION_CAVE_B1F": "sea_cave",
    "D25R0103_UNION_CAVE_B2F": "sea_cave", "D42R0102_DARK_CAVE_ROUTE_31_ENTRANCE": "sea_cave",
    "D26R0102_SLOWPOKE_WELL_1F": "sea_cave", "D26R0103_SLOWPOKE_WELL_B2F": "sea_cave",
    # Bloomreef jungle
    "R33_ROUTE_33": "jungle", "D36R0101_ILEX_FOREST": "jungle", "D22R0101_NATIONAL_PARK": "jungle",
    "D22R0102_NATIONAL_PARK_BUG_CATCHING_CONTEST": "jungle",
    # Coralcross coast
    "R34_ROUTE_34": "coast", "R35_ROUTE_35": "coast",
    # Lantern Key
    "R36_ROUTE_36": "dusk", "R37_ROUTE_37": "dusk", "T27_ECRUTEAK_CITY": "dusk",
    "D18R0101_BURNED_TOWER_1F": "ghost", "D18R0102_BURNED_TOWER_B1F": "ghost",
    **{f"D17R01{n:02d}_BELL_TOWER_{n}F": "ghost" for n in range(2, 10)},
    "D17R0112_BELL_TOWER_10F": "ghost",
    # Palemoon dojo / Rivetport shipyard
    "R38_ROUTE_38": "dojo", "R39_ROUTE_39": "dojo", "T26_OLIVINE_CITY": "dojo",
    "W40_ROUTE_40": "dojo", "W41_ROUTE_41": "dojo", "T24_CIANWOOD_CITY": "dojo", "R42_ROUTE_42": "dojo",
    "D38R0101_MT_MORTAR_WATERFALL_ROOM": "mortar", "D38R0102_MT_MORTAR_CENTRAL_ROOM": "mortar",
    "D38R0103_MT_MORTAR_ROOM_ABOVE_WATERFALL": "mortar", "D38R0104_MT_MORTAR_B1F": "mortar",
    # Abyssal Isles (Whirl Islands)
    "D40R0101_WHIRL_ISLANDS_1F": "abyss", "D40R0102_WHIRL_ISLANDS_B1F": "abyss",
    "D40R0104_WHIRL_ISLANDS_B2F": "abyss", "D40R0106_WHIRL_ISLANDS_B3F_LEDGE_OVERLOOKING_LUGIA_ROOM": "abyss",
    # Frostveil
    "R43_ROUTE_43": "frost", "T29_LAKE_OF_RAGE": "frost", "R44_ROUTE_44": "frost",
    "D39R0101_ICE_PATH_1F": "ice_cave", "D39R0102_ICE_PATH_B1F": "ice_cave",
    "D39R0103_ICE_PATH_B2F": "ice_cave", "D39R0104_ICE_PATH_B3F": "ice_cave",
    # Drakespire volcano
    "R45_ROUTE_45": "volcano", "T30_BLACKTHORN_CITY": "volcano", "D44R0102_DRAGONS_DEN": "dragon_cave",
    "D42R0101_DARK_CAVE_ROUTE_45_ENTRANCE": "dragon_cave",
}

LEVEL_EVOS = re.compile(r"EVO_LEVEL\w*")


def load_evolutions():
    """species -> [(level, target)] for level-up evolutions, and target -> (pre, level)."""
    src = (ROOT / "data/Evolutions.c").read_text(encoding="utf-8")
    nxt, pre = {}, {}
    for m in re.finditer(r"\[SPECIES_(\w+)\]\s*=\s*\{\s*\.entries\s*=\s*\{(.*?)\}\s*,?\s*\}", src, re.S):
        sp = m.group(1)
        for method, param, target in re.findall(r"\{\s*(EVO_\w+)\s*,\s*(\d+)\s*,\s*SPECIES_(\w+)\s*\}", m.group(2)):
            if LEVEL_EVOS.fullmatch(method) and target != "NONE" and int(param) > 0:
                nxt.setdefault(sp, []).append((int(param), target))
                pre.setdefault(target, (sp, int(param)))
    return nxt, pre


NEXT, PRE = load_evolutions()


def fit(species, level):
    """Walk species down/up its level-up evolution line to suit level."""
    while species in PRE and level < PRE[species][1]:
        species = PRE[species][0]
    while species in NEXT and len(NEXT[species]) == 1 and level >= NEXT[species][0][0]:
        species = NEXT[species][0][1]
    return species


def species_list(block, field):
    m = re.search(r"(\." + field + r" = \{\n)(.*?)(\n\s*\},)", block, re.S)
    return m


def set_land(block, zone):
    levels = [int(x) for x in re.search(r"\.levels = \{\s*([\d,\s]+?)\s*\}", block).group(1).split(",")]
    for field in ("speciesMorning", "speciesDay", "speciesNight"):
        pool = list(zone["land"])
        if field == "speciesNight" and "night" in zone:
            pool[0], pool[2] = zone["night"]
        m = species_list(block, field)
        indent = re.match(r"\s*", m.group(2)).group(0)
        body = "\n".join(f"{indent}SPECIES_{fit(pool[LAND_PATTERN[i]], levels[i])}," for i in range(12))
        block = block[:m.start(2)] + body + block[m.end(2):]
    return block


def set_slots(block, field, pool):
    m = species_list(block, field)
    rows = re.findall(r"\{\s*(\d+),\s*(\d+),\s*SPECIES_\w+\s*\}", m.group(2))
    indent = re.match(r"\s*", m.group(2)).group(0)
    out = []
    for (lo, hi), sp in zip(rows, pool):
        out.append(f"{indent}{{ {lo}, {hi}, SPECIES_{fit(sp, int(hi)) if int(hi) else 'NONE'} }},")
    return block[:m.start(2)] + "\n".join(out) + block[m.end(2):]


def main():
    src = ENC.read_text(encoding="utf-8")
    known = set(re.findall(r"#define SPECIES_(\w+)\b", (ROOT / "include/constants/species.h").read_text()))
    for z in ZONES.values():
        for sp in z["land"] + z.get("night", []) + z["rock"]:
            assert sp in known, sp
    for w in WATER.values():
        for pool in w.values():
            for sp in pool:
                assert sp in known, sp
    starts = [(m.start(), m.group(1)) for m in re.finditer(r"^    \[ENCDATA_(\w+)\] = \{", src, re.M)]
    starts.append((len(src) - src[::-1].index("}") - 1, None))
    out, pos, done = [], 0, 0
    for (start, name), (end, _) in zip(starts, starts[1:]):
        out.append(src[pos:start])
        block = src[start:end]
        if name in AREAS:
            zone = ZONES[AREAS[name]]
            rate = lambda k: int(re.search(r"\.rate" + k + r" = (\d+)", block).group(1))
            if rate("Walk"):
                block = set_land(block, zone)
            water = WATER[zone["water"]]
            for k, field, key in (("Surf", "surfSlots", "surf"), ("OldRod", "oldRodSlots", "old"),
                                  ("GoodRod", "goodRodSlots", "good"), ("SuperRod", "superRodSlots", "super")):
                if rate(k):
                    block = set_slots(block, field, water[key])
            if rate("RockSmash"):
                block = set_slots(block, "rockSmashSlots", zone["rock"])
            done += 1
        out.append(block)
        pos = end
    out.append(src[pos:])
    ENC.write_text("".join(out), encoding="utf-8")
    missing = set(AREAS) - {n for _, n in starts}
    print(f"rebuilt {done} areas" + (f"; unknown area names: {sorted(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
