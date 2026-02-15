import React, { useEffect, useState, ChangeEvent, FormEvent } from 'react';

const BoundBook: React.FC = () => {
  const [boundBook, setBoundBook] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({
    manufacturer: '',
    importer: '',
    model: '',
    serial_number: '',
    type: 'Pistol',
    caliber: '',
    acquisition_date: new Date().toISOString().split('T')[0],
    acquisition_source_contact_id: ''
  });

  useEffect(() => {
    loadBoundBook();
    loadContacts();
  }, []);

  const loadBoundBook = async () => {
    const data = await window.api.getBoundBook();
    setBoundBook(data);
  };

  const handleSearch = async (e: ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length > 0) {
      const data = await window.api.searchBoundBook(query);
      setBoundBook(data);
    } else {
      loadBoundBook();
    }
  };

  const loadContacts = async () => {
    const data = await window.api.getContacts();
    setContacts(data);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!formData.acquisition_source_contact_id) {
      alert('Please select a source contact');
      return;
    }
    
    await window.api.addAcquisition({
      ...formData,
      acquisition_source_contact_id: Number(formData.acquisition_source_contact_id)
    });
    
    setFormData({
      manufacturer: '',
      importer: '',
      model: '',
      serial_number: '',
      type: 'Pistol',
      caliber: '',
      acquisition_date: new Date().toISOString().split('T')[0],
      acquisition_source_contact_id: ''
    });
    setShowForm(false);
    loadBoundBook();
  };

  return (
    <div className="bound-book-container">
      <header className="page-header">
        <div>
           <h2>Bound Book (A&D Record)</h2>
        </div>
        <div className="page-actions">
           <div className="search-box">
             <input 
              type="text" 
              placeholder="Search..." 
              value={searchQuery} 
              onChange={handleSearch} 
            />
           </div>
           <button className={showForm ? 'secondary' : 'primary'} onClick={() => setShowForm(!showForm)}>
             {showForm ? 'Cancel' : 'Add Acquisition'}
           </button>
        </div>
      </header>

      {showForm && (
        <div className="card acquisition-form-card">
          <h3 style={{ marginTop: 0 }}>New Acquisition</h3>
          <form onSubmit={handleSubmit} className="acquisition-form">
            <div className="form-grid">
               <div className="form-group">
                  <label>Manufacturer</label>
                  <input name="manufacturer" placeholder="e.g. Glock" value={formData.manufacturer} onChange={handleInputChange} required />
               </div>
               <div className="form-group">
                  <label>Importer</label>
                  <input name="importer" placeholder="e.g. Glock Inc." value={formData.importer} onChange={handleInputChange} />
               </div>
               <div className="form-group">
                  <label>Model</label>
                  <input name="model" placeholder="e.g. 19 Gen 5" value={formData.model} onChange={handleInputChange} required />
               </div>
               <div className="form-group">
                  <label>Serial Number</label>
                  <input name="serial_number" placeholder="Unique Serial" value={formData.serial_number} onChange={handleInputChange} required />
               </div>
               <div className="form-group">
                  <label>Type</label>
                  <select name="type" value={formData.type} onChange={handleInputChange}>
                    <option value="Pistol">Pistol</option>
                    <option value="Revolver">Revolver</option>
                    <option value="Rifle">Rifle</option>
                    <option value="Shotgun">Shotgun</option>
                    <option value="Receiver">Receiver</option>
                    <option value="Other">Other</option>
                  </select>
               </div>
               <div className="form-group">
                  <label>Caliber</label>
                  <input name="caliber" placeholder="e.g. 9mm" value={formData.caliber} onChange={handleInputChange} required />
               </div>
               <div className="form-group">
                  <label>Date Acquired</label>
                  <input name="acquisition_date" type="date" value={formData.acquisition_date} onChange={handleInputChange} required />
               </div>
               <div className="form-group">
                  <label>Source Contact</label>
                  <select name="acquisition_source_contact_id" value={formData.acquisition_source_contact_id} onChange={handleInputChange} required>
                    <option value="">Select Source Contact</option>
                    {contacts.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
               </div>
            </div>
            
            <div className="form-actions" style={{ marginTop: 'var(--spacing-md)', display: 'flex', justifyContent: 'flex-end' }}>
               <button type="submit" className="primary">Save Acquisition</button>
            </div>
          </form>
          <style>{`
             .form-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: var(--spacing-md);
             }
             .form-group {
                display: flex;
                flex-direction: column;
                gap: 4px;
             }
             .form-group label {
                font-size: 0.8rem;
                color: var(--color-text-secondary);
                font-weight: 500;
             }
          `}</style>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Acq Date</th>
              <th>Manufacturer</th>
              <th>Model</th>
              <th>Serial #</th>
              <th>Source</th>
              <th>Disp Date</th>
              <th>Disposition</th>
            </tr>
          </thead>
          <tbody>
            {boundBook.length > 0 ? (
              boundBook.map((record) => (
                <tr key={record.id}>
                  <td>{record.acquisition_date}</td>
                  <td>{record.manufacturer}</td>
                  <td>{record.model}</td>
                  <td>{record.serial_number}</td>
                  <td>{record.source_name}</td>
                  <td>{record.disposition_date || '-'}</td>
                  <td>{record.dest_name || '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
                  No records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BoundBook;
