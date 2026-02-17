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
    is_ffl BOOLEAN DEFAULT 0,
    ccw_path TEXT,
    notes TEXT
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

CREATE TABLE IF NOT EXISTS nfa_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL, -- Individual, Trust, Corporation
    name TEXT NOT NULL,
    address_street TEXT,
    address_city TEXT,
    address_state TEXT,
    address_zip TEXT,
    phone TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS responsible_persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    title TEXT, -- Trustee, Beneficiary, etc.
    dob TEXT,
    pob_city TEXT,
    pob_state TEXT,
    pob_country TEXT,
    ssn TEXT, -- Stored plain text locally for MVP
    upin TEXT,
    photo_path TEXT, -- Path to local photo file
    fingerprint_path TEXT, -- Path to local fingerprint file (EFT/Card)

    FOREIGN KEY (entity_id) REFERENCES nfa_entities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nfa_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_type TEXT NOT NULL, -- Form 1, Form 4
    status TEXT DEFAULT 'Draft', -- Draft, Pending, Approved, Denied
    submitted_date TEXT,
    approved_date TEXT,
    control_number TEXT,

    transferee_entity_id INTEGER,
    firearm_id INTEGER,

    cleo_name TEXT,
    cleo_title TEXT,
    cleo_agency TEXT,
    cleo_address_street TEXT,
    cleo_address_city TEXT,
    cleo_address_state TEXT,
    cleo_address_zip TEXT,

    FOREIGN KEY (transferee_entity_id) REFERENCES nfa_entities(id),
    FOREIGN KEY (firearm_id) REFERENCES firearms(id)
);

-- Gunsmithing
CREATE TABLE IF NOT EXISTS gunsmith_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    firearm_id INTEGER, -- Link to inventory if acquired, or just description if immediate return
    description TEXT,
    status TEXT, -- Intake, In Progress, Waiting Parts, Completed, Delivered
    intake_date TEXT,
    completed_date TEXT,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES contacts(id),
    FOREIGN KEY (firearm_id) REFERENCES firearms(id)
);

CREATE TABLE IF NOT EXISTS job_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    item_type TEXT, -- Part, Labor
    description TEXT,
    quantity REAL,
    cost_per_unit REAL,
    price_per_unit REAL,
    FOREIGN KEY (job_id) REFERENCES gunsmith_jobs(id)
);

-- CRM / PO
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    order_date TEXT,
    expected_date TEXT,
    status TEXT, -- Draft, Ordered, Partial, Received
    notes TEXT,
    FOREIGN KEY (vendor_id) REFERENCES contacts(id)
);

CREATE TABLE IF NOT EXISTS po_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER,
    description TEXT,
    make TEXT,
    model TEXT,
    upc TEXT,
    quantity_ordered INTEGER,
    quantity_received INTEGER DEFAULT 0,
    cost REAL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id)
);

-- Profiles (Multi-FFL) - Schema enhancement for settings
-- We will store profile data in 'settings' table with prefixes, e.g., "profile_1_name", "profile_2_name"
-- Or better, a profiles table if we want robust switching.
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    license_number TEXT,
    premise_address TEXT
);

-- POS / Products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upc TEXT UNIQUE,
    name TEXT,
    description TEXT,
    price REAL,
    cost REAL,
    quantity_on_hand INTEGER DEFAULT 0,
    category TEXT -- Ammo, Accessory, Part
);

CREATE TABLE IF NOT EXISTS sales_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    sale_date TEXT,
    subtotal REAL,
    tax REAL,
    total REAL,
    payment_method TEXT, -- Cash, Card, Check
    status TEXT, -- Completed, Refunded
    FOREIGN KEY (customer_id) REFERENCES contacts(id)
);

CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    product_id INTEGER, -- Link to products
    firearm_id INTEGER, -- Link to firearms (if serialized)
    description TEXT,
    quantity INTEGER,
    price_per_unit REAL,
    FOREIGN KEY (sale_id) REFERENCES sales_orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (firearm_id) REFERENCES firearms(id)
);

-- Gunsmithing Extensions
CREATE TABLE IF NOT EXISTS gunsmith_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    task_name TEXT,
    is_completed BOOLEAN DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    FOREIGN KEY (job_id) REFERENCES gunsmith_jobs(id)
);
