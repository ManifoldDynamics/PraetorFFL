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

CREATE TABLE IF NOT EXISTS transactions_4473 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firearm_id INTEGER NOT NULL,
    transferee_name TEXT,
    transferee_address TEXT,
    transferee_city TEXT,
    transferee_state TEXT,
    transferee_zip TEXT,
    transferee_dob TEXT,
    transferee_pob TEXT,
    transferee_height TEXT,
    transferee_weight TEXT,
    transferee_sex TEXT,
    transferee_ethnicity TEXT,
    transferee_race TEXT,

    q_21a BOOLEAN, q_21b BOOLEAN, q_21c BOOLEAN, q_21d BOOLEAN,
    q_21e BOOLEAN, q_21f BOOLEAN, q_21g BOOLEAN, q_21h BOOLEAN,
    q_21i BOOLEAN, q_21j BOOLEAN, q_21k BOOLEAN, q_21l1 BOOLEAN,
    q_21l2 BOOLEAN, q_21m BOOLEAN,

    id_type TEXT,
    id_number TEXT,
    id_expiration_date TEXT,

    nics_ntn TEXT,
    nics_status TEXT, -- Proceed, Delayed, Denied, Open
    nics_date TEXT,

    transferor_name TEXT,
    transferor_title TEXT,
    transfer_date TEXT,

    buyer_signature_svg TEXT, -- Simple path data for signature
    certification_date TEXT,

    FOREIGN KEY (firearm_id) REFERENCES firearms(id)
);
