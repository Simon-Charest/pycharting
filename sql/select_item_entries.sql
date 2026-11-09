SELECT i.id
    , o.name AS owner
    , o.id AS owner_id
    , COALESCE(i.source, f.path) AS source
    , i.group_name
    , i.name
    , i.region
    , i.console
    , i.gamepad
    , i.amiibo
    , i.accessory
    , i.damaged
    , i.selling
    , i.wishlist
    , i.previously_owned
    , i.quantity
    , i.reproduction
    , i."virtual"
    , i.game
    , i.manual
    , i.box
    , i."date"
    , i.paid
    , i.pricecharting
FROM collection_items AS i
JOIN source_files AS f ON f.id = i.source_file_id
JOIN owners AS o ON o.id = COALESCE(i.owner_id, f.owner_id)
;
