from __future__ import annotations

from pathlib import Path

import ezdxf
from ezdxf.entities import Wipeout

from excel_reader import Work
from layout import LayoutConfig


def _make_detail_text(work: Work) -> str:
    parts = []
    if work.author:
        line = work.author
        if work.title and work.title not in work.author:
            line += f"{{\\fArial|b0|i1|c0|p34;\\P{work.title}}}"
        parts.append(line)
    elif work.title:
        parts.append(work.title)
    if work.date:
        parts.append(f"\\P{work.date}")
    if work.dimensions:
        parts.append(f"\\P{work.dimensions}")
    if work.lender:
        parts.append(f"\\P\\P\\pxa0.25;{work.lender}")
    return "".join(parts)


def create_work_block(doc: ezdxf.drawing.Drawing, name: str, work: Work, cfg: LayoutConfig):
    plan_w, plan_h = cfg.largeur_image, cfg.hauteur_image
    marge = cfg.marge_cadre
    cadre_w = plan_w + 2 * marge
    cadre_h = plan_h + 2 * marge
    half_pw, half_ph = plan_w / 2, plan_h / 2
    half_cw, half_ch = cadre_w / 2, cadre_h / 2

    blk = doc.blocks.new(name)

    blk.add_wipeout([
        (-half_cw, -half_ch),
        (half_cw, -half_ch),
        (half_cw, half_ch),
        (-half_cw, half_ch),
        (-half_cw, -half_ch),
    ])
    for e in blk:
        if isinstance(e, Wipeout):
            e.dxf.layer = "A8-ART-cadre"
            break

    img_path = work.image_path
    if img_path and Path(img_path).exists():
        try:
            from PIL import Image as PILImage
            pil = PILImage.open(img_path)
            px, py = pil.size
            scale = min(plan_w / px, plan_h / py)
            disp_w = px * scale
            disp_h = py * scale
            img_def = doc.add_imagedef(str(Path(img_path).resolve()), px, py)
            img_def.dxf.layer = "A8-ART-works photo"
            img = blk.add_image(img_def, insert=(-half_pw, -half_ph), size_in_units=(disp_w, disp_h))
            img.dxf.layer = "A8-ART-works photo"
        except Exception:
            pass

    no_pos_y = half_ch + 75
    blk.add_mtext(
        work.dexid,
        dxfattribs={
            "layer": "A8-ART no",
            "style": "JP_50",
            "char_height": 90,
            "color": 152,
            "insert": (-half_cw, no_pos_y),
            "attachment_point": 4,
        },
    )

    blk.add_lwpolyline(
        [(-half_pw, -half_ph), (half_pw, -half_ph), (half_pw, half_ph), (-half_pw, half_ph), (-half_pw, -half_ph)],
        dxfattribs={"layer": "A8-ART-works plan", "color": 241},
    )

    blk.add_lwpolyline(
        [(-half_cw, -half_ch), (half_cw, -half_ch), (half_cw, half_ch), (-half_cw, half_ch), (-half_cw, -half_ch)],
        dxfattribs={"layer": "A8-ART-cadre", "color": 8},
    )

    return blk, plan_w, plan_h, cadre_w, cadre_h
