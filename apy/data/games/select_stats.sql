SELECT q.console_name
    , q.count
    , ROUND(q.min, 2) AS min
    , ROUND(q.avg, 2) AS avg
    , ROUND(q.max, 2) AS max
    , ROUND(q.sum, 2) AS sum
FROM
(
    SELECT g1.console_name
        , COUNT(g1.loose_price) AS count
        , MIN(g1.loose_price) AS min
        , AVG(g1.loose_price) AS avg
        , MAX(g1.loose_price) AS max
        , SUM(g1.loose_price) AS sum
    FROM games AS g1
    JOIN
    (
        SELECT g2.console_name
            , g2.product_name
            , MAX(g2.moment) AS max_moment
        FROM games AS g2
        GROUP BY g2.console_name
            , g2.product_name
    ) AS g3 ON g1.console_name = g3.console_name 
        AND g1.product_name = g3.product_name 
        AND g1.moment = g3.max_moment
    GROUP BY g1.console_name
    UNION ALL
    SELECT 'Total'
        , COUNT(g4.loose_price) AS count
        , MIN(g4.loose_price) AS min
        , AVG(g4.loose_price) AS avg
        , MAX(g4.loose_price) AS max
        , SUM(g4.loose_price) AS sum
    FROM games AS g4
) AS q
ORDER BY CASE WHEN  q.console_name = 'Total' THEN 1 ELSE 0 END ASC
    , q.sum DESC
    , q.console_name ASC
;
