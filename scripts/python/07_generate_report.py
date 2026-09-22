"""
Génération du rapport Excel : chiffre d'affaires par produit + chiffre
d'affaires total, sur une feuille dédiée.

Usage : python 07_generate_report.py
Entrée  : data/clean/ca_par_produit.csv
Sortie  : outputs/rapport_ca.xlsx
"""

from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEAN_FILE = ROOT / "data" / "clean" / "ca_par_produit.csv"
OUTPUTS_DIR = ROOT / "outputs"


def main() -> None:
    if not CLEAN_FILE.exists():
        print(f"ERREUR : fichier introuvable : {CLEAN_FILE}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(CLEAN_FILE)
    ca_total = round(df["ca_produit"].sum(), 2)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUTS_DIR / "rapport_ca.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="CA par produit", index=False)
        pd.DataFrame([{"chiffre_affaires_total": ca_total}]).to_excel(
            writer, sheet_name="CA total", index=False
        )

    print(f"Rapport généré : {out_path}")
    print(f"Chiffre d'affaires total : {ca_total} €")


if __name__ == "__main__":
    main()
