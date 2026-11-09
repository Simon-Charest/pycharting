-- Administrators first, then by last name, first name and username
SELECT id
    , username
    , first_name
    , last_name
    , role
FROM users
ORDER BY role <> 'administrator'
    , last_name IS NULL
    , last_name COLLATE NOCASE
    , first_name COLLATE NOCASE
    , username COLLATE NOCASE
;
