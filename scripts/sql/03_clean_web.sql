-- Nettoyage Web
-- Règle (méthode Octave) : suppression des valeurs manquantes puis dédoublonnage,
-- pour obtenir une clé primaire (sku) unique avant toute jointure.

COPY (
    SELECT * EXCLUDE (rn)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY sku ORDER BY sku) AS rn
        FROM read_csv_auto('data/brut/web_brut.csv')
        WHERE sku IS NOT NULL
          AND post_type = 'product'
    )
    WHERE rn = 1
) TO 'data/clean/web_clean.csv' (HEADER, DELIMITER ',');