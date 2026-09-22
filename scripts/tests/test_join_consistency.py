"""
Test (famille 3) : cohérence de la jointure ERP ⋈ Liaison ⋈ Web.

Vérifie que :
  - le fichier fusionné n'a aucune valeur manquante sur les colonnes clés,
  - son nombre de lignes correspond au fichier le plus restrictif des trois
    (le web, qui pilote la jointure) et à la valeur de référence d'Octave.

La valeur de référence (WEB_CLEAN_REF_ROWS = 714) vient des chiffres
transmis par Octave sur ce jeu de données précis ; si les exports source
changent de volumétrie, ajustez cette constante en conséquence.
"""

import sys
import pandas as pd

WEB_CLEAN_REF_ROWS = 714


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

    if len(fusion) != WEB_CLEAN_REF_ROWS:
        errors.append(
            f"Le fichier fusionné a {len(fusion)} lignes, "
            f"attendu {WEB_CLEAN_REF_ROWS} d'après les valeurs de référence d'Octave."
        )

    if fusion["sku"].duplicated().sum() > 0:
        errors.append(
            "Des doublons de sku sont apparus après la jointure (fan-out inattendu)."
        )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"OK : jointure cohérente, {len(fusion)} lignes, aucune valeur manquante sur les colonnes clés."
    )


if __name__ == "__main__":
    main()
