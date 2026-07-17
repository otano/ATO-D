# ATO_A — Générateur d'accrochage d'exposition

Application Python qui lit un catalogue d'œuvres depuis un fichier Excel et génère automatiquement un plan d'accrochage en DXF/DWG (compatible AutoCAD).

## Fonctionnalités

- Lecture du fichier Excel contenant les œuvres (auteur, titre, dimensions, image, prêteur…)
- Extraction des images intégrées dans le fichier Excel
- Calcul automatique de la disposition spatiale des œuvres (colonnes, sections)
- Génération d'un fichier DXF avec :
  - Blocs AutoCAD contenant l'image, le cadre, le numéro et la fiche descriptive
  - Lignes de référence par section (cimaise, chimase, etc.)
  - Styles de cotation copiés depuis un fichier cible (`documentation/target.dxf`)
  - Annotation des dimensions réelles des œuvres (en mm)

## Prérequis

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets)

## Installation

```bash
git clone <url_du_depot>
cd ATO_A
uv sync
```

Cela crée l'environnement virtuel et installe les dépendances :

| Paquet      | Rôle                                     |
|-------------|------------------------------------------|
| `ezdxf`     | Génération de fichiers DXF/DWG           |
| `openpyxl`  | Lecture Excel et extraction d'images     |
| `pandas`    | Manipulation des données Excel           |
| `pillow`    | Traitement et redimensionnement d'images |
| `pyyaml`    | Lecture de la configuration YAML         |

## Utilisation

```bash
# Usage basique
uv run python main.py <fichier_excel.xlsx>

# Avec des options
uv run python main.py <fichier_excel.xlsx> -c config.yaml -o resultat.dxf
```

### Options

| Option              | Défaut         | Description                          |
|---------------------|----------------|--------------------------------------|
| `excel`             | *(requis)*     | Chemin vers le fichier Excel         |
| `-c, --config`      | `config.yaml`  | Fichier de configuration YAML        |
| `-o, --output`      | `output.dxf`   | Chemin de sortie du fichier DXF      |

## Configuration (`config.yaml`)

Toutes les valeurs sont en unités DXF (mm).

| Paramètre            | Défaut | Description                                                         |
|----------------------|--------|---------------------------------------------------------------------|
| `largeur_colonne`    | 1800   | Largeur de chaque colonne (emplacement d'œuvre)                     |
| `hauteur_image`      | 600    | Hauteur par défaut de l'image (pas de dimensions)                   |
| `largeur_image`      | 450    | Largeur par défaut de l'image (pas de dimensions)                   |
| `espace_horizontal`  | 250    | Espace horizontal entre les colonnes                                |
| `espace_vertical`    | 700    | Espace vertical entre les sections                                  |
| `marge_gauche`       | 400    | Marge à gauche depuis l'origine                                     |
| `marge_haut`         | 300    | Marge en haut                                                       |
| `marge_cadre`        | 100    | Marge autour de l'œuvre quand les dimensions du cadre sont inconnues|
| `largeur_carte`      | 1800   | Largeur de la fiche descriptive sous chaque œuvre                   |
| `hauteur_texte_carte`| 80     | Hauteur du caractère sur la fiche descriptive                       |

## Structure du projet

```
ATO_A/
├── main.py              # Point d'entrée CLI
├── excel_reader.py      # Lecture Excel → objets Python
├── layout.py            # Moteur de disposition spatiale
├── dwg_generator.py     # Génération DXF (backend ezdxf)
├── blocks.py            # Définitions des blocs AutoCAD
├── styles.py            # Styles de texte et définitions de calques
├── image_manager.py     # Utilitaire de redimensionnement d'images
├── config.yaml          # Paramètres de disposition
├── documentation/
│   └── target.dxf       # Fichier DXF de référence (cotes, styles)
└── links/               # Images extraites du fichier Excel
```

## Architecture

L'application suit une architecture en 3 couches, séparant les préoccupations :

```
┌─────────────────────────────────────────────┐
│              FICHIER EXCEL                  │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  COUCHE 1 : excel_reader.py                │
│  Données pures, pas de CAD                 │
│  → list[Section] contenant des Work         │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  COUCHE 2 : layout.py                      │
│  Calcul des positions, pas de CAD           │
│  → list[PositionedWork]                     │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  COUCHE 3 : dwg_generator.py + blocks.py   │
│  Backend ezdxf — écriture du DXF           │
│  → output.dxf                               │
└─────────────────────────────────────────────┘
```

### Rôles des modules

| Module              | Couche | Rôle                                                               |
|---------------------|--------|--------------------------------------------------------------------|
| `main.py`           | CLI    | Orchestration : parsing args → lecture → layout → génération       |
| `excel_reader.py`   | 1      | Extraction des données Excel, parsing des dimensions (notation FR) |
| `layout.py`         | 2      | Calcul des positions X/Y de chaque œuvre dans la grille            |
| `dwg_generator.py`  | 3      | Création du document DXF, insertion des blocs et annotations       |
| `blocks.py`         | 3      | Définition des blocs AutoCAD (image + cadre + fiche)               |
| `styles.py`         | 3      | Définitions des calques (28) et styles de texte (14)               |
| `image_manager.py`  | util   | Utilitaire de redimensionnement d'images (Pillow)                  |

### Format des dimensions

Le lecteur Excel gère la notation française des dimensions :

- `H. 80 L. 60` → hauteur 80 cm, largeur 60 cm
- `H. 80 L. 60 avec cadre H. 90 L. 70` → dimensions œuvre + cadre
- `H. 80 L. 60 P. 10` → œuvre avec profondeur ( placée sur ligne 3 )

Les œuvres sans dimensions valides utilisent les valeurs par défaut (`largeur_image` × `hauteur_image`).

### Calques DXF

Le projet définit 28 calques organisés par fonction :

- **A8-ART-*** :Œuvres (plan, photo, cadre, détail, numéro)
- **A7-TXT-*** : Textes d'annotation (tailles 5 à 200)
- **A6-VU** : Vues en élévation
- **A2-CHIMASE / A2-CIMAISE H** : Matériel d'accrochage
- **A4-SOCLE** : Socles
- **Defpoints** : Points de référence (non imprimés)

## Sortie

Le fichier DXF généré contient :

1. Un **bloc AutoCAD** par œuvre avec :
   - Image de l'œuvre (ou hachurée si pas d'image)
   - Contour du cadre
   - Numéro d'identification (DEXID)
   - Fiche descriptive (auteur, titre, date, dimensions, prêteur)
2. Des **lignes de référence** par section (cimaise, chimase, etc.)
3. Les **styles de cotation** copiés depuis `documentation/target.dxf`
