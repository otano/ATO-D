import re
from dataclasses import dataclass, field

from excel_reader import Section, Work, parse_dimensions


# Ligne offsets from section top
LIGNE_LAYERS = ["A8-ART no", "A8-ART no", "A6-VU 2", "A6-VU 2", "A2-CHIMASE", "Defpoints", "Defpoints"]

# Cumulative offsets from section top: start at 0, then add user's gaps
LIGNE_GAPS = [400, 1209, 800, 800, 100, 100]
_ligne_offsets = [0]
_cum = 0
for gap in LIGNE_GAPS:
    _cum += gap
    _ligne_offsets.append(_cum)
LIGNE_OFFSETS = tuple(_ligne_offsets)


def has_depth(dim_str: str | None) -> bool:
    if not dim_str:
        return False
    return bool(re.search(r"P\.?\s*[\d,]", dim_str))


@dataclass
class LayoutConfig:
    largeur_colonne: float = 1800
    hauteur_image: float = 600
    largeur_image: float = 450
    espace_horizontal: float = 250
    espace_vertical: float = 700
    marge_gauche: float = 400
    marge_haut: float = 300
    marge_cadre: float = 100
    largeur_carte: float = 1800
    hauteur_texte_carte: float = 80


@dataclass
class PositionedWork:
    work: Work
    col: int
    row: int
    block_name: str
    insert_x: float
    insert_y: float
    plan_w: float
    plan_h: float
    cadre_w: float
    cadre_h: float
    has_dimensions: bool = True
    section_name: str = ""
    has_depth: bool = False
    section_y: float = 0.0


def _compute_display_size(work: Work, marge_cadre: float) -> tuple[float, float, float, float, bool]:
    dims = parse_dimensions(work.dimensions)
    if dims is None:
        return 450, 600, 450 + 2 * marge_cadre, 600 + 2 * marge_cadre, False

    plan_w = dims.work_w * 10.0
    plan_h = dims.work_h * 10.0

    if dims.cadre_w and dims.cadre_h:
        cadre_w = dims.cadre_w * 10.0
        cadre_h = dims.cadre_h * 10.0
    else:
        cadre_w = plan_w + 2 * marge_cadre
        cadre_h = plan_h + 2 * marge_cadre

    return plan_w, plan_h, cadre_w, cadre_h, True


def compute_layout(sections: list[Section], config: LayoutConfig) -> list[PositionedWork]:
    row_height = LIGNE_OFFSETS[-1] + config.hauteur_texte_carte + 200
    start_y = 89280.0

    result: list[PositionedWork] = []
    for row_idx, section in enumerate(sections):
        section_top = start_y - row_idx * row_height
        for col_idx, work in enumerate(section.works):
            x = config.marge_gauche + col_idx * (config.largeur_colonne + config.espace_horizontal)
            plan_w, plan_h, cadre_w, cadre_h, has_dim = _compute_display_size(work, config.marge_cadre)
            block_name = f"ART-{work.dexid}"

            # Works with depth (P) go on ligne 3 (idx 2), others on ligne 1 (idx 0)
            dep = has_depth(work.dimensions)
            block_y = section_top - (LIGNE_OFFSETS[2] if dep else LIGNE_OFFSETS[0])

            result.append(PositionedWork(
                work=work, col=col_idx, row=row_idx,
                block_name=block_name,
                insert_x=x, insert_y=block_y,
                plan_w=plan_w, plan_h=plan_h,
                cadre_w=cadre_w, cadre_h=cadre_h,
                has_dimensions=has_dim,
                section_name=section.name,
                has_depth=dep,
                section_y=section_top,
            ))
    return result
