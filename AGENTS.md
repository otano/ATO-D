# ATO_A — Auto DWG from Excel

## Stack & tooling

- **Python** managed with `uv` — add deps via `uv add <pkg>`, run via `uv run python main.py <excel>`
- Core deps: `pandas`, `openpyxl` (Excel reading), `ezdxf` (DXF/DWG generation), `Pillow` (image scaling)
- Cross‑platform (macOS + Windows) — `ezdxf` backend, no AutoCAD COM dependency
- Windows option: `pyautocad` can be added as optional backend later
- Config in `config.yaml` (layout dimensions, margins, image sizes)

## Project structure

```
main.py              ← entrypoint
excel_reader.py      ← Excel → Pandas DataFrame → Python objects
layout.py            ← auto-layout engine (section rows, column grid)
dwg_generator.py     ← ezdxf writer (pluggable backend)
image_manager.py     ← image fetching / scaling / xref
blocks.py            ← AutoCAD block definitions
styles.py            ← text styles, layers, colors
```

## Architecture (3 layers)

1. **Excel → Python objects** — `excel_reader.py` (pure data, no CAD)
2. **Layout engine** — `layout.py` (positions independent of CAD backend)
3. **DWG generator** — `dwg_generator.py` + `blocks.py` (one backend = one class, currently `ezdxf`)

This lets you swap the DWG backend or the layout without touching the other layers.

## Layout rules

- Each Excel `Section` becomes a horizontal row
- Works are placed in a column grid: `X = marge + colonne × largeur_colonne`, `Y = section × hauteur`
- Every work is an AutoCAD block (`ARTWORK`) containing: image, frame, number, info card, attributes
- Images can be embedded, xref'd, or copied to an `images/` folder

## Key config (config.yaml)

```yaml
largeur_colonne: 1800
hauteur_cartouche: 950
largeur_image: 450
hauteur_image: 600
espace_horizontal: 250
espace_vertical: 700
marge_gauche: 400
marge_haut: 300
```

## Committing

- French commit messages
- One commit per feature, logical scope
