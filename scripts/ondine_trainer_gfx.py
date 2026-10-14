"""Import Black 2 / White 2 trainer art into hg-engine's trainer_gfx.

Black 2 keeps each trainer class in a/0/7/1 as 8 files; file 8*n+1 is a 256x128 linear
4bpp parts sheet whose top-right corner holds the fully assembled trainer, and
file 8*n+7 is its 16-colour palette. This crops that figure, fits it (bottom-centred,
shrunk only if needed) into HeartGold's 80x80 frame and writes, per HG class:
  NNN.png      80x80 indexed frame (battle animation sheet, one still cell)
  NNN_enc.png  160x80 static sheet (the same frame twice)
  NNN_cell.json / NNN_anim.json  copied from a one-cell class so old multi-frame layouts go away
The existing NNN_enc.png.key (encryption seed) is kept.

Needs Pillow; reads a folder of a/0/7/1 files extracted as 0000.bin, 0001.bin, ...

    python ondine_trainer_gfx.py <a071 dir> <hg-engine data/graphics/trainer_gfx dir>
"""
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image

# HeartGold trainer class -> Black 2 a/0/7/1 entry
SWAPS = {
    70: 19,    # Sunny (Whitney)            <- Lenora
    75: 78,    # Tomo (Chuck)               <- Marshal
    76: 155,   # Ryla (Clair)               <- Iris (Champion outfit)
    87: 101,   # Coral (E4 Will)            <- Marlon
    112: 99,   # Brick (E4 Bruno)           <- Clay
    88: 80,    # Nyx (E4 Karen)             <- Caitlin
    86: 100,   # Champion Soren             <- Drayden
    123: 100,  # Soren (story battle class) <- Drayden
    124: 151,  # Boss Wake (Giovanni)       <- Ghetsis
    55: 149,   # Riptide Grunt M            <- Plasma Grunt M
    62: 150,   # Riptide Grunt F            <- Plasma Grunt F
    116: 12,   # Admin Hook (Archer)        <- Colress
    23: 127,   # Rival                      <- Hugh
}
ONE_CELL_TEMPLATE = 64   # a class whose cell/anim json is a single 80x80 still


def lz11(d):
    if d[0] != 0x11:
        return d
    size = d[1] | d[2] << 8 | d[3] << 16
    i = 4
    if size == 0:
        size, i = int.from_bytes(d[4:8], "little"), 8
    out = bytearray()
    while len(out) < size:
        flags = d[i]
        i += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                x, ind = d[i], d[i] >> 4
                if ind == 0:
                    n, disp, i = ((x & 15) << 4 | d[i + 1] >> 4) + 0x11, ((d[i + 1] & 15) << 8 | d[i + 2]) + 1, i + 3
                elif ind == 1:
                    n = ((x & 15) << 12 | d[i + 1] << 4 | d[i + 2] >> 4) + 0x111
                    disp, i = ((d[i + 2] & 15) << 8 | d[i + 3]) + 1, i + 4
                else:
                    n, disp, i = ind + 1, ((x & 15) << 8 | d[i + 1]) + 1, i + 2
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(d[i])
                i += 1
    return bytes(out)


def block(d, magic):
    i = 0x10
    while i < len(d):
        if d[i:i + 4] == magic:
            return i
        i += struct.unpack_from("<I", d, i + 4)[0]
    raise KeyError(magic)


def palette(nclr):
    o = block(nclr, b"TTLP")
    size = struct.unpack_from("<I", nclr, o + 0x10)[0]
    cols = []
    for k in range(min(16, size // 2)):
        c = struct.unpack_from("<H", nclr, o + 0x18 + 2 * k)[0]
        cols.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))
    return cols + [(0, 0, 0)] * (16 - len(cols))


def b2_figure(a071, n):
    g = lz11((a071 / f"{8 * n + 1:04d}.bin").read_bytes())
    cols = palette(lz11((a071 / f"{8 * n + 7:04d}.bin").read_bytes()))
    o = block(g, b"RAHC")
    size, off = struct.unpack_from("<II", g, o + 0x18)
    px = []
    for b in g[o + 8 + off:o + 8 + off + size]:
        px += [b & 15, b >> 4]
    sheet = Image.new("P", (256, 128))
    sheet.putdata(px)
    return sheet.crop(figure_box(px, 256, 128, x0=128)), cols


def figure_box(px, w, h, x0):
    """Bounding box of the assembled trainer: the largest 8-connected blob right of x0,
    grown by any other blob that overlaps its (slightly padded) box (held items etc.)."""
    seen = [False] * (w * h)
    blobs = []
    for start in range(w * h):
        if seen[start] or not px[start] or start % w < x0:
            continue
        stack, box, count = [start], [w, h, 0, 0], 0
        seen[start] = True
        while stack:
            p = stack.pop()
            x, y = p % w, p // w
            count += 1
            box = [min(box[0], x), min(box[1], y), max(box[2], x + 1), max(box[3], y + 1)]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    q = ny * w + nx
                    if x0 <= nx < w and 0 <= ny < h and not seen[q] and px[q]:
                        seen[q] = True
                        stack.append(q)
        blobs.append((count, box))
    blobs.sort(reverse=True)
    box = list(blobs[0][1])
    for _, b in blobs[1:]:
        if b[0] < box[2] + 2 and b[2] > box[0] - 2 and b[1] < box[3] + 2 and b[3] > box[1] - 2:
            box = [min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3])]
    return tuple(box)


def to_frame(fig, cols):
    w, h = fig.size
    scale = min(1.0, 78 / w, 80 / h)   # keep the two bottom-right corner pixels clear for the encryption seed
    if scale < 1:
        fig = fig.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
    frame = Image.new("P", (80, 80), 0)
    frame.paste(fig, ((78 - fig.width) // 2, 80 - fig.height))
    frame.putpalette([c for rgb in cols for c in rgb])
    return frame


def main():
    a071, out = Path(sys.argv[1]), Path(sys.argv[2])
    for hg, b2 in SWAPS.items():
        fig, cols = b2_figure(a071, b2)
        frame = to_frame(fig, cols)
        frame.save(out / f"{hg:03d}.png")
        static = Image.new("P", (160, 80), 0)
        static.paste(frame, (0, 0))
        static.paste(frame, (80, 0))
        static.putpalette([c for rgb in cols for c in rgb])
        static.save(out / f"{hg:03d}_enc.png")
        for kind in ("cell", "anim"):
            shutil.copyfile(out / f"{ONE_CELL_TEMPLATE:03d}_{kind}.json", out / f"{hg:03d}_{kind}.json")
        print(f"class {hg:3d} <- Black 2 #{b2:3d}  ({fig.width}x{fig.height})")


if __name__ == "__main__":
    main()
