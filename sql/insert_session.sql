INSERT
INTO sessions
(
    token_hash
    , user_id
    , expires
)
VALUES
(
    :token_hash
    , :user_id
    , DATETIME('now', '+' || :days || ' days')
)
;
