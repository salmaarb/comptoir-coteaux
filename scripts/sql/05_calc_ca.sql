-- Calcul du chiffre d'affaires
-- CA par bouteille = prix unitaire (ERP) x quantité vendue (total_sales, web)
-- Résultat attendu : CA total = 70 568,60 €

COPY (
    SELECT
        product_id,
        sku,
        nom_produit,
        price,
        total_sales,
        ROUND(price * total_sales, 2) AS ca_produit
    FROM read_csv_auto('data/clean/fusion.csv')
) TO 'data/clean/ca_par_produit.csv' (HEADER, DELIMITER ',');