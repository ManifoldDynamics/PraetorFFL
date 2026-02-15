CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address_street TEXT,
    address_city TEXT,
    address_state TEXT,
    address_zip TEXT,
    license_number TEXT,
    phone TEXT,
    email TEXT,
    is_ffl BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS firearms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    type TEXT NOT NULL,
    caliber TEXT NOT NULL,
    importer TEXT,
    condition TEXT,
    upc TEXT,

    acquisition_date TEXT NOT NULL,
    source_contact_id INTEGER,

    disposition_date TEXT,
    disposition_contact_id INTEGER,

    FOREIGN KEY (source_contact_id) REFERENCES contacts(id),
    FOREIGN KEY (disposition_contact_id) REFERENCES contacts(id)
);
