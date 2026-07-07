from dataclasses import dataclass, field

from excel_reader import Section, Work


@dataclass
class LayoutConfig:
    largeur_colonne: float = 1800
    hauteur_cartouche: float = 950
    largeur_image: float = 450
    hauteur_image: float = 600
    espace_horizontal: float = 250
    espace_vertical: float = 700
    marge_gauche: float = 400
    marge_haut: float = 300


@dataclass
class PositionedWork:
    work: Work
    x: float
    y: float
    col: int = 0
    row: int = 0


def compute_layout(sections: list[Section], config: LayoutConfig) -> list[PositionedWork]:
    y = -config.marge_haut
    result: list[PositionedWork] = []

    for row, section in enumerate(sections):
        y -= config.hauteur_image + config.hauteur_cartouche + config.espace_vertical
        for col, work in enumerate(section.works):
            x = config.marge_gauche + col * (config.largeur_colonne + config.espace_horizontal)
            result.append(PositionedWork(work=work, x=x, y=y, col=col, row=row))

    return result
