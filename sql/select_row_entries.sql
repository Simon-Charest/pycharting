SELECT r.id
    , o.name AS owner
    , o.id AS owner_id
    , COALESCE(r.source, f.path || ' (' || r.sheet || ')') AS source
    , r.system
    , r.title
    , r.region
    , r.console
    , r.amiibo
    , r.accessory
    , r.damaged
    , r.duplicate
    , r.game
    , r.box
    , r.manual
    , r."date"
    , r.paid
    , r.pricecharting
    , r.quantity
    , r.gamepad
    , r.previously_owned
    , r.reproduction
    , r."virtual"
    , r.wishlist
FROM spreadsheet_rows AS r
JOIN source_files AS f ON f.id = r.source_file_id
JOIN owners AS o ON o.id = COALESCE(r.owner_id, f.owner_id)
;
