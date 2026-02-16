from ffl_suite.database.db_manager import execute_query

def add_nfa_entity(data):
    """Adds an NFA Entity (Individual/Trust/Corp)."""
    sql = """
        INSERT INTO nfa_entities (entity_type, name, address_street, address_city, address_state, address_zip, phone, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data['entity_type'], data['name'], data['address_street'], data['address_city'],
        data['address_state'], data['address_zip'], data.get('phone'), data.get('email')
    )
    return execute_query(sql, params)

def get_nfa_entities():
    sql = "SELECT id, name, entity_type FROM nfa_entities ORDER BY name"
    return execute_query(sql, fetch=True)

def get_nfa_entity_details(entity_id):
    sql = "SELECT * FROM nfa_entities WHERE id = ?"
    res = execute_query(sql, (entity_id,), fetch=True)
    return res[0] if res else None

def add_responsible_person(entity_id, data):
    """Adds a Responsible Person to an entity."""
    sql = """
        INSERT INTO responsible_persons
        (entity_id, first_name, middle_name, last_name, title, dob, pob_city, pob_state, pob_country, ssn, upin, photo_path, fingerprint_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        entity_id, data['first_name'], data.get('middle_name'), data['last_name'], data.get('title'),
        data.get('dob'), data.get('pob_city'), data.get('pob_state'), data.get('pob_country'),
        data.get('ssn'), data.get('upin'), data.get('photo_path'), data.get('fingerprint_path')
    )
    return execute_query(sql, params)

def get_responsible_persons(entity_id):
    sql = "SELECT * FROM responsible_persons WHERE entity_id = ?"
    return execute_query(sql, (entity_id,), fetch=True)


def create_nfa_form(form_type, entity_id, firearm_id, cleo_data):
    """Creates a draft NFA form."""
    sql = """
        INSERT INTO nfa_forms (form_type, status, transferee_entity_id, firearm_id, cleo_name, cleo_title, cleo_agency, cleo_address_street, cleo_address_city, cleo_address_state, cleo_address_zip)
        VALUES (?, 'Draft', ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        form_type, entity_id, firearm_id,
        cleo_data.get('cleo_name'), cleo_data.get('cleo_title'), cleo_data.get('cleo_agency'),
        cleo_data.get('cleo_address_street'), cleo_data.get('cleo_address_city'), cleo_data.get('cleo_address_state'), cleo_data.get('cleo_address_zip')
    )
    return execute_query(sql, params)

def get_nfa_forms():
    sql = """
        SELECT f.id, f.form_type, f.status, e.name, i.make, i.model
        FROM nfa_forms f
        JOIN nfa_entities e ON f.transferee_entity_id = e.id
        JOIN firearms i ON f.firearm_id = i.id
        ORDER BY f.id DESC
    """
    return execute_query(sql, fetch=True)

def get_nfa_form_details(form_id):
    # Fetch Form + Entity + Firearm + Responsible Persons
    form_sql = """
        SELECT f.*, e.name as entity_name, e.entity_type,
               i.make, i.model, i.serial_number, i.caliber, i.type, i.acquisition_date
        FROM nfa_forms f
        JOIN nfa_entities e ON f.transferee_entity_id = e.id
        JOIN firearms i ON f.firearm_id = i.id
        WHERE f.id = ?
    """
    form_res = execute_query(form_sql, (form_id,), fetch=True)
    if not form_res: return None

    # Simple dict conversion (assuming column order, but for PDF generator robust dict is better)
    # Let's return the raw tuple + fetched RP list for now, the generator can parse indices or we map to dict
    # Mapping to dict for cleaner usage:
    # Columns in nfa_forms: id(0), type(1), status(2), sub_date(3), app_date(4), control(5), ent_id(6), fire_id(7), cleo...(8-14)
    # Extra columns: entity_name(15), entity_type(16), make(17), model(18), serial(19), cal(20), type(21), acq(22)

    row = form_res[0]
    data = {
        'id': row[0], 'form_type': row[1], 'status': row[2], 'submitted_date': row[3], 'control_number': row[5],
        'cleo_name': row[8], 'cleo_agency': row[10], 'cleo_address': f"{row[11]} {row[12]} {row[13]} {row[14]}",
        'entity_name': row[15], 'entity_type': row[16],
        'firearm_make': row[17], 'firearm_model': row[18], 'firearm_serial': row[19],
        'firearm_cal': row[20], 'firearm_type': row[21],
        'transferee_entity_id': row[6]
    }

    rps = get_responsible_persons(row[6])
    data['responsible_persons'] = rps # List of tuples

    return data
