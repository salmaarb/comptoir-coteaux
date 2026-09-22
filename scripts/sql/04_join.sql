-- Jointure ERP ⋈ Liaison ⋈ Web
-- ERP.product_id -> Liaison.product_id -> Liaison.id_web -> Web.sku
-- Résultat attendu : 714 lignes (piloté par le fichier web, le plus restrictif
-- des trois : certains produits ERP ne sont pas encore en ligne, et le fichier
-- de liaison peut contenir des correspondances non exploitables).

COPY (
    SELECT
        e.product_id,
        w.sku,
        w.post_title AS nom_produit,
        e.price,
        e.stock_quantity,
        e.stock_status,
        w.total_sales
    FROM read_csv_auto('data/clean/erp_clean.csv') AS e
    INNER JOIN read_csv_auto('data/clean/liaison_clean.csv') AS l
        ON e.product_id = l.product_id
    INNER JOIN read_csv_auto('data/clean/web_clean.csv') AS w
        ON l.id_web = w.sku
) TO 'data/clean/fusion.csv' (HEADER, DELIMITER ',');