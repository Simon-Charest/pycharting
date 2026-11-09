UPDATE collection_items
SET group_name = :group_name
    , name = :name
    , console = :console
    , gamepad = :gamepad
    , amiibo = :amiibo
    , accessory = :accessory
    , damaged = :damaged
    , duplicate = :duplicate
    , wishlist = :wishlist
    , previously_owned = :previously_owned
    , quantity = :quantity
    , reproduction = :reproduction
    , "virtual" = :virtual
    , game = :game
    , manual = :manual
    , box = :box
    , "date" = :date
    , paid = :paid
    , pricecharting = :pricecharting
    , region = :region
    , owner_id = COALESCE(:owner_id, owner_id)
    , source = COALESCE(:source, source)
WHERE id = :id
AND (:owner_id IS NULL OR EXISTS (SELECT 1 FROM owners WHERE id = :owner_id))
;
