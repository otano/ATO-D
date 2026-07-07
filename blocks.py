from __future__ import annotations

import ezdxf
from ezdxf.math import Vec2
from ezdxf import colors

from layout import LayoutConfig, PositionedWork


def draw_artwork(msp: ezdxf.layouts.Modelspace, pw: PositionedWork, cfg: LayoutConfig):
    x, y = pw.x, pw.y
    col_w = cfg.largeur_colonne
    img_w = cfg.largeur_image
    img_h = cfg.hauteur_image
    card_h = cfg.hauteur_cartouche

    img_x = x + (col_w - img_w) / 2
    img_y = y - img_h

    card_top = img_y
    card_bot = card_top - card_h

    # Image frame
    msp.add_lwpolyline(
        [
            (img_x, y),
            (img_x + img_w, y),
            (img_x + img_w, img_y),
            (img_x, img_y),
            (img_x, y),
        ],
        dxfattribs={"layer": "FRAME", "color": colors.WHITE},
    )

    # Cartouche frame
    msp.add_lwpolyline(
        [
            (x, card_top),
            (x + col_w, card_top),
            (x + col_w, card_bot),
            (x, card_bot),
            (x, card_top),
        ],
        dxfattribs={"layer": "FRAME", "color": colors.WHITE},
    )

    # DEXID label (large, top-left of image)
    msp.add_text(
        pw.work.dexid,
        dxfattribs={
            "layer": "TITLE",
            "height": 80,
            "color": colors.YELLOW,
            "insert": (img_x + 10, y - 10),
        },
    )

    # Cartouche text
    lines = [
        pw.work.author,
        pw.work.title,
        pw.work.date,
        pw.work.dimensions,
        pw.work.lender,
    ]
    lines = [ln.strip() for ln in lines if ln.strip()]

    msp.add_mtext(
        "\n".join(lines),
        dxfattribs={
            "layer": "TEXT",
            "char_height": 50,
            "color": colors.GREEN,
            "insert": (x + 20, card_top - 30),
            "line_spacing_factor": 1.5,
            "attachment_point": 1,  # top-left
        },
    )
