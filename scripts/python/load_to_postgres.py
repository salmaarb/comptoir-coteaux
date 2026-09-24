"""
Chargement des résultats du pipeline dans PostgreSQL (Neon)  architecture hybride.
Usage : python load_postgres.py
Entrées : data/clean/ca_par_produit.csv, outputs/vins_premium.csv, outputs/vins_ordinaires.csv
"""

import os
import sys
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]


BASE_COLUMNS = {
    "product_id": "BIGINT",
    "sku": "VARCHAR",
    "nom_produit": "VARCHAR",
    "price": "DOUBLE",
    "total_sales": "BIGINT",
    "ca_produit": "DOUBLE",
}
ZSCORE_COLUMNS = {**BASE_COLUMNS, "z_score": "DOUBLE"}

TABLES = {
    "ca_par_produit": {
        "csv": ROOT / "data" / "clean" / "ca_par_produit.csv",
        "columns": BASE_COLUMNS,
    },
    "vins_premium": {
        "csv": ROOT / "outputs" / "vins_premium.csv",
        "columns": ZSCORE_COLUMNS,
    },
    "vins_ordinaires": {
        "csv": ROOT / "outputs" / "vins_ordinaires.csv",
        "columns": ZSCORE_COLUMNS,
    },
}


def schema_clause(columns: dict) -> str:
    return ", ".join(f"{name} {dtype}" for name, dtype in columns.items())


def read_csv_columns_clause(columns: dict) -> str:
    pairs = ", ".join(f"'{name}': '{dtype}'" for name, dtype in columns.items())
    return "{" + pairs + "}"


def get_connection_string() -> str:
    conn = os.environ.get("NEON_CONNECTION_STRING")
    if not conn:
        print(
            "ERREUR : variable d'environnement NEON_CONNECTION_STRING absente.",
            file=sys.stderr,
        )
        sys.exit(1)
    return conn


def main() -> None:
    conn_str = get_connection_string()

    for name, cfg in TABLES.items():
        if not cfg["csv"].exists():
            print(f"ERREUR : fichier introuvable : {cfg['csv']}", file=sys.stderr)
            sys.exit(1)

    con = duckdb.connect()
    try:
        con.execute("INSTALL postgres;")
        con.execute("LOAD postgres;")
        con.execute(f"ATTACH '{conn_str}' AS neon (TYPE POSTGRES);")
    except Exception:
        print(
            "ERREUR : connexion à PostgreSQL (Neon) impossible. "
            "Vérifiez la disponibilité de la base et sslmode=require.",
            file=sys.stderr,
        )
        sys.exit(1)

    for name, cfg in TABLES.items():
        schema = schema_clause(cfg["columns"])
        types_clause = read_csv_columns_clause(cfg["columns"])
        con.execute(f"CREATE OR REPLACE TABLE neon.{name} ({schema});")
        con.execute(
            f"INSERT INTO neon.{name} "
            f"SELECT * FROM read_csv('{cfg['csv']}', columns={types_clause}, header=true);"
        )
        print(f"OK : table '{name}' rechargée dans PostgreSQL (Neon).")

    print("Chargement PostgreSQL terminé avec succès.")


if __name__ == "__main__":
    main()
