-- Nettoyage ERP
-- Règle (méthode Octave) : suppression des valeurs manquantes puis dédoublonnage,
-- pour obtenir une clé primaire (product_id) unique avant toute jointure.
-- Résultat attendu : 825 lignes (fichier déjà propre, aucune valeur retirée).

COPY (
    SELECT * EXCLUDE (rn)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_id) AS rn
        FROM read_csv_auto('data/staging/erp_raw.csv')
        WHERE product_id IS NOT NULL
          AND onsale_web IS NOT NULL
          AND price IS NOT NULL
          AND stock_quantity IS NOT NULL
          AND stock_status IS NOT NULL
    )
    WHERE rn = 1
) TO 'data/clean/erp_clean.csv' (HEADER, DELIMITER ',');