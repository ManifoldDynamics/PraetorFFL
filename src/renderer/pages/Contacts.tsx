import React, { useEffect, useState, ChangeEvent, FormEvent } from 'react';

const Contacts: React.FC = () => {
  const [contacts, setContacts] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    ffl_number: '',
    ffl_expiry: '',
    phone: '',
    email: ''
  });

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    const data = await window.api.getContacts();
    setContacts(data);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await window.api.addContact(formData);
    setFormData({
      name: '',
      address: '',
      ffl_number: '',
      ffl_expiry: '',
      phone: '',
      email: ''
    });
    setShowForm(false);
    loadContacts();
  };

  return (
    <div className="contacts-container">
      <header className="page-header">
        <div>
           <h2>Contacts</h2>
        </div>
        <div className="page-actions">
           <button className={showForm ? 'secondary' : 'primary'} onClick={() => setShowForm(!showForm)}>
             {showForm ? 'Cancel' : 'Add Contact'}
           </button>
        </div>
      </header>
      
      {showForm && (
        <div className="card contact-form-card">
          <h3 style={{ marginTop: 0 }}>Add New Contact</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label>Name (Required)</label>
                <input
                  name="name"
                  placeholder="Full Name or Business Name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Address</label>
                <input
                  name="address"
                  placeholder="Street, City, State, Zip"
                  value={formData.address}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>FFL Number</label>
                <input
                  name="ffl_number"
                  placeholder="x-xx-xxx-xx-xx-xxxxx"
                  value={formData.ffl_number}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>FFL Expiry</label>
                <input
                  name="ffl_expiry"
                  type="date"
                  value={formData.ffl_expiry}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  name="phone"
                  placeholder="(555) 555-5555"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  name="email"
                  type="email"
                  placeholder="contact@example.com"
                  value={formData.email}
                  onChange={handleInputChange}
                />
              </div>
            </div>
            
            <div className="form-actions" style={{ marginTop: 'var(--spacing-md)', display: 'flex', justifyContent: 'flex-end' }}>
               <button type="submit" className="primary">Save Contact</button>
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
              <th>Name</th>
              <th>Address</th>
              <th>FFL #</th>
              <th>Expiry</th>
              <th>Phone</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            {contacts.length > 0 ? (
              contacts.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.address}</td>
                  <td>{c.ffl_number || '-'}</td>
                  <td>{c.ffl_expiry || '-'}</td>
                  <td>{c.phone || '-'}</td>
                  <td>{c.email || '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
                  No contacts found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Contacts;
