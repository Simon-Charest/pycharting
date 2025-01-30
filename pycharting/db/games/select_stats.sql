SELECT g1.console_name
    , COUNT(1) AS count
    , ROUND(MIN(g1.loose_price), 2) AS min
    , ROUND(AVG(g1.loose_price), 2) AS avg
    , ROUND(MAX(g1.loose_price), 2) AS max
    , ROUND(SUM(g1.loose_price), 2) AS sum
FROM games AS g1
JOIN
(
    SELECT console_name
        , product_name
        , MAX(moment) AS max_moment
    FROM games
    GROUP BY console_name
        , product_name
) AS g2 ON g1.console_name = g2.console_name 
    AND g1.product_name = g2.product_name 
    AND g1.moment = g2.max_moment
GROUP BY g1.console_name
ORDER BY sum DESC
    , g1.console_name ASC
;
