"""Recolour HeartGold overworld (walking) sprites to match the Black 2 battle art.

Only palette entries change (data/graphics/overworlds/NNNN-name.pal, JASC-PAL), so the
sprite shapes stay HeartGold's. Re-runnable: entries are set to fixed colours.

    python3 scripts/ondine_overworld_recolors.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OW = ROOT / "data/graphics/overworlds"

TEAL, DEEP_TEAL, ICE = (40, 160, 176), (24, 96, 112), (120, 200, 232)
RECOLORS = {
    # rival: Silver -> Hugh (navy hair, red jacket)
    "0058-gsrivel.pal": {1: (16, 24, 56), 3: (32, 48, 104), 2: (56, 80, 152), 4: (96, 120, 192),
                         13: (184, 40, 48), 14: (120, 24, 32), 8: (216, 80, 72)},
    # Team Riptide grunts: Rocket magenta/orange trim -> Plasma-style teal
    "0174-rocketm.pal": {9: TEAL, 12: ICE},
    "0173-rocketw.pal": {6: TEAL, 9: DEEP_TEAL, 5: DEEP_TEAL, 13: ICE},
}


def main():
    for name, changes in RECOLORS.items():
        path = OW / name
        lines = path.read_text().splitlines()
        assert lines[0] == "JASC-PAL" and lines[2] == "16", name
        for index, (r, g, b) in changes.items():
            lines[3 + index] = f"{r} {g} {b}"
        path.write_bytes(("\r\n".join(lines) + "\r\n").encode())
        print(f"{name}: {len(changes)} colours")


if __name__ == "__main__":
    main()
