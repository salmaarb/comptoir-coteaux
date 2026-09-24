-- Nettoyage Web
-- Règle (méthode Octave) : suppression des valeurs manquantes puis dédoublonnage,
-- pour obtenir une clé primaire (sku) unique avant toute jointure.
--
-- Constat sur les données réelles : l'export brut contient 83 lignes entièrement
-- vides (à supprimer), puis pour chaque produit une ligne dupliquée de type
-- "attachment" portant le même sku que la ligne "product" (à supprimer, on ne
-- garde que les fiches produit).
-- Résultat attendu : 1428 lignes après suppression des lignes vides,
-- 714 lignes après dédoublonnage sur sku.

-- On filtre d'abord sur post_type = 'product' pour écarter les lignes
-- "attachment" (images) : il ne peut donc plus rester de vrai doublon de sku,
-- mais on garde le ROW_NUMBER par sécurité (défense en profondeur) si une
-- future extraction contenait deux fiches produit pour le même sku.
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