from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd


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
class Section:
    name: str
    works: list[Work] = field(default_factory=list)


COLUMN_MAP = {
    "DEXID": "dexid",
    "Image": "image_path",
    "Auteur": "author",
    "Titre": "title",
    "Date": "date",
    "Dimensions": "dimensions",
    "Prêteur": "lender",
    "N° inventaire": "inventory_number",
    "Section": "section",
    "Conditions de présentation": "presentation_conditions",
}


def read_excel(filepath: str | Path) -> list[Section]:
    df = pd.read_excel(filepath, dtype=str)
    df = df.where(pd.notna(df), "")

    rename = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename)

    works = [Work(**{f.name: row[f.name] for f in Work.__dataclass_fields__ if f.name in row.index}) for _, row in df.iterrows()]

    sections: dict[str, Section] = {}
    for w in works:
        key = w.section or "Sans section"
        if key not in sections:
            sections[key] = Section(name=key)
        sections[key].works.append(w)

    return list(sections.values())
