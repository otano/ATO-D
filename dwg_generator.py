from __future__ import annotations

from pathlib import Path

import ezdxf

from blocks import draw_artwork
from layout import LayoutConfig, PositionedWork
from styles import LAYERS


def generate_dxf(works: list[PositionedWork], config: LayoutConfig, output_path: Path) -> Path:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for layer_def in LAYERS.values():
        doc.layers.add(name=layer_def["name"], color=layer_def["color"])

    for pw in works:
        draw_artwork(msp, pw, config)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(output_path))
    return output_path
