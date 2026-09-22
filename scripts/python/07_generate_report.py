"""
Segmentation premium/ordinaire par z-score sur le prix.

z = (prix - moyenne des prix) / écart-type des prix
Un vin est premium si z > 2, ordinaire sinon.

Ce script contient la seule logique statistique du pipeline (pandas) ;
le reste (nettoyage, jointure, agrégation) reste en SQL/DuckDB.

Usage : python 06_zscore_segmentation.py
Entrée  : data/clean/ca_par_produit.csv
Sorties : outputs/vins_premium.csv, outputs/vins_ordinaires.csv
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

    mean_price = df["price"].mean()
    std_price = df["price"].std()  # écart-type d'échantillon (ddof=1)

    if std_price == 0 or pd.isna(std_price):
        print("ERREUR : écart-type nul ou indéfini, z-score impossible.", file=sys.stderr)
        sys.exit(1)

    df["z_score"] = (df["price"] - mean_price) / std_price

    premium = df[df["z_score"] > 2].sort_values("price", ascending=False)
    ordinaire = df[df["z_score"] <= 2].sort_values("price", ascending=False)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    premium.to_csv(OUTPUTS_DIR / "vins_premium.csv", index=False)
    ordinaire.to_csv(OUTPUTS_DIR / "vins_ordinaires.csv", index=False)

    print(f"Moyenne des prix : {mean_price:.2f} € | Écart-type : {std_price:.2f} €")
    print(f"Vins premium (z > 2) : {len(premium)}")
    print(f"Vins ordinaires (z <= 2) : {len(ordinaire)}")


if __name__ == "__main__":
    main()
