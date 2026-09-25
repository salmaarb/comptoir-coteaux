"""
Test (famille 5) : cohérence du z-score sur le prix et de la segmentation
premium/ordinaire.

"""

import json
import sys
from pathlib import Path
import pandas as pd

REF_FILE = Path(__file__).resolve().parent / "reference_values.json"


def load_reference(key: str):
    if not REF_FILE.exists():
        return None
    with open(REF_FILE) as f:
        return json.load(f).get(key)


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

    premium_ref = load_reference("premium_count_expected")
    if premium_ref is not None and len(premium) != premium_ref:
        errors.append(
            f"{len(premium)} vin(s) premium détecté(s), attendu {premium_ref} (valeur de référence)"
        )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    ref_note = (
        f" (référence {premium_ref} confirmée)"
        if premium_ref is not None
        else " (aucune valeur de référence fournie, vérification interne uniquement)"
    )
    print(
        f"OK : {len(premium)} vins premium, {len(ordinaire)} vins ordinaires, z-score cohérent.{ref_note}"
    )


if __name__ == "__main__":
    main()
