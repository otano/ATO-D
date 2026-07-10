from __future__ import annotations

from itertools import groupby
from pathlib import Path

import ezdxf

from blocks import create_work_block, _make_detail_text
from layout import LIGNE_OFFSETS, LIGNE_LAYERS, LayoutConfig, PositionedWork
from styles import LAYERS, TEXT_STYLES


def _make_block_name(pw: PositionedWork) -> str:
    raw = pw.block_name
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    return safe[:64]


def _setup_layers_and_styles(doc: ezdxf.drawing.Drawing):
    existing_layers = {l.dxf.name: l for l in doc.layers}
    for layer_def in LAYERS:
        kwargs = {k: v for k, v in layer_def.items() if v is not None}
        if "color" in kwargs:
            kwargs["color"] = abs(kwargs["color"])
        name = kwargs.pop("name")
        if name in existing_layers:
            layer = existing_layers[name]
            for k, v in kwargs.items():
                setattr(layer.dxf, k, v)
        else:
            doc.layers.add(name=name, **kwargs)

    existing_styles = {s.dxf.name for s in doc.styles}
    for st in TEXT_STYLES:
        if st["name"] not in existing_styles:
            doc.styles.new(name=st["name"], dxfattribs={
                "font": st["font"], "height": st["height"], "width": st["width"],
            })


DIMSTYLES_PROPS = [
    {"name": "AtoY_cot_5",   "dimtxt": 10.0,  "dimasz": 5.0,   "dimgap": 2.5},
    {"name": "AtoY_cot_10",  "dimtxt": 20.0,  "dimasz": 10.0,  "dimgap": 5.0},
    {"name": "AtoY_cot_20",  "dimtxt": 40.0,  "dimasz": 20.0,  "dimgap": 10.0},
    {"name": "AtoY_cot_30",  "dimtxt": 60.0,  "dimasz": 30.0,  "dimgap": 15.0},
    {"name": "AtoY_cot_40",  "dimtxt": 80.0,  "dimasz": 40.0,  "dimgap": 20.0},
    {"name": "AtoY_cot_50",  "dimtxt": 100.0, "dimasz": 50.0,  "dimgap": 25.0},
    {"name": "AtoY_cot_100", "dimtxt": 200.0, "dimasz": 100.0, "dimgap": 50.0},
    {"name": "AtoY_cot_150", "dimtxt": 300.0, "dimasz": 150.0, "dimgap": 75.0},
    {"name": "AtoY_cot_200", "dimtxt": 400.0, "dimasz": 200.0, "dimgap": 100.0},
]

DIMSTYLE_COMMON = {
    "dimadec": 1,
    "dimaltd": 3,
    "dimaltf": 0.03937007874016,
    "dimalttd": 3,
    "dimblk": "_DotSmall",
    "dimcen": 5.0,
    "dimdec": 0,
    "dimdli": 0.0,
    "dimdsep": 44,
    "dimexe": 0.0,
    "dimexo": 0.0,
    "dimjogang": 90.0,
    "dimldrblk": "_DotSmall",
    "dimtad": 1,
    "dimtdec": 0,
    "dimtih": 0,
    "dimtofl": 1,
    "dimtoh": 0,
    "dimtolj": 0,
    "dimtzin": 8,
    "dimzin": 8,
}


def _copy_style_annotations(doc: ezdxf.drawing.Drawing, target_path: Path | str):
    target = ezdxf.readfile(str(target_path))

    existing_ds = {d.dxf.name for d in doc.dimstyles}
    existing_bs = {b.name for b in doc.blocks}

    if "_DotSmall" not in existing_bs:
        src_block = target.blocks["_DotSmall"]
        e = list(src_block)[0]
        points = list(e.get_points())
        blk = doc.blocks.new("_DotSmall")
        blk.add_lwpolyline(points, dxfattribs={
            "color": 0,
            "const_width": 0.5,
            "linetype": "ByBlock",
        })

    for ds in DIMSTYLES_PROPS:
        if ds["name"] in existing_ds:
            continue
        style = ds["name"]
        attrs = dict(DIMSTYLE_COMMON)
        attrs.update(ds)
        attrs["dimtxsty"] = style.replace("cot_", "")
        doc.dimstyles.new(name=style, dxfattribs=attrs)

    msp = doc.modelspace()
    anchor_x = -2000.0
    anchor_y = 6000.0

    for e in target.modelspace():
        if not e.dxf.layer.startswith("A7"):
            continue
        dxf = e.dxf

        if e.dxftype() == "MTEXT":
            raw_y = dxf.insert[1]
            offset_y = raw_y - 78566.0
            msp.add_mtext(
                e.text,
                dxfattribs={
                    "layer": dxf.layer,
                    "style": dxf.style,
                    "char_height": dxf.char_height,
                    "insert": (anchor_x, anchor_y + offset_y),
                    "attachment_point": dxf.attachment_point,
                },
            )

        elif e.dxftype() == "DIMENSION":
            src_dp = dxf.defpoint
            src_ext1 = dxf.defpoint3
            src_ext2 = dxf.defpoint2
            delta_y = src_dp[1] - 78566.0
            ext_y = anchor_y + delta_y - (src_dp[1] - src_ext1[1])
            dim_ov = msp.add_linear_dim(
                base=(src_dp[0], anchor_y + delta_y, 0),
                p1=(src_ext1[0], ext_y, 0),
                p2=(src_ext2[0], ext_y, 0),
                dimstyle=dxf.dimstyle,
                dxfattribs={"layer": dxf.layer},
            )
            dim_ov.render()


def generate_dxf(works: list[PositionedWork], config: LayoutConfig, output_path: Path) -> Path:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    _setup_layers_and_styles(doc)

    target_path = Path(__file__).parent / "documentation" / "target.dxf"
    if target_path.exists():
        _copy_style_annotations(doc, target_path)

    for pw in works:
        bname = _make_block_name(pw)
        create_work_block(
            doc, bname, pw.work,
            plan_w=pw.plan_w, plan_h=pw.plan_h,
            cadre_w=pw.cadre_w, cadre_h=pw.cadre_h,
            has_dimensions=pw.has_dimensions,
        )

        cx, cy = pw.insert_x, pw.insert_y
        msp.add_blockref(bname, insert=(cx, cy), dxfattribs={"layer": "0"})

        card_x = cx - pw.cadre_w / 2
        sy = pw.section_y
        if pw.has_depth:
            no_y = sy - LIGNE_OFFSETS[5]
        else:
            no_y = sy - LIGNE_OFFSETS[1]

        detail_y = sy - LIGNE_OFFSETS[6]

        msp.add_mtext(
            pw.work.dexid,
            dxfattribs={
                "layer": "A8-ART no",
                "style": "JP_50",
                "char_height": 90,
                "color": 152,
                "insert": (card_x, no_y),
                "attachment_point": 8,
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
                    "attachment_point": 4,
                    "width": config.largeur_carte,
                },
            )

    _draw_section_lines(msp, works)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(output_path))
    return output_path


def _draw_section_lines(msp, works: list[PositionedWork]):
    for _row, group in groupby(works, key=lambda w: w.row):
        group_list = list(group)
        sy = group_list[0].section_y
        x_min = min(pw.insert_x - pw.cadre_w / 2 for pw in group_list)
        x_max = max(pw.insert_x + pw.cadre_w / 2 for pw in group_list)
        padding = 1500
        x1 = x_min - padding
        x2 = x_max + padding

        for i, layer in enumerate(LIGNE_LAYERS):
            ly = sy - LIGNE_OFFSETS[i]
            msp.add_line((x1, ly), (x2, ly), dxfattribs={"layer": layer})
