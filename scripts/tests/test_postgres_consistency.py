"""
Test de cohérence entre PostgreSQL (Neon) et les fichiers locaux.

Vérifie que les 3 tables chargées dans Neon contiennent exactement les mêmes
données que les fichiers .csv produits par le pipeline : mêmes nombres de
lignes, même chiffre d'affaires total, même nombre de vins premium.

Comme le chargement Postgres est volontairement tolérant aux pannes
(allowFailure: true côté Kestra), ce test peut lui aussi échouer sans
bloquer la livraison des fichiers à Capucine et Théo : il sert d'alerte de
cohérence, pas de verrou sur le pipeline.


"""

import os
import sys
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]
CA_CSV = ROOT / "data" / "clean" / "ca_par_produit.csv"
PREMIUM_CSV = ROOT / "outputs" / "vins_premium.csv"
ORDINAIRE_CSV = ROOT / "outputs" / "vins_ordinaires.csv"

CA_TOTAL_REF = 70568.60
PREMIUM_COUNT_REF = 30
TOLERANCE = 0.01

BASE_COLUMNS = "{'product_id': 'BIGINT', 'sku': 'VARCHAR', 'nom_produit': 'VARCHAR', 'price': 'DOUBLE', 'total_sales': 'BIGINT', 'ca_produit': 'DOUBLE'}"
ZSCORE_COLUMNS = "{'product_id': 'BIGINT', 'sku': 'VARCHAR', 'nom_produit': 'VARCHAR', 'price': 'DOUBLE', 'total_sales': 'BIGINT', 'ca_produit': 'DOUBLE', 'z_score': 'DOUBLE'}"


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
    con = duckdb.connect()
    try:
        con.execute("INSTALL postgres;")
        con.execute("LOAD postgres;")
        con.execute(f"ATTACH '{conn_str}' AS neon (TYPE POSTGRES);")
    except Exception:
        print(
            "ERREUR : connexion à PostgreSQL (Neon) impossible pour le test de cohérence.",
            file=sys.stderr,
        )
        sys.exit(1)

    errors = []

    local_ca = con.execute(
        f"SELECT COUNT(*) FROM read_csv('{CA_CSV}', columns={BASE_COLUMNS}, header=true)"
    ).fetchone()[0]
    remote_ca = con.execute("SELECT COUNT(*) FROM neon.ca_par_produit").fetchone()[0]
    if local_ca != remote_ca:
        errors.append(
            f"ca_par_produit : {local_ca} lignes en local vs {remote_ca} dans Neon"
        )

    remote_total = con.execute(
        "SELECT ROUND(SUM(ca_produit), 2) FROM neon.ca_par_produit"
    ).fetchone()[0]
    if remote_total is None or abs(remote_total - CA_TOTAL_REF) > TOLERANCE:
        errors.append(
            f"CA total dans Neon = {remote_total} €, attendu {CA_TOTAL_REF} €"
        )

    local_premium = con.execute(
        f"SELECT COUNT(*) FROM read_csv('{PREMIUM_CSV}', columns={ZSCORE_COLUMNS}, header=true)"
    ).fetchone()[0]
    remote_premium = con.execute("SELECT COUNT(*) FROM neon.vins_premium").fetchone()[0]
    if local_premium != remote_premium or remote_premium != PREMIUM_COUNT_REF:
        errors.append(
            f"vins_premium : {local_premium} lignes en local, {remote_premium} dans Neon, "
            f"attendu {PREMIUM_COUNT_REF}"
        )

    local_ordinaire = con.execute(
        f"SELECT COUNT(*) FROM read_csv('{ORDINAIRE_CSV}', columns={ZSCORE_COLUMNS}, header=true)"
    ).fetchone()[0]
    remote_ordinaire = con.execute(
        "SELECT COUNT(*) FROM neon.vins_ordinaires"
    ).fetchone()[0]
    if local_ordinaire != remote_ordinaire:
        errors.append(
            f"vins_ordinaires : {local_ordinaire} lignes en local vs {remote_ordinaire} dans Neon"
        )

    if errors:
        for e in errors:
            print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"OK : PostgreSQL cohérent avec les fichiers locaux "
        f"({remote_ca} lignes CA, CA total {remote_total} €, {remote_premium} vins premium)."
    )


if __name__ == "__main__":
    main()
