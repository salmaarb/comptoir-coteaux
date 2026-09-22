"""
Test (famille 5) : cohérence du z-score sur le prix et de la segmentation
premium/ordinaire.

Vérifie que :
  - tous les vins de vins_premium.csv ont bien z > 2 (recalculé indépendamment),
  - tous les vins de vins_ordinaires.csv ont bien z <= 2,
  - la somme des deux fichiers correspond au nombre total de vins,
  - le nombre de vins premium correspond à la valeur de référence d'Octave (30).

La constante PREMIUM_COUNT_REF vient des chiffres transmis par Octave sur ce
jeu de données précis ; à ajuster si les exports source changent.
"""

import sys
import pandas as pd

PREMIUM_COUNT_REF = 30


def main() -> None:
    ca = pd.read_csv("data/clean/ca_par_produit.csv")
    premium = pd.read_csv("outputs/vins_premium.csv")
    ordinaire = pd.read_csv("outputs/vins_ordinaires.csv")

    errors = []

    mean_price = ca["price"].mean()
    std_price = ca["price"].std()
    ca = ca.copy()
    ca["z_recalcule"] = (ca["price"] - mean_price) / std_price

    premium_prices = set(premium["price"].round(4))
    wrong_premium = ca[
        ca["price"].round(4).isin(premium_prices) & (ca["z_recalcule"] <= 2)
    ]
    if len(wrong_premium) > 0:
        errors.append(
            f"{len(wrong_premium)} vin(s) classé(s) premium avec un z recalculé <= 2"
        )

    ordinaire_prices = set(ordinaire["price"].round(4))
    wrong_ordinaire = ca[
        ca["price"].round(4).isin(ordinaire_prices) & (ca["z_recalcule"] > 2)
    ]
    if len(wrong_ordinaire) > 0:
        errors.append(
            f"{len(wrong_ordinaire)} vin(s) classé(s) ordinaire avec un z recalculé > 2"
        )

    if len(premium) + len(ordinaire) != len(ca):
        errors.append(
            f"premium ({len(premium)}) + ordinaire ({len(ordinaire)}) != total ({len(ca)})"
        )

    if len(premium) != PREMIUM_COUNT_REF:
        errors.append(
            f"{len(premium)} vin(s) premium détecté(s), attendu {PREMIUM_COUNT_REF} (référence Octave)"
        )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"OK : {len(premium)} vins premium, {len(ordinaire)} vins ordinaires, z-score cohérent."
    )


if __name__ == "__main__":
    main()
