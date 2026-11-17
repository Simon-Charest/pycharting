-- Give every item stored under one system name another one
UPDATE collection_items
SET group_name = :name
WHERE group_name = :current
;
