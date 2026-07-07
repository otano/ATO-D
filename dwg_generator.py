from __future__ import annotations

from pathlib import Path

import ezdxf

from blocks import create_work_block, _make_detail_text
from layout import LayoutConfig, PositionedWork
from styles import LAYERS


def _setup_styles(doc: ezdxf.drawing.Drawing):
    existing = {s.dxf.name for s in doc.styles}
    specs = {
        "JP_50": ("arial.ttf", 90),
        "AtoY_40": ("arial.ttf", 80),
    }
    for name, (font, height) in specs.items():
        if name not in existing:
            doc.styles.new(name, dxfattribs={"font": font, "height": height})


def _make_block_name(pw: PositionedWork) -> str:
    raw = pw.block_name
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    return safe[:64]


def generate_dxf(works: list[PositionedWork], config: LayoutConfig, output_path: Path) -> Path:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for layer_def in LAYERS.values():
        doc.layers.add(name=layer_def["name"], color=layer_def["color"])

    _setup_styles(doc)

    for pw in works:
        bname = _make_block_name(pw)
        create_work_block(doc, bname, pw.work, config)

        cx, cy = pw.insert_x, pw.insert_y
        msp.add_blockref(bname, insert=(cx, cy), dxfattribs={"layer": "A8-ART-works plan"})

        card_x = cx - pw.cadre_w / 2
        no_y = cy - config.offset_carte
        detail_y = no_y - 100

        msp.add_mtext(
            pw.work.dexid,
            dxfattribs={
                "layer": "A8-ART no",
                "style": "JP_50",
                "char_height": 90,
                "color": 152,
                "insert": (card_x, no_y),
                "attachment_point": 4,
                "width": config.largeur_carte,
            },
        )

        detail_text = _make_detail_text(pw.work)
        if detail_text.strip("\\P"):
            msp.add_mtext(
                detail_text,
                dxfattribs={
                    "layer": "A8-ART-detail",
                    "style": "AtoY_40",
                    "char_height": config.hauteur_texte_carte,
                    "color": 230,
                    "insert": (card_x, detail_y),
                    "attachment_point": 1,
                    "width": config.largeur_carte,
                },
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(output_path))
    return output_path
