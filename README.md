# Comptoir des Coteaux : Pipeline CA & segmentation vins

## Contexte
Le Comptoir des Coteaux dispose de deux systèmes qui ne communiquent pas : l'ERP (prix,stocks) et le CMS de la boutique en ligne (ventes). Chaque mois, Octave croisait ces données à la main dans un notebook pour produire le chiffre d'affaires et la liste des vins premium.
Ce dépôt automatise ce croisement avec **Kestra**, qui orchestre des scripts **SQL (DuckDB)** pour le nettoyage/la jointure/l'agrégation et **Python (pandas)** pour la segmentation statistique (z-score), avec une tâche de test après chaque tâche de traitement.

## Prérequis
- Docker et Docker Compose (pour faire tourner Kestra)
- Python 3.11+ avec `pandas`, `openpyxl`, `duckdb` (pour le pipeline lui-même et pour tester en local sans Kestra) : voir `requirements.txt`

## Lancer le pipeline

### Option A : via Kestra (orchestration complète, comme en production)
1. `docker compose up -d` : lance Kestra (interface sur http://localhost:8080) et son métastore Postgres.
2. Créez votre compte admin au premier lancement.
3. Créez un flow dans le namespace `comptoir.coteaux`, collez-y le contenu de
   `flows/pipeline_comptoir.yaml`.
4. Dans l'onglet **Files** du flow, importez (glisser-déposer) les dossiers `data/` et `scripts/` de ce dépôt : le flow lit ces fichiers via `namespaceFiles`.
5. Cliquez sur **Execute** pour un lancement manuel, ou attendez le trigger cron programmé le 15 du mois à 9h (`0 9 15 * *`).
6. Les résultats (`rapport_ca.xlsx`, `vins_premium.csv`, `vins_ordinaires.csv`) sont  récupérables dans l'onglet **Outputs** de l'exécution.

### Option B : en local, sans Kestra (pour tester/déboguer rapidement)
```bash
pip install -r requirements.txt
python run_all_local.py
```
Ce script enchaîne les 14 étapes du pipeline (conversion, nettoyage, tests, jointure, calcul du CA, z-score, rapport) dans l'ordre, et s'arrête au premier échec en indiquant l'étape en cause.

## Résultats obtenus face aux valeurs de référence d'Octave
Toutes les valeurs ci-dessous ont été vérifiées, en local et dans Kestra, contre les chiffres transmis par Octave sur ce jeu de données précis.

| Étape | Valeur attendue (Octave) | Valeur obtenue |
|---|---|---|
| ERP après dédoublonnage | 825 | **825** |
| Web après nettoyage (lignes vides supprimées) | 1 428 | **1 428**|
| Web après dédoublonnage | 714 | **714** |
| Fichier fusionné | 714 | **714** |
| Chiffre d'affaires total | 70 568,60 € | **70 568,60 €** 
|
| Vins premium détectés (z > 2) | 30 | **30**  |


## Tests
5 familles de tests, dans `scripts/tests/`, intégrées au flow après chaque tâche nominale
correspondante :
- absence de doublons et de valeurs manquantes (après chaque nettoyage ERP/Liaison/Web)
- cohérence de la jointure
- cohérence du chiffre d'affaires
- cohérence du z-score et de la segmentation premium/ordinaire

Chaque test échoue explicitement (code de sortie non nul, message clair) si un résultats'écarte des valeurs de référence ou d'une règle de cohérence interne, ce qui fait échouer la tâche Kestra correspondante.

## Gestion des erreurs
Les tâches sensibles (accès à DuckDB, installation de dépendances) ont un `retry` configuré (3 tentatives, intervalle de 30s) dans `flows/pipeline_comptoir.yaml`, pour absorber les pannes
transitoires (ex. service indisponible, téléchargement réseau interrompu) sans faire échouer tout le pipeline au premier accroc.

## Suivi de projet
Backlog et Kanban 

## Logigramme
Voir `docs/logigramme.drawio` (éditable sur [app.diagrams.net](https://app.diagrams.net)) et son export `docs/logigramme.png`. Il détaille l'enchaînement nettoyage → jointure → calcul CA → z-score → extractions, avec une tâche de test après chaque tâche de traitement.

## Arborescence
- `docs/` : note de cadrage, logigramme, captures d'écran Kestra
- `flows/` : le workflow Kestra (`.yaml`)
- `scripts/sql/` : nettoyage, jointure, agrégation (DuckDB)
- `scripts/python/` : conversion xlsx→csv, z-score, génération du rapport
- `scripts/tests/` : les 5 familles de tests
- `data/` : les 3 exports sources
- `outputs/` : rapport CA, listes premium/ordinaires (générés par le pipeline)
- `soutenance/` : support de présentation
- `run_all_local.py` : lance tout le pipeline en local, hors Kestra, pour tester/déboguer
- `docker-compose.yml` : Kestra  + Postgres