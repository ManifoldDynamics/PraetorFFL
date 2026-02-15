import * as fs from 'fs';
import * as path from 'path';
import * as assert from 'assert';

const dbPath = path.join(__dirname, '../praetor-test.db');

async function runTests() {
  // Clean up previous test run
  if (fs.existsSync(dbPath)) {
    try {
      fs.unlinkSync(dbPath);
    } catch (e) {
      console.log('Could not delete DB file, might be open. Proceeding...');
    }
  }

  // Dynamic import to ensure DB is initialized AFTER cleanup
  const dbModule = await import('../src/main/database');
  const { 
    addContact, 
    getContacts, 
    addAcquisition, 
    getBoundBook, 
    getInventory, 
    create4473,
    update4473,
    addFirearmTo4473,
    get4473ById,
    complete4473,
    default: db 
  } = dbModule;

  console.log('Running tests...');

  // Clear tables just in case
  db.prepare('DELETE FROM firearms').run();
  db.prepare('DELETE FROM contacts').run();
  db.prepare('DELETE FROM forms_4473').run();
  db.prepare('DELETE FROM forms_4473_items').run();

  // 1. Setup Data (Contact + Firearm)
  addContact({ name: 'Vendor A', address: '123 St' });
  const vendor = (getContacts() as any[])[0];
  const vendorId = vendor.id;

  addAcquisition({
    manufacturer: 'Glock', model: '19', serial_number: '12345',
    type: 'Pistol', caliber: '9mm', acquisition_date: '2024-01-01',
    acquisition_source_contact_id: vendorId
  });
  const firearm = (getInventory() as any[])[0];
  const firearmId = firearm.id;

  // 2. Test 4473 Creation
  console.log('Testing 4473 Creation...');
  const formId = create4473();
  assert.ok(formId);
  
  const form = get4473ById(formId as number) as any;
  assert.ok(form);
  assert.strictEqual(form.status, 'draft');

  // 3. Test 4473 Update
  console.log('Testing 4473 Update...');
  update4473(formId as number, {
    transferee_first_name: 'John',
    transferee_last_name: 'Doe',
    q_11_a: 1 // true in sqlite is 1
  });
  
  const updatedForm = get4473ById(formId as number) as any;
  assert.strictEqual(updatedForm.transferee_first_name, 'John');
  assert.strictEqual(updatedForm.q_11_a, 1);

  // 4. Test Adding Firearm
  console.log('Testing Adding Firearm to 4473...');
  addFirearmTo4473(formId as number, firearmId);
  
  const formWithItems = get4473ById(formId as number) as any;
  assert.strictEqual(formWithItems.items.length, 1);
  assert.strictEqual(formWithItems.items[0].serial_number, '12345');

  // 5. Test Completion & Disposition
  console.log('Testing 4473 Completion...');
  complete4473(formId as number);
  
  const completedForm = get4473ById(formId as number) as any;
  assert.strictEqual(completedForm.status, 'completed');

  // Check Inventory (Should be empty)
  const inventory = getInventory() as any[];
  assert.strictEqual(inventory.length, 0);

  // Check Bound Book (Should have disposition)
  const boundBook = getBoundBook() as any[];
  assert.ok(boundBook[0].disposition_date);
  
  // Note: Depending on implementation, complete4473 might create a contact. 
  // In my implementation, I create a contact with the transferee's name.
  // "John Doe"
  
  // Let's check the destination contact name
  assert.strictEqual(boundBook[0].dest_name, 'John Doe');

  console.log('All tests passed!');
}

runTests().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
