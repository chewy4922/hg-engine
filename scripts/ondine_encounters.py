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
    # Outer Isles (post-game, replace Kanto)
    "o_forest":  {"land": ["SEWADDLE", "PHANTUMP", "MORELULL", "DEERLING", "SKIDDO", "VENIPEDE", "PIKACHU"],
                  "night": ["NOIBAT", "PHANTUMP"], "water": "fresh", "rock": ["DWEBBLE", "NACLI"]},
    "o_rock":    {"land": ["ROGGENROLA", "NACLI", "ROLYCOLY", "ROCKRUFF", "ONIX", "LARVITAR", "TYRUNT"],
                  "water": "fresh", "rock": ["NACLI", "ROLYCOLY"]},
    "o_cave":    {"land": ["WOOBAT", "ROGGENROLA", "DRILBUR", "NOSEPASS", "BRONZOR", "SABLEYE", "GIBLE"],
                  "water": "fresh", "rock": ["ROGGENROLA", "NACLI"]},
    "o_coast":   {"land": ["WATTREL", "WIGLETT", "CRAMORANT", "SURSKIT", "LOTAD", "PYUKUMUKU", "MARILL"],
                  "night": ["WATTREL", "NOIBAT"], "water": "sea", "rock": ["BINACLE", "DWEBBLE"]},
    "o_psychic": {"land": ["FLITTLE", "HATENNA", "ESPURR", "INKAY", "NATU", "RALTS", "ABRA"],
                  "night": ["INKAY", "MISDREAVUS"], "water": "fresh", "rock": ["NACLI", "ROGGENROLA"]},
    "o_electric": {"land": ["PAWMI", "YAMPER", "SHINX", "BLITZLE", "TADBULB", "ELEKID", "TOGEDEMARU"],
                  "night": ["SHINX", "TADBULB"], "water": "sea", "rock": ["ROLYCOLY", "NOSEPASS"]},
    "o_grass":   {"land": ["PETILIL", "BOUNSWEET", "DEERLING", "SKIDDO", "SMOLIV", "BRAMBLIN", "MORELULL"],
                  "night": ["MORELULL", "PHANTUMP"], "water": "fresh", "rock": ["DWEBBLE", "NACLI"]},
    "o_swamp":   {"land": ["SHROODLE", "GLIMMET", "CROAGUNK", "SKORUPI", "VENIPEDE", "SALANDIT", "TOXEL"],
                  "night": ["SHROODLE", "CROAGUNK"], "water": "fresh", "rock": ["GLIMMET", "NACLI"]},
    "o_strong":  {"land": ["DEINO", "BELDUM", "GIBLE", "DREEPY", "LARVITAR", "JANGMO_O", "FRIGIBAX"],
                  "water": "dragon", "rock": ["NACLI", "ROLYCOLY"]},
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
    "R47_ROUTE_47": "cliffs", "R48_ROUTE_48": "cliffs", "D48R0101_CLIFF_EDGE_GATE": "sea_cave",
    "D50R0101_CLIFF_CAVE": "sea_cave",
    # ---- Outer Isles (Kanto) ----
    # Tidecrown (Viridian) forests
    "T01_PALLET_TOWN": "o_forest", "R01_ROUTE_1": "o_forest", "T02_VIRIDIAN_CITY": "o_forest",
    "R22_ROUTE_22": "o_forest", "R02_ROUTE_2_SOUTH_BELOW_VIRIDIAN_FOREST": "o_forest",
    "R02R0101_ROUTE_2_NORTH_ABOVE_VIRIDIAN_FOREST": "o_forest", "D46R0101_VIRIDIAN_FOREST": "o_forest",
    # Basalt Isle (Pewter) rock and caves
    "R03_ROUTE_3": "o_rock", "R09_ROUTE_9": "o_rock", "R10_ROUTE_10": "o_rock",
    "D02R0101_MT_MOON_1F": "o_cave", "D02R0102_MT_MOON_2F": "o_cave", "D02R0103_MT_MOON_OUTSIDE_AREA": "o_rock",
    "D02R0104_MT_MOON_OUTSIDE_CLEFAIRY_ACTIVE": "o_rock", "D05R0101_ROCK_TUNNEL_1F": "o_cave",
    "D05R0102_ROCK_TUNNEL_B1F": "o_cave", "D01R0101_DIGLETTS_CAVE": "o_cave",
    # Coralline (Cerulean) coast
    "R04_ROUTE_4": "o_coast", "R24_ROUTE_24": "o_coast", "R25_ROUTE_25": "o_coast", "T04_CERULEAN_CITY": "o_coast",
    "W19_ROUTE_19": "o_coast", "W20_ROUTE_20": "o_coast", "W21_ROUTE_21": "o_coast", "T09_CINNABAR_ISLAND": "o_coast",
    # Mirage Isle (Saffron) psychic routes
    "R05_ROUTE_5": "o_psychic", "R06_ROUTE_6": "o_psychic", "R07_ROUTE_7": "o_psychic", "R08_ROUTE_8": "o_psychic",
    # Stormcap (Vermilion)
    "R11_ROUTE_11": "o_electric", "T06_VERMILION_CITY": "o_electric",
    # Bloomhaven (Celadon)
    "T07_CELADON_CITY": "o_grass", "R16R0301_ROUTE_16": "o_grass",
    # Mire Isle (Fuchsia) swamps
    "R12_ROUTE_12": "o_swamp", "R13_ROUTE_13": "o_swamp", "R14_ROUTE_14": "o_swamp", "R15_ROUTE_15": "o_swamp",
    "R17_ROUTE_17": "o_swamp", "R18_ROUTE_18": "o_swamp", "T08_FUCHSIA_CITY": "o_swamp",
    # Seafoam stays icy
    **{f"D11R010{n}_SEAFOAM_ISLANDS_{f}": "ice_cave" for n, f in ((1, "1F"), (2, "B1F"), (3, "B2F"), (4, "B3F"), (5, "B4F"))},
    # strongest areas: Victory Road, Cerulean Cave, Mt. Apex (Mt. Silver) and the roads to them
    "R26_ROUTE_26": "o_strong", "R27_ROUTE_27": "o_strong", "R28_ROUTE_28": "o_strong",
    "D45R0101_TOHJO_FALLS": "sea_cave",
    "D43R0101_VICTORY_ROAD_1F": "o_strong", "D43R0102_VICTORY_ROAD_2F": "o_strong", "D43R0103_VICTORY_ROAD_3F": "o_strong",
    "D03R0101_CERULEAN_CAVE_1F": "o_strong", "D03R0102_CERULEAN_CAVE_B1F": "o_strong", "D03R0103_CERULEAN_CAVE_B2F": "o_strong",
    "T31_MT_SILVER_OUTSIDE_POKEMON_CENTER": "o_strong", "D41R0101_MT_SILVER_1F": "o_strong",
    "D41R0102_MT_SILVER_TOP_SNOWY_AREA": "o_strong", "D41R0103_MT_SILVER_MOUNTAINSIDE": "o_strong",
    "D41R0104_MT_SILVER_EXPERT_BELT_ROOM": "o_strong", "D41R0105_MT_SILVER_MOLTRES_ROOM": "o_strong",
    "D41R0106_MT_SILVER_3F": "o_strong", "D41R0107_MT_SILVER_4F": "o_strong",
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


# Post-game zones get a level floor: if an area's lowest level is below it, the whole area
# (each section separately) is shifted up to meet it. Idempotent - a second run changes nothing.
LEVEL_FLOOR = {z: 35 for z in ZONES if z.startswith("o_")}
LEVEL_FLOOR["o_strong"] = 45
LEVEL_CAP = 70


def raise_floor(levels, floor):
    low = min((lv for lv in levels if lv), default=0)
    shift = max(0, floor - low) if low else 0
    return [min(LEVEL_CAP, lv + shift) if lv else 0 for lv in levels]


def set_land(block, zone, floor=0):
    m = re.search(r"(\.levels = \{\s*)([\d,\s]+?)(\s*\})", block)
    levels = raise_floor([int(x) for x in m.group(2).split(",")], floor)
    block = block[:m.start(2)] + ", ".join(map(str, levels)) + block[m.end(2):]
    for field in ("speciesMorning", "speciesDay", "speciesNight"):
        pool = list(zone["land"])
        if field == "speciesNight" and "night" in zone:
            pool[0], pool[2] = zone["night"]
        m = species_list(block, field)
        indent = re.match(r"\s*", m.group(2)).group(0)
        body = "\n".join(f"{indent}SPECIES_{fit(pool[LAND_PATTERN[i]], levels[i])}," for i in range(12))
        block = block[:m.start(2)] + body + block[m.end(2):]
    return block


def set_slots(block, field, pool, floor=0):
    m = species_list(block, field)
    rows = [(int(lo), int(hi)) for lo, hi in re.findall(r"\{\s*(\d+),\s*(\d+),\s*SPECIES_\w+\s*\}", m.group(2))]
    los = raise_floor([lo for lo, _ in rows], floor)
    shift = [nl - lo for nl, (lo, _) in zip(los, rows)]
    rows = [(lo + d, min(LEVEL_CAP, hi + d) if hi else 0) for (lo, hi), d in zip(rows, shift)]
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
            floor = LEVEL_FLOOR.get(AREAS[name], 0)
            rate = lambda k: int(re.search(r"\.rate" + k + r" = (\d+)", block).group(1))
            if rate("Walk"):
                block = set_land(block, zone, floor)
            water = WATER[zone["water"]]
            for k, field, key in (("Surf", "surfSlots", "surf"), ("OldRod", "oldRodSlots", "old"),
                                  ("GoodRod", "goodRodSlots", "good"), ("SuperRod", "superRodSlots", "super")):
                if rate(k):
                    block = set_slots(block, field, water[key], floor)
            if rate("RockSmash"):
                block = set_slots(block, "rockSmashSlots", zone["rock"], floor)
            done += 1
        out.append(block)
        pos = end
    out.append(src[pos:])
    ENC.write_text("".join(out), encoding="utf-8")
    missing = set(AREAS) - {n for _, n in starts}
    print(f"rebuilt {done} areas" + (f"; unknown area names: {sorted(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
