INSERT
INTO collection_items
(
    source_file_id
    , position
    , group_name
    , name
    , console
    , gamepad
    , amiibo
    , accessory
    , damaged
    , wishlist
    , previously_owned
    , quantity
    , reproduction
    , "virtual"
    , game
    , manual
    , box
    , "date"
    , paid
    , pricecharting
    , region
    , source
)
SELECT f.id
    , COALESCE((SELECT MAX(i.position) + 1 FROM collection_items AS i WHERE i.source_file_id = f.id), 0)
    , :group_name
    , :name
    , :console
    , :gamepad
    , :amiibo
    , :accessory
    , :damaged
    , :wishlist
    , :previously_owned
    , :quantity
    , :reproduction
    , :virtual
    , :game
    , :manual
    , :box
    , :date
    , :paid
    , :pricecharting
    , :region
    , :source
FROM source_files AS f
JOIN owners AS o ON o.id = f.owner_id
WHERE o.id = :owner_id
AND f.path = 'added/' || o.name
;
