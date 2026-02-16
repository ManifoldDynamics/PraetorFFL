from ffl_suite.database.db_manager import execute_query

def get_profiles():
    return execute_query("SELECT * FROM profiles", fetch=True)

def add_profile(name, license_num, address):
    execute_query("INSERT INTO profiles (name, license_number, premise_address) VALUES (?, ?, ?)", (name, license_num, address))

def set_active_profile(profile_id):
    # For now, we just update the main settings table to mirror the selected profile
    # This keeps the rest of the app working without refactoring every get_ffl_info call
    prof = execute_query("SELECT * FROM profiles WHERE id = ?", (profile_id,), fetch=True)
    if prof:
        p = prof[0]
        from ffl_suite.logic.settings_manager import set_setting
        set_setting('ffl_name', p[1])
        set_setting('ffl_license_number', p[2])
        set_setting('ffl_premise_address', p[3])
