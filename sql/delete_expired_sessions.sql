DELETE
FROM sessions
WHERE expires <= DATETIME('now')
;
