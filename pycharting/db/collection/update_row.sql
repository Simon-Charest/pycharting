UPDATE spreadsheet_rows
SET system = :system
    , title = :title
    , console = :console
    , amiibo = :amiibo
    , game = :game
    , box = :box
    , manual = :manual
    , pricecharting = :pricecharting
    , quantity = :quantity
    , gamepad = :gamepad
    , previously_owned = :previously_owned
    , reproduction = :reproduction
    , "virtual" = :virtual
    , wishlist = :wishlist
    , region = :region
    , owner_id = COALESCE(:owner_id, owner_id)
    , source = COALESCE(:source, source)
WHERE id = :id
AND (:owner_id IS NULL OR EXISTS (SELECT 1 FROM owners WHERE id = :owner_id))
;
