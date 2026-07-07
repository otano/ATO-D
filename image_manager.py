from pathlib import Path
from PIL import Image


def prepare_image(
    src_path: str | Path,
    output_dir: Path,
    max_width: float,
    max_height: float,
) -> Path:
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Image not found: {src}")

    img = Image.open(src)
    img.thumbnail((int(max_width), int(max_height)), Image.LANCZOS)

    dst = output_dir / f"{src.stem}_scaled{src.suffix}"
    img.save(dst)
    return dst
