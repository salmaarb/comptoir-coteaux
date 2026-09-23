# Note de cadrage  Pipeline CA & segmentation vins premium/ordinaires

## Besoin métier
Le Comptoir des Coteaux dispose de deux systèmes qui ne communiquent pas : l'ERP (prix,
stocks) et le CMS de la boutique (ventes). Chaque mois, ce croisement était fait à la main par Octave, avec un risque d'erreur (cf. l'épisode des deux caisses). L'objectif est d'automatiser ce croisement pour produire, sans intervention humaine, le 15 de chaque mois : le chiffre d'affaires par produit et total, ainsi que les listes de vins premium et ordinaires destinées à Capucine et Théo pour leurs campagnes.

## Périmètre technique retenu
- Orchestration avec **Kestra**, qui enchaîne les tâches mais ne contient
  aucune logique métier.
- Traitements de nettoyage, jointure et agrégation en **SQL/DuckDB**.
- Segmentation premium/ordinaire par z-score en **Python/pandas**.
- Une tâche de test après chaque tâche de traitement (nettoyage, jointure, agrégation,
  extraction), afin d'éviter tout nouvel incident de type "doublon silencieux".
- Sorties : un rapport `.xlsx` (CA par produit + total) et deux extractions `.csv` (premium,
  ordinaires).
- Déclenchement automatique le 15 du mois à 9h via un trigger cron Kestra.
- Gestion des pannes : le workflow doit réagir si DuckDB (ou tout service tiers) est
  indisponible, plutôt que d'échouer silencieusement.

## Contraintes identifiées dans les sources
- Les deux systèmes utilisent des identifiants différents (`product_id` côté ERP, `sku` côté
  web) : la jointure passe obligatoirement par `fichier_liaison.xlsx`.
- `Fichier_erp.xlsx` : propre (825 lignes, aucune valeur manquante, aucun doublon).
- `fichier_liaison.xlsx` : `product_id` unique, mais **91 valeurs manquantes** et **90
  doublons** sur `id_web`, à traiter avant la jointure sous peine de fausser le résultat.
- `Fichier_web.xlsx` : export brut de type WooCommerce (1513 lignes, 28 colonnes). Contient
  83 lignes entièrement vides et, pour chaque produit, une ligne dupliquée de type
  `attachment` portant le même `sku`. Nettoyage nécessaire : suppression des lignes vides,
  puis dédoublonnage sur `sku` en ne conservant que les lignes `post_type = product`.
- Les valeurs de référence transmises par Octave (825 / 825 / 1428 / 714 / 714 lignes,
  70 568,60 € de CA total, 30 vins premium) serviront de jeu de test pour valider chaque
  étape du pipeline.

## Questions en attente
- Pour les 91 lignes de `fichier_liaison.xlsx` sans `id_web` : faut-il les exclure du
  périmètre (produits non encore en ligne) ou faut-il alerter Théo/Capucine sur ces
  produits ERP non réconciliés ?
- Pour les 90 doublons sur `id_web` : est-ce une anomalie de saisie à corriger à la source,
  ou une correspondance plusieurs-produits-ERP vers un seul produit web à assumer telle
  quelle ?
- Le seuil `z > 2` doit-il être recalculé sur l'ensemble des vins fusionnés à chaque
  exécution, ou existe-t-il un historique de prix à prendre en compte pour lisser l'effet
  d'un mois exceptionnel ?
- Quel comportement attendu exactement si DuckDB est indisponible : nouvelle tentative
  automatique (combien de fois, à quel intervalle), ou alerte immédiate sans retry ?
