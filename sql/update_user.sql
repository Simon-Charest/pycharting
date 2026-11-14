-- A missing name, role or password keeps the one the account has; the names change only when given (empty clears them)
UPDATE users
SET username = COALESCE(:username, username)
    , role = COALESCE(:role, role)
    , password_hash = COALESCE(:password_hash, password_hash)
    , first_name = CASE WHEN :set_names THEN :first_name ELSE first_name END
    , last_name = CASE WHEN :set_names THEN :last_name ELSE last_name END
WHERE id = :id
;
