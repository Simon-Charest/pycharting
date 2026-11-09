INSERT
INTO users
(
    username
    , password_hash
    , role
)
VALUES
(
    :username
    , :password_hash
    , :role
)
ON CONFLICT (username) DO NOTHING
;
