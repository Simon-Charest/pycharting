SELECT g.console_name
    , g.id
    , g.product_name
    , g.loose_price
FROM games AS g
WHERE DATE(g.moment) = DATE('NOW', 'LOCALTIME')
GROUP BY g.console_name
    , g.id
    , g.product_name
    , g.loose_price
HAVING g.moment = MAX(g.moment)
ORDER BY g.loose_price DESC
LIMIT ?
;
