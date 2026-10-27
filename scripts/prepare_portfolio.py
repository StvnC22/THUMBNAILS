from pathlib import Path
from PIL import Image
import json
import re

SOURCE = Path(r"C:\Users\Stvn\Desktop\Miniaturas")
DEST = Path(__file__).resolve().parents[1] / "public" / "portfolio"
MANIFEST = Path(__file__).resolve().parents[1] / "src" / "data" / "portfolio.json"

DEST.mkdir(parents=True, exist_ok=True)
MANIFEST.parent.mkdir(parents=True, exist_ok=True)

items = []
png_files = sorted(
    (p for p in SOURCE.rglob("*") if p.is_file() and p.suffix.lower() == ".png"),
    key=lambda p: (p.parent.name.lower(), p.name.lower()),
)

for index, source in enumerate(png_files, start=1):
    client = source.parent.name
    safe_client = re.sub(r"[^a-z0-9-]+", "-", client.lower()).strip("-") or "cliente"
    target_name = f"{index:04d}-{safe_client}.png"
    target = DEST / target_name

    with Image.open(source) as image:
        image = image.convert("RGB")
        image.thumbnail((640, 360), Image.Resampling.LANCZOS)
        if image.size != (640, 360):
            canvas = Image.new("RGB", (640, 360), (10, 7, 22))
            canvas.paste(image, ((640 - image.width) // 2, (360 - image.height) // 2))
            image = canvas
        image = image.quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        image.save(target, format="PNG", optimize=True)

    items.append({
        "id": index,
        "src": f"/portfolio/{target_name}",
        "client": client,
        "creator": "BanneGFX",
        "original": source.name,
    })
    if index % 50 == 0 or index == len(png_files):
        print(f"Procesadas {index}/{len(png_files)}")

MANIFEST.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Manifest: {MANIFEST}")
