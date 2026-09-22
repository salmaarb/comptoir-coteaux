"""
Test générique (familles 1 et 2) : absence de doublons sur la/les clé(s)
primaire(s), et absence de valeurs manquantes sur les colonnes critiques.

Usage :
    python test_clean_file.py <chemin_csv> <colonnes_cle_separees_par_virgule> <colonnes_requises_separees_par_virgule>

Exemple :
    python test_clean_file.py data/clean/erp_clean.csv product_id product_id,price,stock_quantity
"""

import sys
import pandas as pd


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "ERREUR : usage python test_clean_file.py <csv> <cle1,cle2> <col1,col2,...>",
            file=sys.stderr,
        )
        sys.exit(2)

    csv_path, key_columns_raw, required_columns_raw = sys.argv[1:4]
    key_columns = key_columns_raw.split(",")
    required_columns = required_columns_raw.split(",")

    df = pd.read_csv(csv_path)
    errors = []

    # Famille 1 : absence de doublons sur la clé primaire
    duplicated = df.duplicated(subset=key_columns).sum()
    if duplicated > 0:
        errors.append(
            f"{duplicated} doublon(s) trouvé(s) sur la clé {key_columns} dans {csv_path}"
        )

    # Famille 2 : absence de valeurs manquantes sur les colonnes critiques
    for col in required_columns:
        missing = df[col].isnull().sum()
        if missing > 0:
            errors.append(
                f"{missing} valeur(s) manquante(s) dans la colonne '{col}' de {csv_path}"
            )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"OK : {csv_path} - {len(df)} lignes, clé {key_columns} unique, aucune valeur manquante sur {required_columns}"
    )


if __name__ == "__main__":
    main()
