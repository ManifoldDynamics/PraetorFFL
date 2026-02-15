import unittest
import os
import sqlite3
import ffl_suite.database.db_manager
from ffl_suite.database.db_manager import execute_query, init_db
from ffl_suite.logic.inventory_manager import add_acquisition, record_disposition, get_bound_book
from ffl_suite.logic.compliance import can_acquire, can_dispose
from ffl_suite.logic.settings_manager import set_setting, get_ffl_info

TEST_DB = 'test_ffl_data.db'

class TestCompliance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Monkeypatch DB_FILE
        ffl_suite.database.db_manager.DB_FILE = TEST_DB
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_settings(self):
        set_setting('ffl_name', 'Test Armory')
        info = get_ffl_info()
        self.assertEqual(info['name'], 'Test Armory')

    def test_acquisition_compliance(self):
        # Create contact
        execute_query("INSERT INTO contacts (name) VALUES (?)", ('Supplier Inc',))
        res = execute_query("SELECT id FROM contacts WHERE name = ?", ('Supplier Inc',), fetch=True)
        contact_id = res[0][0]

        data = {
            'make': 'Glock', 'model': '19', 'serial_number': 'ABC12345',
            'type': 'Pistol', 'caliber': '9mm', 'acquisition_date': '2023-01-01'
        }

        # Check can_acquire
        self.assertTrue(can_acquire('Glock', '19', 'ABC12345'))

        # Add it
        add_acquisition(data, contact_id)

        # Check can_acquire again (should be False)
        self.assertFalse(can_acquire('Glock', '19', 'ABC12345'))

    def test_disposition_compliance(self):
        # Get the firearm ID
        res = execute_query("SELECT id FROM firearms WHERE serial_number = 'ABC12345'", fetch=True)
        fid = res[0][0]

        # Check can_dispose
        self.assertTrue(can_dispose(fid))

        # Dispose
        execute_query("INSERT INTO contacts (name) VALUES (?)", ('Buyer Bob',))
        res = execute_query("SELECT id FROM contacts WHERE name = ?", ('Buyer Bob',), fetch=True)
        buyer_id = res[0][0]

        record_disposition(fid, buyer_id, '2023-01-02')

        # Check can_dispose again (should be False)
        self.assertFalse(can_dispose(fid))

        # Verify Bound Book
        bb = get_bound_book()
        # Should be 1 record
        self.assertEqual(len(bb), 1)
        # Check disposition date is at index 8 (based on updated query in inventory_manager)
        # 0:id, 1:make, 2:model, 3:serial, 4:type, 5:caliber, 6:acq_date, 7:source_name, 8:disp_date, 9:dest_name
        self.assertEqual(bb[0][8], '2023-01-02')

if __name__ == '__main__':
    unittest.main()
