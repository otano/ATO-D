import argparse
import sys
from pathlib import Path

import yaml

from dwg_generator import generate_dxf
from excel_reader import read_excel
from layout import LayoutConfig, compute_layout


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate DWG/DXF from Excel exhibition data")
    parser.add_argument("excel", type=Path, help="Path to the Excel file")
    parser.add_argument("-c", "--config", type=Path, default=Path("config.yaml"), help="Config YAML")
    parser.add_argument("-o", "--output", type=Path, default=Path("output.dxf"), help="Output DXF path")
    args = parser.parse_args()

    if not args.excel.exists():
        print(f"Error: Excel file not found: {args.excel}", file=sys.stderr)
        sys.exit(1)

    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    with open(args.config) as f:
        raw = yaml.safe_load(f)
    cfg = LayoutConfig(**raw)

    sections = read_excel(args.excel)
    if not sections:
        print("No data found in Excel file", file=sys.stderr)
        sys.exit(1)

    works = compute_layout(sections, cfg)
    result = generate_dxf(works, cfg, args.output)

    section_count = len(sections)
    work_count = sum(len(s.works) for s in sections)
    print(f"Generated {result} — {section_count} section(s), {work_count} work(s)")


if __name__ == "__main__":
    main()
