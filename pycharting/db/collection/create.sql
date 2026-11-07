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
    , wishlist INTEGER
    , previously_owned INTEGER
    , quantity INTEGER DEFAULT 1
    , reproduction INTEGER
    , "virtual" INTEGER
    , game
    , manual
    , box
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
    , game
    , box
    , manual
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
