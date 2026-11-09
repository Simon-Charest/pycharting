-- Region, owner and source become editable on each entry. The region used to be a
-- "PAL " prefix on the console name. All of this applies together, or not at all.
BEGIN;

ALTER TABLE collection_items ADD COLUMN region TEXT;
ALTER TABLE collection_items ADD COLUMN owner_id INTEGER REFERENCES owners (id);
ALTER TABLE collection_items ADD COLUMN source TEXT;
ALTER TABLE spreadsheet_rows ADD COLUMN region TEXT;
ALTER TABLE spreadsheet_rows ADD COLUMN owner_id INTEGER REFERENCES owners (id);
ALTER TABLE spreadsheet_rows ADD COLUMN source TEXT;

UPDATE collection_items
SET region = CASE
        WHEN group_name LIKE 'PAL %' THEN 'PAL'
        WHEN group_name IN ('Arcade', 'Mini Arcade', 'Nintendo Power', 'PC') THEN NULL
        ELSE 'NTSC'
    END
    , group_name = CASE WHEN group_name LIKE 'PAL %' THEN SUBSTR(group_name, 5) ELSE group_name END
;

UPDATE spreadsheet_rows
SET region = CASE
        WHEN system LIKE 'PAL %' THEN 'PAL'
        WHEN system IN ('Arcade', 'Mini Arcade', 'Nintendo Power', 'PC') THEN NULL
        ELSE 'NTSC'
    END
    , system = CASE WHEN system LIKE 'PAL %' THEN SUBSTR(system, 5) ELSE system END
;

COMMIT;
