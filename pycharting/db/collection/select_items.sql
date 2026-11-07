SELECT CASE WHEN i.region = 'PAL' THEN 'PAL ' || i.group_name ELSE i.group_name END AS group_name
    , i.name
    , i.console
    , i.gamepad
    , i.previously_owned
    , i.reproduction
    , i."virtual"
FROM collection_items AS i
ORDER BY i.source_file_id ASC
    , i.position ASC
;
