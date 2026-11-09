SELECT u.username
    , u.role
FROM sessions AS s
JOIN users AS u ON u.id = s.user_id
WHERE s.token_hash = :token_hash
AND s.expires > DATETIME('now')
;
