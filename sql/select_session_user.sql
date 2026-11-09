SELECT u.id
    , u.username
    , u.first_name
    , u.last_name
    , u.role
FROM sessions AS s
JOIN users AS u ON u.id = s.user_id
WHERE s.token_hash = :token_hash
AND s.expires > DATETIME('now')
;
