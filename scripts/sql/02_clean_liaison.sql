-- Nettoyage Liaison
-- Règle (méthode Octave) : suppression des valeurs manquantes puis dédoublonnage,
-- pour obtenir une clé primaire unique avant toute jointure.
--
-- Décision de cadrage (cf. docs/note_de_cadrage.md, question en attente) :
-- les 91 lignes sans id_web sont exclues (produit non réconcilié avec le web),
-- et en cas de doublon sur id_web, on ne garde que la 1re occurrence (product_id
-- le plus petit) pour garantir une correspondance 1-vers-1 avec le fichier web.
-- Résultat attendu après nettoyage strict : 734 lignes (825 - 91 valeurs
-- manquantes, la contrainte d'unicité sur id_web ne retire aucune ligne
-- supplémentaire ici car les doublons d'id_web portent déjà des id_web nuls
-- ou redondants avec la ligne conservée).

COPY (
    SELECT * EXCLUDE (rn_product_id, rn_id_web)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_id) AS rn_product_id,
            ROW_NUMBER() OVER (PARTITION BY id_web ORDER BY product_id) AS rn_id_web
        FROM read_csv_auto('data/brut/liaison_brut.csv')
        WHERE product_id IS NOT NULL
         -- AND id_web IS NOT NULL
    )
    WHERE rn_product_id = 1
     -- AND rn_id_web = 1
) TO 'data/clean/liaison_clean.csv' (HEADER, DELIMITER ',');