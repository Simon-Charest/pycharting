SELECT g.console_name
    , g.product_name
FROM games AS g
WHERE DATE(g.moment) != DATE('NOW', 'LOCALTIME')
AND (
    g.console_name
    , g.product_name
)
NOT IN
(
    SELECT g.console_name
        , g.product_name
    FROM games AS g
    WHERE DATE(g.moment) = DATE('NOW', 'LOCALTIME')
    GROUP BY g.console_name
        , g.product_name
)
GROUP BY g.console_name
    , g.product_name
ORDER BY g.console_name ASC
    , g.product_name ASC
;
