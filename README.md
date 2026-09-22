# Comptoir des Coteaux — Pipeline CA & segmentation vins

## Contexte
Automatisation, avec Kestra, du croisement mensuel entre l'ERP et le CMS de la boutique en
ligne du Comptoir des Coteaux, pour produire le rapport de chiffre d'affaires et les listes de
vins premium / ordinaires, jusque-là construits à la main par Octave.

## Prérequis
- Docker et Docker Compose
- (à compléter au fur et à mesure : version de Kestra, Python, dépendances)

## Lancer le pipeline
_À compléter à l'étape 2 (installation de Kestra, scripts SQL/Python)._

## Résultats obtenus face aux valeurs de référence d'Octave
| Étape | Valeur attendue (Octave) | Valeur obtenue |
|---|---|---|
| ERP après dédoublonnage | 825 | à compléter |
| Liaison après dédoublonnage | 825 | à compléter |
| Web après nettoyage | 1 428 | à compléter |
| Web après dédoublonnage | 714 | à compléter |
| Fichier fusionné | 714 | à compléter |
| Chiffre d'affaires total | 70 568,60 € | à compléter |
| Vins premium détectés (z > 2) | 30 | à compléter |

## Suivi de projet
Lien OpenProject : _à compléter_

## Arborescence
- `docs/` — note de cadrage, logigramme, captures d'écran Kestra
- `flows/` — le workflow Kestra (`.yaml`)
- `scripts/` — scripts SQL (DuckDB) et Python versionnés séparément du YAML
- `data/` — les 3 exports sources
- `outputs/` — rapport CA, listes premium/ordinaires
- `soutenance/` — support de présentation
