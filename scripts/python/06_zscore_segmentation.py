"""
Étape 0 du pipeline : conversion des exports Excel en CSV.

Kestra orchestre, il ne traite pas : ce script ne contient AUCUNE logique métier
(pas de nettoyage, pas de filtre). Il se contente de rendre les 3 exports sources
lisibles par DuckDB (SQL), qui ne lit pas nativement le format .xlsx hors ligne.

Usage : python 00_convert_xlsx_to_csv.py
Entrées  : data/Fichier_erp.xlsx, data/fichier_liaison.xlsx, data/Fichier_web.xlsx
Sorties  : data/staging/erp_raw.csv, liaison_raw.csv, web_raw.csv
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # racine du dépôt
DATA_DIR = ROOT / "data"
STAGING_DIR = DATA_DIR / "staging"

SOURCES = {
    "Fichier_erp.xlsx": "erp_raw.csv",
    "fichier_liaison.xlsx": "liaison_raw.csv",
    "Fichier_web.xlsx": "web_raw.csv",
}


def main() -> None:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    for xlsx_name, csv_name in SOURCES.items():
        src = DATA_DIR / xlsx_name
        if not src.exists():
            print(f"ERREUR : fichier source introuvable : {src}", file=sys.stderr)
            sys.exit(1)
        df = pd.read_excel(src)
        dest = STAGING_DIR / csv_name
        df.to_csv(dest, index=False)
        print(f"OK : {xlsx_name} -> {dest} ({len(df)} lignes brutes)")


if __name__ == "__main__":
    main()
