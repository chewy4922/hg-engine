"""Edit Ondine's maps in DSPRE and keep them in sync with the hg-engine source.

    python3 scripts/dspre.py push    # copy the current test.nds out for DSPRE (keeps a snapshot)
    python3 scripts/dspre.py pull    # bring the edits from the saved DSPRE ROM back into the repo
    python3 scripts/dspre.py apply   # (called by `make`) put stored map edits into the build

How edits flow back on `pull` (the DSPRE ROM is compared with the snapshot taken at `push`):
- Files hg-engine never changes (map geometry: matrices, terrain, buildings, area data,
  textures...) are stored under data/dspre/files/ and copied into every build by `apply`.
- The map header table (arm9, 540 x 24 bytes) is stored as data/dspre/arm9_map_headers.bin.
- Scripts, zone events (warps, NPCs, signs) and message text are dumped back into
  data/scr_seq, data/eventdata/zone_event and data/text with hg-engine's own dump tool;
  only maps whose compiled data actually changed in DSPRE are kept.
- Anything else hg-engine generates from source (trainers, encounters, Pokémon data,
  sprites...) is reported, because a DSPRE edit there would be overwritten by the build.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import ndspy.narc
import ndspy.rom

ROOT = Path(__file__).resolve().parent.parent
DSPRE_ROM = Path("/mnt/c/Users/Erick/RomHacking/NewRegion/Ondine_DSPRE.nds")
SNAPSHOT = ROOT / "build/dspre_base.nds"
VANILLA = ROOT / "rom.nds"
STORE = ROOT / "data/dspre"
FILES = STORE / "files"
HEADERS = STORE / "arm9_map_headers.bin"

MAP_HEADERS_OFFSET, MAP_HEADER_SIZE, MAP_HEADER_COUNT = 0xF6BE0, 24, 540
DUMPED = {"a/0/1/2": "scripts", "a/0/3/2": "zone events", "a/0/2/7": "text"}


def files_of(rom):
    return {rom.filenames.filenameOf(i): bytes(d) for i, d in enumerate(rom.files)
            if rom.filenames.filenameOf(i)}


ARM9_RAM = 0x02000000


def arm9(rom):
    """{ram address: bytes} of every arm9 section, decompressed whether or not DSPRE compressed it"""
    return {s.ramAddress: bytes(s.data) for s in rom.loadArm9().sections}


def header_table(code):
    addr = ARM9_RAM + MAP_HEADERS_OFFSET
    for start, data in code.items():
        if start <= addr < start + len(data):
            return data[addr - start:addr - start + MAP_HEADER_SIZE * MAP_HEADER_COUNT]
    raise ValueError("map header table not found in arm9")


def push(args):
    built = ROOT / "test.nds"
    if DSPRE_ROM.exists() and SNAPSHOT.exists() and DSPRE_ROM.read_bytes() != SNAPSHOT.read_bytes() and not args.force:
        sys.exit(f"{DSPRE_ROM} has edits that were never pulled; run `pull` first (or push --force to discard them)")
    shutil.copyfile(built, SNAPSHOT)
    shutil.copyfile(built, DSPRE_ROM)
    print(f"DSPRE ROM ready: {DSPRE_ROM}")


def changed_members(path, old, new):
    """indices of NARC members that differ between two versions of an archive"""
    a, b = ndspy.narc.NARC(old).files, ndspy.narc.NARC(new).files
    return {i for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)}


def pull(args):
    base_rom, edit_rom = ndspy.rom.NintendoDSRom.fromFile(SNAPSHOT), ndspy.rom.NintendoDSRom.fromFile(DSPRE_ROM)
    vanilla = files_of(ndspy.rom.NintendoDSRom.fromFile(VANILLA))
    base, edit = files_of(base_rom), files_of(edit_rom)
    stored, dump_members, ignored = [], {}, []
    for path in sorted(set(base) | set(edit)):
        if base.get(path) == edit.get(path):
            continue
        if path in DUMPED:
            dump_members[path] = changed_members(path, base[path], edit[path])
        elif base.get(path) != vanilla.get(path):
            ignored.append(path)          # hg-engine builds this file from source
        else:
            out = FILES / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(edit[path])
            stored.append(path)
    old_code, new_code = arm9(base_rom), arm9(edit_rom)
    if header_table(old_code) != header_table(new_code):
        HEADERS.parent.mkdir(parents=True, exist_ok=True)
        HEADERS.write_bytes(header_table(new_code))
        stored.append("arm9 map headers")
    lo = ARM9_RAM + MAP_HEADERS_OFFSET
    hi = lo + MAP_HEADER_SIZE * MAP_HEADER_COUNT
    # arm9's module params (compressed-end pointer etc.) change whenever arm9 is recompressed
    main = old_code.get(ARM9_RAM, b"")
    magic = main.find(bytes.fromhex("2106c0de"))   # module params end with 0xDEC00621
    params = range(ARM9_RAM + magic - 0x1C, ARM9_RAM + magic + 8) if magic >= 0 else range(0)
    outside = [start + i for start, data in old_code.items() if start in new_code
               for i in range(min(len(data), len(new_code[start])))
               if data[i] != new_code[start][i] and not lo <= start + i < hi and start + i not in params]
    if outside or set(old_code) != set(new_code):
        ignored.append(f"arm9 code outside the map header table ({len(outside)} bytes changed)")
    if dump_members:
        dump(dump_members)
    print("stored map edits:", ", ".join(stored) or "none")
    for path, members in dump_members.items():
        print(f"pulled {DUMPED[path]}: members {sorted(members)}")
    for path in ignored:
        print(f"WARNING: DSPRE changed {path}, which hg-engine generates from source - "
              f"this edit will be lost; make it in the source files instead")
    shutil.copyfile(DSPRE_ROM, SNAPSHOT)


def dump(members):
    """run hg-engine's dump tool, then throw away every dumped file whose member didn't change"""
    subprocess.run([sys.executable, "tools/source/dumptools/dump_event_scripts.py", str(DSPRE_ROM)], cwd=ROOT, check=True)
    keep = set()
    for i in members.get("a/0/1/2", ()):
        keep |= {p for p in (ROOT / "data/scr_seq").glob(f"scr_seq_{i:04d}*.s")}
    for i in members.get("a/0/3/2", ()):
        keep |= {p for p in (ROOT / "data/eventdata/zone_event").glob(f"{i:03d}_*.json")}
    for i in members.get("a/0/2/7", ()):
        keep |= {p for p in (ROOT / "data/text").rglob(f"{i:03d}.txt")}
    status = subprocess.run(["git", "status", "--porcelain", "data/scr_seq", "data/eventdata/zone_event", "data/text"],
                            cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
    for line in status:
        path = ROOT / line[3:]
        if path in keep:
            continue
        if line.startswith("??"):
            path.unlink()
        else:
            subprocess.run(["git", "checkout", "--", str(path)], cwd=ROOT, check=True)


def vanilla_header_table():
    return header_table(arm9(ndspy.rom.NintendoDSRom.fromFile(VANILLA)))


def apply(args):
    filesys, arm9_path = Path(args.filesys), Path(args.arm9)
    n = 0
    if FILES.exists():
        for src in FILES.rglob("*"):
            if src.is_file():
                shutil.copyfile(src, filesys / src.relative_to(FILES))
                n += 1
    # base/arm9.bin is reused between builds, so always write a table: the stored DSPRE one,
    # or vanilla HeartGold's when there is none (otherwise an old edit would linger)
    code = bytearray(arm9_path.read_bytes())
    table = HEADERS.read_bytes() if HEADERS.exists() else vanilla_header_table()
    if code[MAP_HEADERS_OFFSET:MAP_HEADERS_OFFSET + len(table)] != table:
        code[MAP_HEADERS_OFFSET:MAP_HEADERS_OFFSET + len(table)] = table
        arm9_path.write_bytes(bytes(code))
    n += HEADERS.exists()
    if n:
        print(f"dspre: applied {n} stored map edit(s)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("push").add_argument("--force", action="store_true")
    sub.add_parser("pull")
    ap = sub.add_parser("apply")
    ap.add_argument("--filesys", required=True)
    ap.add_argument("--arm9", required=True)
    args = p.parse_args()
    {"push": push, "pull": pull, "apply": apply}[args.cmd](args)


if __name__ == "__main__":
    main()
