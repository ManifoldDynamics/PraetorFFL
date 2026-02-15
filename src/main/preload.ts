import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  // Contacts
  getContacts: () => ipcRenderer.invoke('db-get-contacts'),
  addContact: (contact: any) => ipcRenderer.invoke('db-add-contact', contact),

  // Firearms
  getBoundBook: () => ipcRenderer.invoke('db-get-bound-book'),
  searchBoundBook: (query: string) => ipcRenderer.invoke('db-search-bound-book', query),
  getInventory: () => ipcRenderer.invoke('db-get-inventory'),
  searchInventory: (query: string) => ipcRenderer.invoke('db-search-inventory', query),
  addAcquisition: (firearm: any) => ipcRenderer.invoke('db-add-acquisition', firearm),
  addDisposition: (disposition: any) => ipcRenderer.invoke('db-add-disposition', disposition),

  // ATF 4473
  get4473s: () => ipcRenderer.invoke('db-get-4473s'),
  get4473ById: (id: number) => ipcRenderer.invoke('db-get-4473-by-id', id),
  create4473: () => ipcRenderer.invoke('db-create-4473'),
  update4473: (id: number, data: any) => ipcRenderer.invoke('db-update-4473', { id, data }),
  addFirearmTo4473: (formId: number, firearmId: number) => ipcRenderer.invoke('db-add-firearm-to-4473', { formId, firearmId }),
  complete4473: (formId: number) => ipcRenderer.invoke('db-complete-4473', formId),
});
