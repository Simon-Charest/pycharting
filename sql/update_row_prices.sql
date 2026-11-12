UPDATE spreadsheet_rows
SET game = :game
    , manual = :manual
    , box = :box
    , complete = :complete
    , "date" = :date
    , pricecharting = :pricecharting
WHERE id = :id
;
