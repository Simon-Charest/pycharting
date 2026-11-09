UPDATE users
SET password_hash = :password_hash
WHERE username = :username
;
