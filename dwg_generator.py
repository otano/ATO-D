from __future__ import annotations

from pathlib import Path

import ezdxf

from blocks import create_work_block, _make_detail_text
from layout import LayoutConfig, PositionedWork
from styles import LAYERS, TEXT_STYLES


def _make_block_name(pw: PositionedWork) -> str:
    raw = pw.block_name
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    return safe[:64]


def generate_dxf(works: list[PositionedWork], config: LayoutConfig, output_path: Path) -> Path:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    existing_layers = {l.dxf.name for l in doc.layers}
    for layer_def in LAYERS:
        if layer_def["name"] in existing_layers:
            continue
        kwargs = {k: v for k, v in layer_def.items() if v is not None}
        if "color" in kwargs:
            kwargs["color"] = abs(kwargs["color"])
        doc.layers.add(name=kwargs.pop("name"), **kwargs)

    existing_styles = {s.dxf.name for s in doc.styles}
    for st in TEXT_STYLES:
        if st["name"] not in existing_styles:
            doc.styles.new(name=st["name"], dxfattribs={
                "font": st["font"], "height": st["height"], "width": st["width"],
            })

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
