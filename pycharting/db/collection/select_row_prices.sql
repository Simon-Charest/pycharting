SELECT title
    , system AS console
    , region
    , game
    , manual
    , box
    , pricecharting
FROM spreadsheet_rows
WHERE id = :id
;
