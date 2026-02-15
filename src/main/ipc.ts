import { ipcMain } from 'electron';
import * as db from './database';

export function registerIpcHandlers() {
  ipcMain.on('ping', () => console.log('pong'));

  // Database Handlers

  // Contacts
  ipcMain.handle('db-get-contacts', async () => {
    return db.getContacts();
  });

  ipcMain.handle('db-add-contact', async (_event, contact) => {
    return db.addContact(contact);
  });

  // Firearms
  ipcMain.handle('db-get-bound-book', async () => {
    return db.getBoundBook();
  });

  ipcMain.handle('db-get-inventory', async () => {
    return db.getInventory();
  });

  ipcMain.handle('db-search-inventory', async (_event, query) => {
    return db.searchInventory(query);
  });

  ipcMain.handle('db-search-bound-book', async (_event, query) => {
    return db.searchBoundBook(query);
  });

  ipcMain.handle('db-add-acquisition', async (_event, firearm) => {
    return db.addAcquisition(firearm);
  });

  ipcMain.handle('db-add-disposition', async (_event, disposition) => {
    return db.addDisposition(disposition);
  });

  // ATF 4473
  ipcMain.handle('db-get-4473s', async () => {
    return db.get4473s();
  });

  ipcMain.handle('db-get-4473-by-id', async (_event, id) => {
    return db.get4473ById(id);
  });

  ipcMain.handle('db-create-4473', async () => {
    return db.create4473();
  });

  ipcMain.handle('db-update-4473', async (_event, { id, data }) => {
    return db.update4473(id, data);
  });

  ipcMain.handle('db-add-firearm-to-4473', async (_event, { formId, firearmId }) => {
    return db.addFirearmTo4473(formId, firearmId);
  });

  ipcMain.handle('db-complete-4473', async (_event, formId) => {
    return db.complete4473(formId);
  });
}
