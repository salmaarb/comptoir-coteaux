"""
Lance tout le pipeline localement, dans l'ordre, sans passer par Kestra.
Pratique pour tester/déboguer avant de pousser vers l'orchestrateur.

Usage : python run_all_local.py
À exécuter depuis la racine du dépôt (comptoir-coteaux/).
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = (
    sys.executable
)  # même interpréteur que celui qui lance ce script (évite tout conflit pyenv/venv)

# Couleurs ANSI (fonctionnent dans PowerShell moderne, VS Code, et la
# plupart des terminaux ; sans effet si le terminal ne les supporte pas).
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

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
            "product_id",
            "product_id",
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
    total = len(STEPS)
    history = []  # (label, ok: bool, duration: float)
    pipeline_start = time.time()

    print(f"\n{BOLD}Pipeline Comptoir des Coteaux — {total} étapes{RESET}\n")

    for i, (label, cmd) in enumerate(STEPS, start=1):
        prefix = f"[{i}/{total}]"
        print(f"{DIM}{prefix}{RESET} {BOLD}{label}{RESET} ...", end=" ", flush=True)

        step_start = time.time()
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        duration = time.time() - step_start

        if result.returncode == 0:
            print(f"{GREEN}OK{RESET} {DIM}({duration:.1f}s){RESET}")
            if result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    print(f"      {DIM}{line}{RESET}")
            history.append((label, True, duration))
        else:
            print(f"{RED}ÉCHEC{RESET} {DIM}({duration:.1f}s){RESET}")
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print(f"{RED}{result.stderr.strip()}{RESET}")
            history.append((label, False, duration))
            print_summary(history, time.time() - pipeline_start, success=False)
            sys.exit(result.returncode)

    print_summary(history, time.time() - pipeline_start, success=True)


def print_summary(history, total_duration, success: bool) -> None:
    print(f"\n{BOLD}{'─' * 50}{RESET}")
    print(f"{BOLD}Résumé{RESET}")
    for label, ok, duration in history:
        mark = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"  {mark} {label:<40} {DIM}{duration:.1f}s{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}")

    if success:
        print(
            f"{GREEN}{BOLD}Pipeline complet exécuté avec succès (nettoyage, tests, CA, z-score, rapport){RESET} "
            f"{DIM}({total_duration:.1f}s au total){RESET}\n"
        )
    else:
        print(
            f"{RED}{BOLD}Pipeline interrompu au premier échec{RESET} "
            f"{DIM}({total_duration:.1f}s avant l'arrêt){RESET}\n"
        )


if __name__ == "__main__":
    main()
