CREATE
TABLE IF NOT EXISTS owners
(
    id INTEGER PRIMARY KEY
    , name TEXT NOT NULL UNIQUE
)
;

CREATE
TABLE IF NOT EXISTS source_files
(
    id INTEGER PRIMARY KEY
    , owner_id INTEGER NOT NULL REFERENCES owners (id)
    , path TEXT NOT NULL UNIQUE
    , sha256 TEXT NOT NULL
    , content BLOB NOT NULL
)
;

CREATE
TABLE IF NOT EXISTS collection_items
(
    id INTEGER PRIMARY KEY
    , source_file_id INTEGER NOT NULL REFERENCES source_files (id)
    , position INTEGER NOT NULL
    , group_name TEXT NOT NULL
    , name TEXT NOT NULL
    , console INTEGER
    , gamepad INTEGER
    , amiibo INTEGER
    , accessory INTEGER
    , wishlist INTEGER
    , previously_owned INTEGER
    , quantity INTEGER DEFAULT 1
    , reproduction INTEGER
    , "virtual" INTEGER
    , game
    , manual
    , box
    , "date" TEXT
    , paid
    , pricecharting
    , region TEXT
    , owner_id INTEGER REFERENCES owners (id)
    , source TEXT
    , UNIQUE (source_file_id, position)
)
;

CREATE
TABLE IF NOT EXISTS spreadsheet_rows
(
    id INTEGER PRIMARY KEY
    , source_file_id INTEGER NOT NULL REFERENCES source_files (id)
    , sheet TEXT NOT NULL
    , row_index INTEGER NOT NULL
    , system
    , title
    , console
    , amiibo
    , accessory INTEGER
    , game
    , box
    , "date" TEXT
    , manual
    , paid
    , pricecharting
    , quantity INTEGER DEFAULT 1
    , gamepad INTEGER
    , previously_owned INTEGER
    , reproduction INTEGER
    , "virtual" INTEGER
    , wishlist INTEGER
    , region TEXT
    , owner_id INTEGER REFERENCES owners (id)
    , source TEXT
    , UNIQUE (source_file_id, sheet, row_index)
)
;

-- Accounts that may sign in; the password is only kept as a scrypt hash.
-- An administrator can change the collection; a collaborator can only look at it.
CREATE
TABLE IF NOT EXISTS users
(
    id INTEGER PRIMARY KEY
    , username TEXT NOT NULL UNIQUE COLLATE NOCASE
    , password_hash TEXT NOT NULL
    , role TEXT NOT NULL DEFAULT 'collaborator' CHECK (role IN ('administrator', 'collaborator'))
)
;

-- Signed-in browsers; the cookie's token is only kept as a SHA-256 hash
CREATE
TABLE IF NOT EXISTS sessions
(
    token_hash TEXT PRIMARY KEY
    , user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE
    , expires TEXT NOT NULL
)
;
