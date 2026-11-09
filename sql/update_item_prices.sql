UPDATE collection_items
SET game = :game
    , manual = :manual
    , box = :box
    , "date" = :date
    , pricecharting = :pricecharting
WHERE id = :id
;
