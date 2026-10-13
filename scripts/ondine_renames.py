"""Rename HeartGold places and characters to the Ondine Archipelago ones.

Runs over the dumped text archives (data/text/**/*.txt) and the string literals in
data/Trainers.c. Safe to re-run: no new name contains an old one.

    python3 scripts/ondine_renames.py          # apply
    python3 scripts/ondine_renames.py --check  # dry run: only report lines that get too wide
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Order matters: longer phrases first so "Violet City" wins over "Violet".
PLACES = [
    ("New Bark Town", "Saltbloom Town"), ("New Bark", "Saltbloom"),
    ("Cherrygrove City", "Pebblecove"), ("Cherrygrove", "Pebblecove"),
    ("Violet City", "Windrift Town"), ("Violet", "Windrift"),
    ("Azalea Town", "Bloomreef"), ("Azalea", "Bloomreef"),
    ("Goldenrod Tunnel", "Coral Tunnel"),   # map-name popup is narrow
    ("Goldenrod City", "Coralcross City"), ("Goldenrod", "Coralcross"),
    ("Ecruteak City", "Lantern Key"), ("Ecruteak", "Lantern"),
    ("Cianwood City", "Palemoon Isle"), ("Cianwood", "Palemoon"),
    ("Olivine City", "Rivetport"), ("Olivine", "Rivetport"),
    ("Mahogany Town", "Frostveil"), ("Mahogany", "Frostveil"),
    ("Blackthorn City", "Drakespire"), ("Blackthorn", "Drakespire"),
    ("Indigo Plateau", "Crown Isle"),
    ("Whirl Islands", "Abyssal Isles"),
    ("Pewter City", "Basalt Isle"), ("Pewter", "Basalt"),
    ("Cerulean City", "Coralline"), ("Cerulean", "Coralline"),
    ("Vermilion City", "Stormcap"), ("Vermilion", "Stormcap"),
    ("Celadon City", "Bloomhaven"), ("Celadon", "Bloomhaven"),
    ("Fuchsia City", "Mire Isle"), ("Fuchsia", "Mire"),
    ("Saffron City", "Mirage Isle"), ("Saffron", "Mirage"),
    ("Cinnabar Island", "Cinder Isle"), ("Cinnabar", "Cinder"),
    ("Viridian City", "Tidecrown"), ("Viridian", "Tidecrown"),
    ("Mt. Silver", "Mt. Apex"),
    ("Johto", "Ondine"),     # the Inner Isles' region name
    ("Kanto", "Ostra"),      # the Outer Isles (post-game)
]

PEOPLE = [
    ("Professor Elm", "Professor Maren"), ("Prof. Elm", "Prof. Maren"), ("Elm", "Maren"),
    ("Team Rocket", "Team Riptide"), ("Rocket", "Riptide"),
    ("Giovanni", "Wake"),
    ("Ariana", "Siren"), ("Archer", "Hook"), ("Proton", "Brine"), ("Petrel", "Squall"),
    ("Falkner", "Kestrel"), ("Bugsy", "Lumi"), ("Whitney", "Sunny"), ("Morty", "Wren"),
    ("Chuck", "Tomo"), ("Jasmine", "Anvila"), ("Pryce", "Yuki"), ("Clair", "Ryla"),
    ("Koga", "Thorn"), ("Bruno", "Brick"), ("Karen", "Nyx"), ("Lance", "Soren"),
    ("Brock", "Flint"), ("Misty", "Nerissa"), ("Lt. Surge", "Volt"), ("Surge", "Volt"),
    ("Erika", "Ivy"), ("Janine", "Nox"), ("Sabrina", "Sable"), ("Blaine", "Ember"),
    ("Kurt", "Nemo"),
]

PAIRS = PLACES + PEOPLE
# Whole words only, and also the ALL-CAPS spelling used in a few signs/menus.
PATTERNS = []
for old, new in PAIRS:
    PATTERNS.append((re.compile(r"(?<![A-Za-z])" + re.escape(old) + r"(?![a-z])"), new))
    if old.upper() != old:
        PATTERNS.append((re.compile(r"(?<![A-Za-z])" + re.escape(old.upper()) + r"(?![A-Z])"), new.upper()))

# Newer-gen move/ability/item names that contain an old name and must stay as they are.
PROTECTED = ["Misty Terrain", "Misty Surge", "Misty Seed", "Misty Explosion",
             "Electric Surge", "Psychic Surge", "Grassy Surge", "Surge Surfer",
             "MISTY TERRAIN", "MISTY SURGE", "MISTY SEED", "MISTY EXPLOSION",
             "ELECTRIC SURGE", "PSYCHIC SURGE", "GRASSY SURGE", "SURGE SURFER"]

# Lines that end up too wide for their text box after renaming, reworded by hand.
POST_FIXES = {
    "data/text/custom/412.txt": [("Commercial: The symbol of Coralcross City,", "Commercial: Coralcross City’s symbol,")],
    "data/text/custom/542.txt": [("So this is the famous Maren Pokémon Lab...", "So this is the famous Maren Lab..."),
                                 ("Professor Maren has been waiting for you.", "Prof. Maren has been waiting for you.")],
    "data/text/custom/543.txt": [("Professor Maren: Oh, hey! I got an email!", "Professor Maren: Oh! I got an email!")],
    "data/text/custom/556.txt": [("Professor Maren, then from Professor Maren", "Prof. Maren, then from Prof. Maren")],
    "data/text/custom/683.txt": [("the Tidecrown Forest in the Ostra region!", "Tidecrown Forest in the Ostra region!")],
}


def rename(s):
    held = {}
    for i, phrase in enumerate(PROTECTED):
        key = f"\x00{i}\x00"
        if phrase in s:
            held[key] = phrase
            s = s.replace(phrase, key)
    for pat, new in PATTERNS:
        s = pat.sub(new, s)
    for key, phrase in held.items():
        s = s.replace(key, phrase)
    return s


def rename_c_strings(src):
    # only touch "..." literals so constants like TRAINERCLASS_LEADER_FALKNER stay intact
    return re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: rename(m.group(0)), src)


def load_widths():
    """Pixel width of every character in the main message font (a/0/1/6 file 0)."""
    d = (ROOT / "base_dsrom/files/a/0/1/6").read_bytes()
    off = struct.unpack_from("<H", d, 0x0C)[0]
    size, _ = struct.unpack_from("<IH", d, off + 4)
    start, end = struct.unpack_from("<II", d, off + 12)
    gmif = off + size + struct.unpack_from("<I", d, off + size + 4)[0]
    font = d[gmif + 8 + start:gmif + 8 + end]
    table, count = struct.unpack_from("<II", font, 4)
    widths = {}
    for line in (ROOT / "charmap.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([0-9A-F]{4})=(.)$", line)
        if m:
            code = int(m.group(1), 16)
            if 1 <= code <= count:
                widths.setdefault(m.group(2), font[table + code - 1])
    return widths


WIDTHS = None


def line_widths(text):
    """Pixel width of each printed line (lines split at \\n, \\r, \\f and between messages)."""
    global WIDTHS
    if WIDTHS is None:
        WIDTHS = load_widths()
    out = []
    for line in re.split(r"\\[nrf]|\n", text):
        plain = re.sub(r"\{[^}]*\}", "", line)
        out.append((sum(WIDTHS.get(c, 6) for c in plain), plain))
    return out


DIALOGUE_WIDTH = 223  # vanilla field dialogue lines reach this many pixels, so it fits the box


def width(line):
    line_widths("")  # make sure WIDTHS is loaded
    return sum(WIDTHS.get(c, 6) for c in re.sub(r"\{[^}]*\}", "", line))


def reflow(msg, limit):
    """Move words between the two lines of a text box until no line is wider than limit."""
    parts = re.split(r"(\\[nrf])", msg)   # text, sep, text, sep, ...
    for i in range(0, len(parts), 2):
        after = parts[i + 1] if i + 1 < len(parts) else None
        before = parts[i - 1] if i > 0 else None
        while width(parts[i]) > limit:
            words = parts[i].split(" ")
            if after == "\\n" and "{" not in words[-1] and len(words) > 1 \
                    and width(words[-1] + " " + parts[i + 2]) <= limit:
                parts[i] = " ".join(words[:-1])
                parts[i + 2] = words[-1] + " " + parts[i + 2]
            elif before == "\\n" and "{" not in words[0] and len(words) > 1 \
                    and width(parts[i - 2] + " " + words[0]) <= limit:
                parts[i - 2] = parts[i - 2] + " " + words[0]
                parts[i] = " ".join(words[1:])
            else:
                break
    return "".join(parts)


def main():
    check = "--check" in sys.argv
    files = sorted((ROOT / "data/text").rglob("*.txt"))
    changed = 0
    too_wide = []
    for f in files + [ROOT / "data/Trainers.c"]:
        old = f.read_text(encoding="utf-8")
        new = rename_c_strings(old) if f.suffix == ".c" else rename(old)
        if new == old:
            continue
        changed += 1
        if f.suffix == ".txt":
            # a line may not get wider than its window: dialogue files can use the full
            # dialogue width, narrow windows (signs, map names, menus) their own widest line
            limit = max(w for w, _ in line_widths(old))
            if limit >= 200:
                limit = max(limit, DIALOGUE_WIDTH)
            for a, b in POST_FIXES.get(str(f.relative_to(ROOT)), []):
                new = new.replace(a, b)
            new = "\n".join(m if m == o else reflow(m, limit)
                            for m, o in zip(new.split("\n"), old.split("\n")))
            seen = {p for _, p in line_widths(old)}
            too_wide += [(f.relative_to(ROOT), w, limit, p) for w, p in line_widths(new) if w > limit and p not in seen]
        if not check:
            f.write_text(new, encoding="utf-8")
    print(f"{'would change' if check else 'changed'} {changed} files")
    print(f"{len(too_wide)} lines wider than anything their file had before:")
    for f, w, limit, p in too_wide:
        print(f"  {f} ({w}>{limit}px): {p}")


if __name__ == "__main__":
    main()
