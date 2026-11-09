-- Entries added from the web page have no original file: they share an empty
-- source per owner (the sha256 below is the one of empty content).
INSERT OR IGNORE
INTO source_files
(
    owner_id
    , path
    , sha256
    , content
)
SELECT o.id
    , 'added/' || o.name
    , 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    , x''
FROM owners AS o
WHERE o.id = :owner_id
;
