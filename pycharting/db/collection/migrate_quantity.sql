-- Every entry has a quantity: 1 unless stated otherwise. Both steps apply together, or not at all.
BEGIN;

ALTER TABLE spreadsheet_rows ADD COLUMN quantity INTEGER DEFAULT 1;

UPDATE collection_items
SET quantity = 1
WHERE quantity IS NULL
;

COMMIT;
