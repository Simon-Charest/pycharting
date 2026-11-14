-- Rebuild the users table without the 'buyer' role, which the open collection page replaced: anyone can see
-- what is for sale without an account. Any buyer left becomes a collaborator. Accounts and their ids stay the
-- same, so the sessions that point at them stay valid.
CREATE
TABLE users_with_roles
(
    id INTEGER PRIMARY KEY
    , username TEXT NOT NULL UNIQUE COLLATE NOCASE
    , password_hash TEXT NOT NULL
    , first_name TEXT
    , last_name TEXT
    , role TEXT NOT NULL DEFAULT 'collaborator' CHECK (role IN ('administrator', 'collaborator'))
)
;

INSERT
INTO users_with_roles (id, username, password_hash, first_name, last_name, role)
SELECT id
    , username
    , password_hash
    , first_name
    , last_name
    , CASE WHEN role = 'buyer' THEN 'collaborator' ELSE role END
FROM users
;

DROP
TABLE users
;

ALTER
TABLE users_with_roles
RENAME TO users
;
