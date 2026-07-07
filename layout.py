from dataclasses import dataclass, field

from excel_reader import Section, Work


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
    offset_carte: float = 1800
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


def compute_layout(sections: list[Section], config: LayoutConfig) -> list[PositionedWork]:
    start_y = 89280.0
    row_height = config.hauteur_image + 2 * config.marge_cadre + config.hauteur_texte_carte + 1700

    result: list[PositionedWork] = []
    for row_idx, section in enumerate(sections):
        y = start_y - row_idx * row_height
        for col_idx, work in enumerate(section.works):
            x = config.marge_gauche + col_idx * (config.largeur_colonne + config.espace_horizontal)
            plan_w = config.largeur_image
            plan_h = config.hauteur_image
            cadre_w = plan_w + 2 * config.marge_cadre
            cadre_h = plan_h + 2 * config.marge_cadre
            block_name = f"ART-{work.dexid}"
            result.append(PositionedWork(
                work=work, col=col_idx, row=row_idx,
                block_name=block_name,
                insert_x=x, insert_y=y,
                plan_w=plan_w, plan_h=plan_h,
                cadre_w=cadre_w, cadre_h=cadre_h,
            ))
    return result
