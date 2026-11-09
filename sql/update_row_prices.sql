UPDATE spreadsheet_rows
SET game = :game
    , manual = :manual
    , box = :box
    , "date" = :date
    , pricecharting = :pricecharting
WHERE id = :id
;
