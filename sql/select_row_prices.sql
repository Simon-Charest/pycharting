SELECT title
    , system AS console
    , region
    , game
    , manual
    , box
    , complete
    , pricecharting
FROM spreadsheet_rows
WHERE id = :id
;
