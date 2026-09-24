"""
Étape 0 du pipeline : conversion des exports Excel en CSV.

Entrées  : data/Fichier_erp.xlsx, data/fichier_liaison.xlsx, data/Fichier_web.xlsx
Sorties  : data/brut/erp_brut.csv, data/brut/liaison_brut.csv, data/brut/web_brut.csv
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # racine du dépôt
DATA_DIR = ROOT / "data"
BRUT_DIR = DATA_DIR / "brut"
CLEAN_DIR = DATA_DIR / "clean"

SOURCES = {
    "Fichier_erp.xlsx": "erp_brut.csv",
    "fichier_liaison.xlsx": "liaison_brut.csv",
    "Fichier_web.xlsx": "web_brut.csv",
}


def main() -> None:
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    for xlsx_name, csv_name in SOURCES.items():
        src = DATA_DIR / xlsx_name
        if not src.exists():
            print(f"ERREUR : fichier source introuvable : {src}", file=sys.stderr)
            sys.exit(1)
        df = pd.read_excel(src)
        dest = BRUT_DIR / csv_name
        df.to_csv(dest, index=False)
        print(f"OK : {xlsx_name} -> {dest} ({len(df)} lignes brutes)")


if __name__ == "__main__":
    main()
