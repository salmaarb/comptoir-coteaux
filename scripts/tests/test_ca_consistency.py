"""
Test (famille 4) : cohérence du chiffre d'affaires.

Vérifie que :
  - ca_produit = price * total_sales pour chaque ligne (pas d'erreur de calcul),
  - aucun CA négatif ou nul de façon suspecte,
  - le CA total correspond à la valeur de référence d'Octave (70 568,60 €),
    à 1 centime près.

La constante CA_TOTAL_REF vient des chiffres transmis par Octave sur ce jeu
de données précis ; à ajuster si les exports source changent.
"""

import sys
import pandas as pd

CA_TOTAL_REF = 70568.60
TOLERANCE = 0.01


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
    if abs(ca_total - CA_TOTAL_REF) > TOLERANCE:
        errors.append(
            f"CA total = {ca_total} €, attendu {CA_TOTAL_REF} € (référence Octave)"
        )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK : CA total = {ca_total} €, cohérent avec la référence.")


if __name__ == "__main__":
    main()
