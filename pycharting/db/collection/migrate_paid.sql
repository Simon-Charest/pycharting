-- Older databases kept prices in a "paid" column: a price is the one of the game
-- unless stated otherwise. Both steps apply together, or not at all.
BEGIN;

UPDATE collection_items
SET game = paid
WHERE paid IS NOT NULL
AND game IS NULL
;

ALTER TABLE collection_items DROP COLUMN paid;

COMMIT;
