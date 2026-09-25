"""
Test (famille 4) : cohérence du chiffre d'affaires.

Vérifie systématiquement (quel que soit le mois/jeu de données) :
  - ca_produit = price * total_sales pour chaque ligne (pas d'erreur de calcul),
  - aucun CA négatif ou nul de façon suspecte.

"""

import json
import sys
from pathlib import Path
import pandas as pd

TOLERANCE = 0.01
REF_FILE = Path(__file__).resolve().parent / "reference_values.json"


def load_reference(key: str):
    if not REF_FILE.exists():
        return None
    with open(REF_FILE) as f:
        return json.load(f).get(key)


def main() -> None:
    df = pd.read_csv("data/clean/ca_par_produit.csv")
    errors = []

    recalculated = (df["price"] * df["total_sales"]).round(2)
    mismatches = (recalculated - df["ca_produit"]).abs() > TOLERANCE
    if mismatches.sum() > 0:
        errors.append(
            f"{mismatches.sum()} ligne(s) où ca_produit != price * total_sales"
        )

    negative = (df["ca_produit"] < 0).sum()
    if negative > 0:
        errors.append(f"{negative} ligne(s) avec un chiffre d'affaires négatif")

    ca_total = round(df["ca_produit"].sum(), 2)

    ca_total_ref = load_reference("ca_total_expected")
    if ca_total_ref is not None:
        if abs(ca_total - ca_total_ref) > TOLERANCE:
            errors.append(
                f"CA total = {ca_total} €, attendu {ca_total_ref} € (valeur de référence)"
            )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    ref_note = (
        f" (référence {ca_total_ref} € confirmée)"
        if ca_total_ref is not None
        else " (aucune valeur de référence fournie, vérification interne uniquement)"
    )
    print(f"OK : CA total = {ca_total} €, cohérent.{ref_note}")


if __name__ == "__main__":
    main()
