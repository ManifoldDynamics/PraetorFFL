import React, { useEffect, useState } from 'react';

const Forms4473: React.FC = () => {
  const [forms, setForms] = useState<any[]>([]);

  useEffect(() => {
    loadForms();
  }, []);

  const loadForms = async () => {
    const data = await window.api.get4473s();
    setForms(data);
  };

  const handleCreate = async () => {
    await window.api.create4473();
    loadForms();
  };

  const handleEdit = (id: number) => {
    window.dispatchEvent(new CustomEvent('navigate-to-form-editor', { detail: { id } }));
  };

  return (
    <div className="forms-4473-container">
      <header className="page-header">
         <div>
            <h2>ATF Forms 4473</h2>
         </div>
         <div className="page-actions">
            <button className="primary" onClick={handleCreate}>Start New 4473</button>
         </div>
      </header>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Created At</th>
              <th>Status</th>
              <th>Buyer Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {forms.length > 0 ? (
              forms.map((form) => (
                <tr key={form.id}>
                  <td>#{form.id}</td>
                  <td>{new Date(form.created_at).toLocaleDateString()}</td>
                  <td>
                    <span className={`badge ${form.status === 'completed' ? 'completed' : 'draft'}`}>
                      {form.status.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    {form.transferee_first_name 
                      ? `${form.transferee_first_name} ${form.transferee_last_name}` 
                      : <span style={{ color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>Pending...</span>}
                  </td>
                  <td>
                    <button className="secondary" onClick={() => handleEdit(form.id)}>
                      {form.status === 'completed' ? 'View' : 'Edit / Continue'}
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
                  No 4473 forms started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Forms4473;
