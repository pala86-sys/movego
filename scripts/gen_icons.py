"""產生 PWA 用的簡易點陣圖示（純 stdlib，不依賴 Pillow），僅供開發測試使用。"""
import struct
import zlib
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "icons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BLUE = (0, 112, 189)
WHITE = (255, 255, 255)


def make_png(size: int, path: Path) -> None:
    cx = cy = size / 2
    radius = size * 0.32
    bar_w = size * 0.5
    bar_h = size * 0.14

    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            dx, dy = x - cx, y - cy
            in_circle = dx * dx + dy * dy <= radius * radius
            in_bar = abs(dx) <= bar_w / 2 and abs(dy - radius * 0.15) <= bar_h / 2
            color = WHITE if (in_circle and not in_bar) else BLUE
            row.extend(color)
        rows.append(bytes([0]) + bytes(row))

    raw = b"".join(rows)
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.write_bytes(png)


for size in (192, 512):
    make_png(size, OUT_DIR / f"icon-{size}.png")

print("icons written to", OUT_DIR)
