import Database from 'better-sqlite3';
import * as path from 'path';
import * as fs from 'fs';

// Determine the database file path based on the environment
let dbPath = '';

const isElectron = process.versions && process.versions.electron;

if (isElectron) {
  const { app } = require('electron');
  const isDev = process.env.NODE_ENV === 'development';
  // In production, store data in userData. In dev, store in project root.
  dbPath = isDev 
    ? path.join(__dirname, '../../praetor.db') 
    : path.join(app.getPath('userData'), 'praetor.db');
} else {
  // Test environment or pure Node
  dbPath = path.join(__dirname, '../../praetor-test.db');
}

// Ensure the directory exists
if (dbPath && dbPath !== ':memory:') {
  const dbDir = path.dirname(dbPath);
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }
}

console.log(`Database path: ${dbPath}`);

const db = new Database(dbPath);

// Initialize schema
db.exec(`
  CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    ffl_number TEXT,
    ffl_expiry TEXT,
    phone TEXT,
    email TEXT
  );

  CREATE TABLE IF NOT EXISTS firearms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,
    importer TEXT,
    model TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    type TEXT NOT NULL,
    caliber TEXT NOT NULL,
    acquisition_date TEXT NOT NULL,
    acquisition_source_contact_id INTEGER,
    disposition_date TEXT,
    disposition_dest_contact_id INTEGER,
    FOREIGN KEY(acquisition_source_contact_id) REFERENCES contacts(id),
    FOREIGN KEY(disposition_dest_contact_id) REFERENCES contacts(id)
  );

  CREATE TABLE IF NOT EXISTS forms_4473 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL DEFAULT 'draft', -- draft, completed
    created_at TEXT NOT NULL,
    completed_at TEXT,
    
    -- Transferee (Buyer) Information
    transferee_first_name TEXT,
    transferee_middle_name TEXT,
    transferee_last_name TEXT,
    transferee_address TEXT,
    transferee_city TEXT,
    transferee_state TEXT,
    transferee_zip TEXT,
    transferee_county TEXT,
    transferee_dob TEXT,
    transferee_birth_place TEXT,
    transferee_phone TEXT,
    transferee_email TEXT,

    -- Identification
    identification_type TEXT,
    identification_number TEXT,
    identification_expiry TEXT,

    -- Questionnaire (11.a - 11.m in 2023 form, simplified here)
    q_11_a BOOLEAN, -- Actual buyer?
    q_11_b BOOLEAN, -- Prohibited person?
    q_11_c BOOLEAN, -- Felony?
    q_11_d BOOLEAN, -- Fugitive?
    q_11_e BOOLEAN, -- Drug user?
    q_11_f BOOLEAN, -- Mental defective?
    q_11_g BOOLEAN, -- Dishonorable discharge?
    q_11_h BOOLEAN, -- Restraining order?
    q_11_i BOOLEAN -- Domestic violence?
  );

  CREATE TABLE IF NOT EXISTS forms_4473_items (
    form_id INTEGER NOT NULL,
    firearm_id INTEGER NOT NULL,
    FOREIGN KEY(form_id) REFERENCES forms_4473(id),
    FOREIGN KEY(firearm_id) REFERENCES firearms(id)
  );
`);

// Database Helper Functions

// Contacts
export const getContacts = () => {
  return db.prepare('SELECT * FROM contacts ORDER BY name').all();
};

export const addContact = (contact: { name: string, address: string, ffl_number?: string, ffl_expiry?: string, phone?: string, email?: string }) => {
  const stmt = db.prepare(`
    INSERT INTO contacts (name, address, ffl_number, ffl_expiry, phone, email)
    VALUES (@name, @address, @ffl_number, @ffl_expiry, @phone, @email)
  `);
  return stmt.run({
    name: contact.name,
    address: contact.address || null,
    ffl_number: contact.ffl_number || null,
    ffl_expiry: contact.ffl_expiry || null,
    phone: contact.phone || null,
    email: contact.email || null
  });
};

// Firearms (A&D)
export const getBoundBook = () => {
  return db.prepare(`
    SELECT 
      f.*,
      source.name as source_name,
      dest.name as dest_name
    FROM firearms f
    LEFT JOIN contacts source ON f.acquisition_source_contact_id = source.id
    LEFT JOIN contacts dest ON f.disposition_dest_contact_id = dest.id
    ORDER BY f.acquisition_date DESC
  `).all();
};

export const searchBoundBook = (query: string) => {
  const searchQuery = `%${query}%`;
  return db.prepare(`
    SELECT 
      f.*,
      source.name as source_name,
      dest.name as dest_name
    FROM firearms f
    LEFT JOIN contacts source ON f.acquisition_source_contact_id = source.id
    LEFT JOIN contacts dest ON f.disposition_dest_contact_id = dest.id
    WHERE 
      f.manufacturer LIKE @query OR
      f.model LIKE @query OR
      f.serial_number LIKE @query OR
      source.name LIKE @query OR
      dest.name LIKE @query
    ORDER BY f.acquisition_date DESC
  `).all({ query: searchQuery });
};

export const getInventory = () => {
  return db.prepare(`
    SELECT 
      f.*,
      source.name as source_name
    FROM firearms f
    LEFT JOIN contacts source ON f.acquisition_source_contact_id = source.id
    WHERE f.disposition_date IS NULL
    ORDER BY f.acquisition_date DESC
  `).all();
};

export const searchInventory = (query: string) => {
  const searchQuery = `%${query}%`;
  return db.prepare(`
    SELECT 
      f.*,
      source.name as source_name
    FROM firearms f
    LEFT JOIN contacts source ON f.acquisition_source_contact_id = source.id
    WHERE 
      f.disposition_date IS NULL AND (
        f.manufacturer LIKE @query OR
        f.model LIKE @query OR
        f.serial_number LIKE @query OR
        source.name LIKE @query
      )
    ORDER BY f.acquisition_date DESC
  `).all({ query: searchQuery });
};

export const addAcquisition = (firearm: {
  manufacturer: string,
  importer?: string,
  model: string,
  serial_number: string,
  type: string,
  caliber: string,
  acquisition_date: string,
  acquisition_source_contact_id: number
}) => {
  const stmt = db.prepare(`
    INSERT INTO firearms (
      manufacturer, importer, model, serial_number, type, caliber, 
      acquisition_date, acquisition_source_contact_id
    )
    VALUES (
      @manufacturer, @importer, @model, @serial_number, @type, @caliber, 
      @acquisition_date, @acquisition_source_contact_id
    )
  `);
  return stmt.run({
    manufacturer: firearm.manufacturer,
    importer: firearm.importer || null,
    model: firearm.model,
    serial_number: firearm.serial_number,
    type: firearm.type,
    caliber: firearm.caliber,
    acquisition_date: firearm.acquisition_date,
    acquisition_source_contact_id: firearm.acquisition_source_contact_id
  });
};

export const addDisposition = (disposition: {
  id: number,
  disposition_date: string,
  disposition_dest_contact_id: number
}) => {
  const stmt = db.prepare(`
    UPDATE firearms 
    SET disposition_date = @disposition_date, 
        disposition_dest_contact_id = @disposition_dest_contact_id
    WHERE id = @id
  `);
  return stmt.run(disposition);
};

// ATF 4473 Functions

export const get4473s = () => {
  return db.prepare('SELECT * FROM forms_4473 ORDER BY created_at DESC').all();
};

export const get4473ById = (id: number) => {
  const form = db.prepare('SELECT * FROM forms_4473 WHERE id = ?').get(id);
  if (!form) return null;
  const items = db.prepare(`
    SELECT f.* 
    FROM firearms f
    JOIN forms_4473_items i ON f.id = i.firearm_id
    WHERE i.form_id = ?
  `).all(id);
  return { ...form, items };
};

export const create4473 = () => {
  const result = db.prepare(`
    INSERT INTO forms_4473 (created_at) VALUES (?)
  `).run(new Date().toISOString());
  return result.lastInsertRowid;
};

export const update4473 = (id: number, data: any) => {
  // Construct UPDATE query dynamically based on data keys
  const allowedColumns = [
    'status', 'completed_at', 
    'transferee_first_name', 'transferee_middle_name', 'transferee_last_name',
    'transferee_address', 'transferee_city', 'transferee_state', 'transferee_zip',
    'transferee_county', 'transferee_dob', 'transferee_birth_place',
    'transferee_phone', 'transferee_email',
    'identification_type', 'identification_number', 'identification_expiry',
    'q_11_a', 'q_11_b', 'q_11_c', 'q_11_d', 'q_11_e', 'q_11_f',
    'q_11_g', 'q_11_h', 'q_11_i'
  ];
  
  const keys = Object.keys(data).filter(k => allowedColumns.includes(k));
  if (keys.length === 0) return;

  const setClause = keys.map(k => `${k} = @${k}`).join(', ');
  const stmt = db.prepare(`UPDATE forms_4473 SET ${setClause} WHERE id = @id`);
  return stmt.run({ ...data, id });
};

export const addFirearmTo4473 = (formId: number, firearmId: number) => {
  return db.prepare('INSERT INTO forms_4473_items (form_id, firearm_id) VALUES (?, ?)').run(formId, firearmId);
};

export const removeFirearmFrom4473 = (formId: number, firearmId: number) => {
  return db.prepare('DELETE FROM forms_4473_items WHERE form_id = ? AND firearm_id = ?').run(formId, firearmId);
};

export const complete4473 = (formId: number) => {
  // 1. Mark form as completed
  const now = new Date().toISOString();
  db.prepare("UPDATE forms_4473 SET status = 'completed', completed_at = ? WHERE id = ?").run(now, formId);

  // 2. Create a "Customer" contact from the form data (if we want to track them as contacts)
  // For now, let's just create a contact to link the disposition to.
  const form = db.prepare('SELECT * FROM forms_4473 WHERE id = ?').get(formId) as any;
  
  const contactResult = db.prepare(`
    INSERT INTO contacts (name, address, phone, email)
    VALUES (?, ?, ?, ?)
  `).run(
    `${form.transferee_first_name} ${form.transferee_last_name}`,
    `${form.transferee_address}, ${form.transferee_city}, ${form.transferee_state} ${form.transferee_zip}`,
    form.transferee_phone,
    form.transferee_email
  );
  
  const contactId = contactResult.lastInsertRowid;

  // 3. Dispose all firearms on this form to that contact
  const items = db.prepare('SELECT firearm_id FROM forms_4473_items WHERE form_id = ?').all(formId) as any[];
  const disposeStmt = db.prepare(`
    UPDATE firearms 
    SET disposition_date = ?, 
        disposition_dest_contact_id = ?
    WHERE id = ?
  `);

  const date = now.split('T')[0]; // YYYY-MM-DD
  for (const item of items) {
    disposeStmt.run(date, contactId, item.firearm_id);
  }

  return { success: true };
};

export default db;
