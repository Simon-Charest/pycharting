-- The same, for the spreadsheet rows
UPDATE spreadsheet_rows
SET system = :name
WHERE system = :current
;
