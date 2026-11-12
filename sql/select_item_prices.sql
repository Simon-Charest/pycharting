SELECT name AS title
    , group_name AS console
    , region
    , game
    , manual
    , box
    , complete
    , pricecharting
FROM collection_items
WHERE id = :id
;
