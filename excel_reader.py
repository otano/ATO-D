import io
from dataclasses import dataclass, field
from pathlib import Path
import re

import openpyxl
import pandas as pd
from PIL import Image as PILImage


@dataclass
class Work:
    dexid: str
    author: str
    title: str
    date: str
    dimensions: str
    lender: str
    inventory_number: str
    section: str
    image_path: str = ""
    presentation_conditions: str = ""


@dataclass
class WorkDimensions:
    work_h: float
    work_w: float
    cadre_h: float | None = None
    cadre_w: float | None = None


@dataclass
class Section:
    name: str
    works: list[Work] = field(default_factory=list)


def parse_dimensions(dim_str: str | None) -> WorkDimensions | None:
    if not dim_str:
        return None
    s = dim_str.strip()
    if not s or s in ("n. r.", "n.r.", "N. R.", "NR", "nr", "0"):
        return None

    parts = s.replace("\n", " ").split("avec cadre")
    sans_cadre = parts[0].replace("sans cadre", "").strip()
    avec_cadre = parts[1].strip() if len(parts) > 1 else ""

    def extract_hw(text: str):
        h = w = None
        m = re.search(r"H\.?\s*([0-9]+[.,]?[0-9]*)", text)
        if m:
            h = float(m.group(1).replace(",", "."))
        m = re.search(r"L\.?\s*([0-9]+[.,]?[0-9]*)", text)
        if m:
            w = float(m.group(1).replace(",", "."))
        m = re.search(r"([0-9]+[.,]?[0-9]*)\s*x\s*([0-9]+[.,]?[0-9]*)", text)
        if m and h is None:
            v1 = float(m.group(1).replace(",", "."))
            v2 = float(m.group(2).replace(",", "."))
            h, w = v2, v1
        return h, w

    work_h, work_w = extract_hw(sans_cadre)
    cadre_h, cadre_w = (extract_hw(avec_cadre) if avec_cadre else (None, None))

    if work_h is None and work_w is None:
        return None
    work_h = work_h or work_w
    work_w = work_w or work_h
    return WorkDimensions(work_h=work_h, work_w=work_w, cadre_h=cadre_h, cadre_w=cadre_w)


COLUMN_MAP = {
    "DEXID": "dexid",
    "Image": "image_path",
    "Auteur": "author",
    "Titre": "title",
    "Date": "date",
    "Dimensions": "dimensions",
    "Prêteur": "lender",
    "N° inventaire prêteur": "inventory_number",
    "Section": "section",
    "conditions de présentation": "presentation_conditions",
}


def _extract_images(filepath: str | Path, works: list[Work], links_dir: Path):
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    if not hasattr(ws, "_images"):
        return

    links_dir.mkdir(parents=True, exist_ok=True)

    for img in ws._images:
        df_idx = img.anchor._from.row - 1
        if df_idx < 0 or df_idx >= len(works):
            continue
        if works[df_idx].image_path:
            continue

        try:
            pil = PILImage.open(io.BytesIO(img._data()))
            ext = (pil.format or "png").lower()
            dst = links_dir / f"{works[df_idx].dexid}.{ext}"
            pil.save(dst)
            works[df_idx].image_path = str(dst.resolve())
        except Exception:
            pass


def read_excel(filepath: str | Path, links_dir: Path | None = None) -> list[Section]:
    df = pd.read_excel(filepath, dtype=str)
    df = df.where(pd.notna(df), "")

    rename = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename)

    field_names = list(Work.__dataclass_fields__)
    existing = [f for f in field_names if f in df.columns]
    works = [Work(**{f: row[f] for f in existing}) for _, row in df.iterrows()]

    if links_dir is not None:
        _extract_images(filepath, works, links_dir)

    sections: dict[str, Section] = {}
    for w in works:
        key = w.section or "Sans section"
        if key not in sections:
            sections[key] = Section(name=key)
        sections[key].works.append(w)

    return list(sections.values())
