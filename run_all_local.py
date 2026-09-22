"""
Lance tout le pipeline localement, dans l'ordre, sans passer par Kestra.
Pratique pour tester/déboguer avant de pousser vers l'orchestrateur.

Usage : python run_all_local.py
À exécuter depuis la racine du dépôt (comptoir-coteaux/).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = (
    sys.executable
)  # même interpréteur que celui qui lance ce script (évite tout conflit pyenv/venv)

STEPS = [
    ("Conversion xlsx -> csv", [PY, "scripts/python/00_convert_xlsx_to_csv.py"]),
    (
        "Nettoyage ERP",
        [
            PY,
            "-c",
            "import duckdb; duckdb.connect().execute(open('scripts/sql/01_clean_erp.sql').read())",
        ],
    ),
    (
        "Test ERP",
        [
            PY,
            "scripts/tests/test_clean_file.py",
            "data/clean/erp_clean.csv",
            "product_id",
            "product_id,price,stock_quantity,stock_status,onsale_web",
        ],
    ),
    (
        "Nettoyage Liaison",
        [
            PY,
            "-c",
            "import duckdb; duckdb.connect().execute(open('scripts/sql/02_clean_liaison.sql').read())",
        ],
    ),
    (
        "Test Liaison",
        [
            PY,
            "scripts/tests/test_clean_file.py",
            "data/clean/liaison_clean.csv",
            "product_id,id_web",
            "product_id,id_web",
        ],
    ),
    (
        "Nettoyage Web",
        [
            PY,
            "-c",
            "import duckdb; duckdb.connect().execute(open('scripts/sql/03_clean_web.sql').read())",
        ],
    ),
    (
        "Test Web",
        [
            PY,
            "scripts/tests/test_clean_file.py",
            "data/clean/web_clean.csv",
            "sku",
            "sku,total_sales",
        ],
    ),
    (
        "Jointure",
        [
            PY,
            "-c",
            "import duckdb; duckdb.connect().execute(open('scripts/sql/04_join.sql').read())",
        ],
    ),
    ("Test Jointure", [PY, "scripts/tests/test_join_consistency.py"]),
    (
        "Calcul CA",
        [
            PY,
            "-c",
            "import duckdb; duckdb.connect().execute(open('scripts/sql/05_calc_ca.sql').read())",
        ],
    ),
    ("Test CA", [PY, "scripts/tests/test_ca_consistency.py"]),
    ("Z-score / segmentation", [PY, "scripts/python/06_zscore_segmentation.py"]),
    ("Test Z-score", [PY, "scripts/tests/test_zscore.py"]),
    ("Génération rapport Excel", [PY, "scripts/python/07_generate_report.py"]),
]


def main() -> None:
    for label, cmd in STEPS:
        print(f"\n=== {label} ===")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            print(f"\nÉCHEC à l'étape : {label}", file=sys.stderr)
            sys.exit(result.returncode)
    print(
        "\nPipeline complet exécuté avec succès (nettoyage, tests, CA, z-score, rapport)."
    )


if __name__ == "__main__":
    main()
