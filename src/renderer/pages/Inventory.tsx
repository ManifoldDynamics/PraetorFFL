import React, { useEffect, useState, ChangeEvent, FormEvent } from 'react';

const Inventory: React.FC = () => {
  const [inventory, setInventory] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [dispositionData, setDispositionData] = useState({
    disposition_date: new Date().toISOString().split('T')[0],
    disposition_dest_contact_id: ''
  });

  useEffect(() => {
    loadInventory();
    loadContacts();
  }, []);

  const loadInventory = async () => {
    const data = await window.api.getInventory();
    setInventory(data);
  };

  const handleSearch = async (e: ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length > 0) {
      const data = await window.api.searchInventory(query);
      setInventory(data);
    } else {
      loadInventory();
    }
  };

  const loadContacts = async () => {
    const data = await window.api.getContacts();
    setContacts(data);
  };

  const handleDisposeClick = (item: any) => {
    setSelectedItem(item);
    setDispositionData({
      disposition_date: new Date().toISOString().split('T')[0],
      disposition_dest_contact_id: ''
    });
  };

  const handleDispositionSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!dispositionData.disposition_dest_contact_id) {
      alert('Please select a destination contact');
      return;
    }

    await window.api.addDisposition({
      id: selectedItem.id,
      disposition_date: dispositionData.disposition_date,
      disposition_dest_contact_id: Number(dispositionData.disposition_dest_contact_id)
    });

    setSelectedItem(null);
    loadInventory();
  };

  return (
    <div className="inventory-container">
      <header className="page-header">
        <div>
           <h2>Current Inventory</h2>
        </div>
        <div className="search-box">
           <input 
            type="text" 
            placeholder="Search Serial, Model, Manufacturer..." 
            value={searchQuery} 
            onChange={handleSearch} 
            style={{ width: '300px' }}
          />
        </div>
      </header>

      {selectedItem && (
        <div className="card disposition-card" style={{ borderLeft: '4px solid var(--color-warning)' }}>
          <h3 style={{ marginTop: 0 }}>Dispose Firearm</h3>
          <p><strong>{selectedItem.manufacturer} {selectedItem.model}</strong> (Serial: {selectedItem.serial_number})</p>
          
          <form onSubmit={handleDispositionSubmit} className="disposition-form">
            <div className="form-group">
               <label>Date of Disposition</label>
               <input 
                type="date" 
                value={dispositionData.disposition_date} 
                onChange={(e) => setDispositionData({...dispositionData, disposition_date: e.target.value})} 
                required 
              />
            </div>
            
            <div className="form-group">
               <label>Transferee (Buyer)</label>
               <select 
                value={dispositionData.disposition_dest_contact_id} 
                onChange={(e) => setDispositionData({...dispositionData, disposition_dest_contact_id: e.target.value})} 
                required 
              >
                <option value="">Select Destination Contact</option>
                {contacts.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            
            <div className="form-actions" style={{ marginTop: 'var(--spacing-md)' }}>
              <button type="submit" className="primary">Confirm Disposition</button>
              <button type="button" className="secondary" onClick={() => setSelectedItem(null)} style={{ marginLeft: '10px' }}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Date Acquired</th>
              <th>Manufacturer</th>
              <th>Model</th>
              <th>Serial #</th>
              <th>Type</th>
              <th>Caliber</th>
              <th style={{ textAlign: 'center' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {inventory.length > 0 ? (
              inventory.map((item) => (
                <tr key={item.id}>
                  <td>{item.acquisition_date}</td>
                  <td>{item.manufacturer}</td>
                  <td>{item.model}</td>
                  <td>{item.serial_number}</td>
                  <td>{item.type}</td>
                  <td>{item.caliber}</td>
                  <td style={{ textAlign: 'center' }}>
                    <button className="primary" style={{ fontSize: '0.75rem', padding: '2px 8px' }} onClick={() => handleDisposeClick(item)}>Dispose</button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
                  No items in inventory.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Inventory;
