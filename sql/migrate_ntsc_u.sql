-- NTSC becomes NTSC-U, now that NTSC-J tells the Japanese products apart. Everything
-- stored before was North American: the Japanese ones were never told apart from it.
BEGIN;

UPDATE collection_items
SET region = 'NTSC-U'
WHERE region = 'NTSC'
;

UPDATE spreadsheet_rows
SET region = 'NTSC-U'
WHERE region = 'NTSC'
;

COMMIT;
