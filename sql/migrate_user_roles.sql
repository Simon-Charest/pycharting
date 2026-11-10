-- Rebuild the users table so that its roles include 'buyer'; accounts and their ids stay the same.
CREATE
TABLE users_with_roles
(
    id INTEGER PRIMARY KEY
    , username TEXT NOT NULL UNIQUE COLLATE NOCASE
    , password_hash TEXT NOT NULL
    , first_name TEXT
    , last_name TEXT
    , role TEXT NOT NULL DEFAULT 'collaborator' CHECK (role IN ('administrator', 'collaborator', 'buyer'))
)
;

INSERT
INTO users_with_roles (id, username, password_hash, first_name, last_name, role)
SELECT id, username, password_hash, first_name, last_name, role
FROM users
;

DROP
TABLE users
;

ALTER
TABLE users_with_roles
RENAME TO users
;
