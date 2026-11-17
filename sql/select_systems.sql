-- Every system name the collection uses, with how many items and spreadsheet rows carry it.
-- Two names that differ only in case stay apart: each entry keeps the name it was stored with,
-- and renaming one of them is what brings them together.
SELECT name
    , SUM(items) AS items
    , SUM("rows") AS "rows"
FROM (
    SELECT group_name AS name
        , COUNT(1) AS items
        , 0 AS "rows"
    FROM collection_items
    GROUP BY group_name

    UNION ALL

    SELECT system AS name
        , 0 AS items
        , COUNT(1) AS "rows"
    FROM spreadsheet_rows
    GROUP BY system
)
WHERE name IS NOT NULL
    AND TRIM(name) <> ''
GROUP BY name
ORDER BY name COLLATE NOCASE ASC
    , name ASC
;
