from dataclasses import dataclass, field

from excel_reader import Section, Work, parse_dimensions


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
    offset_carte: float = 1700
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


def _compute_display_size(work: Work, col_w: float) -> tuple[float, float, float, float, bool]:
    marge = 100
    dims = parse_dimensions(work.dimensions)
    if dims is None:
        return 450, 600, 450 + 2*marge, 600 + 2*marge, False

    work_aspect = dims.work_h / dims.work_w if dims.work_w else 1.0
    max_w = col_w * 0.8
    max_h = 2000.0

    if dims.cadre_w and dims.cadre_h:
        cad_aspect = dims.cadre_h / dims.cadre_w
        if cad_aspect > 1.0:
            cadre_h = min(max_w * cad_aspect, max_h)
            cadre_w = cadre_h / cad_aspect
        else:
            cadre_w = max_w
            cadre_h = cadre_w * cad_aspect
    else:
        cadre_w = max_w
        cadre_h = cadre_w * max(work_aspect, 0.5)
        if cadre_h > max_h:
            cadre_h = max_h

    cadre_w = min(cadre_w, max_w)

    plan_w = cadre_w - 2 * marge
    plan_h = plan_w * work_aspect
    if plan_h > cadre_h - 2 * marge:
        plan_h = cadre_h - 2 * marge
        plan_w = plan_h / work_aspect

    return plan_w, plan_h, cadre_w, cadre_h, True


def compute_layout(sections: list[Section], config: LayoutConfig) -> list[PositionedWork]:
    start_y = 89280.0
    row_height = config.hauteur_image + 2 * config.marge_cadre + config.hauteur_texte_carte + 1700

    result: list[PositionedWork] = []
    for row_idx, section in enumerate(sections):
        y = start_y - row_idx * row_height
        for col_idx, work in enumerate(section.works):
            x = config.marge_gauche + col_idx * (config.largeur_colonne + config.espace_horizontal)
            plan_w, plan_h, cadre_w, cadre_h, has_dim = _compute_display_size(work, config.largeur_colonne)
            block_name = f"ART-{work.dexid}"
            result.append(PositionedWork(
                work=work, col=col_idx, row=row_idx,
                block_name=block_name,
                insert_x=x, insert_y=y,
                plan_w=plan_w, plan_h=plan_h,
                cadre_w=cadre_w, cadre_h=cadre_h,
                has_dimensions=has_dim,
                section_name=section.name,
            ))
    return result
