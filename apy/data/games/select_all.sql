SELECT g.*
FROM games AS g
WHERE DATE(g.moment) = DATE('NOW')
GROUP BY g.console_name
    , g.id
    , g.product_name
    , g.loose_price
HAVING g.moment = MAX(g.moment)
;
