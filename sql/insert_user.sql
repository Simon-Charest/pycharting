INSERT
INTO users
(
    username
    , password_hash
    , first_name
    , last_name
    , role
)
VALUES
(
    :username
    , :password_hash
    , :first_name
    , :last_name
    , :role
)
ON CONFLICT (username) DO NOTHING
;
