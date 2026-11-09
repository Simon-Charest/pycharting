-- A missing role or password keeps the one the account has
UPDATE users
SET role = COALESCE(:role, role)
    , password_hash = COALESCE(:password_hash, password_hash)
WHERE id = :id
;
