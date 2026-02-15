export {};

declare global {
  interface Window {
    api: {
      getContacts: () => Promise<any[]>;
      addContact: (contact: any) => Promise<any>;
      getBoundBook: () => Promise<any[]>;
      searchBoundBook: (query: string) => Promise<any[]>;
      getInventory: () => Promise<any[]>;
      searchInventory: (query: string) => Promise<any[]>;
      addAcquisition: (firearm: any) => Promise<any>;
      addDisposition: (disposition: any) => Promise<any>;
      
      get4473s: () => Promise<any[]>;
      get4473ById: (id: number) => Promise<any>;
      create4473: () => Promise<number>;
      update4473: (id: number, data: any) => Promise<any>;
      addFirearmTo4473: (formId: number, firearmId: number) => Promise<any>;
      complete4473: (formId: number) => Promise<any>;
    };
  }
}
