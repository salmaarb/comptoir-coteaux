"""
Test (famille 3) : cohérence de la jointure ERP ⋈ Liaison ⋈ Web.

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
    fusion = pd.read_csv("data/clean/fusion.csv")
    web_clean = pd.read_csv("data/clean/web_clean.csv")

    errors = []

    key_columns = ["product_id", "sku", "price", "total_sales"]
    for col in key_columns:
        missing = fusion[col].isnull().sum()
        if missing > 0:
            errors.append(
                f"{missing} valeur(s) manquante(s) dans la colonne '{col}' du fichier fusionné"
            )

    if len(fusion) != len(web_clean):
        errors.append(
            f"Le fichier fusionné a {len(fusion)} lignes, "
            f"mais web_clean.csv (le fichier le plus restrictif) en a {len(web_clean)} : "
            "la jointure a perdu ou dupliqué des lignes de façon inattendue."
        )

    web_rows_ref = load_reference("web_clean_rows_expected")
    if web_rows_ref is not None and len(fusion) != web_rows_ref:
        errors.append(
            f"Le fichier fusionné a {len(fusion)} lignes, "
            f"attendu {web_rows_ref} (valeur de référence)."
        )

    if fusion["sku"].duplicated().sum() > 0:
        errors.append(
            "Des doublons de sku sont apparus après la jointure (fan-out inattendu)."
        )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    ref_note = (
        f" (référence {web_rows_ref} confirmée)"
        if web_rows_ref is not None
        else " (aucune valeur de référence fournie, vérification interne uniquement)"
    )
    print(f"OK : jointure cohérente, {len(fusion)} lignes.{ref_note}")


if __name__ == "__main__":
    main()
