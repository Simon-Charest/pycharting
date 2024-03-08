SELECT g.console_name
    , g.product_name
    , (
        SELECT MAX(g2.moment)
        FROM games AS g2
        WHERE g2.console_name = g.console_name
        AND g2.product_name = g.product_name
    ) AS max_moment
    , COUNT(1) AS count
FROM games AS g
GROUP BY g.console_name
    , g.product_name
ORDER BY max_moment ASC
    , count ASC
    , g.console_name ASC
    , g.product_name ASC
LIMIT ?
;
