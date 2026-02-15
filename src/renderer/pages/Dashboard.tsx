import React, { useEffect, useState } from 'react';

const Dashboard: React.FC = () => {
  const [inventoryCount, setInventoryCount] = useState<number>(0);
  const [contactCount, setContactCount] = useState<number>(0);
  const [formsCount, setFormsCount] = useState<number>(0);

  useEffect(() => {
    async function loadData() {
      try {
        const inventory = await window.api.getInventory();
        setInventoryCount(inventory.length);
        
        const contacts = await window.api.getContacts();
        setContactCount(contacts.length);
        
        const forms = await window.api.get4473s();
        setFormsCount(forms.length);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      }
    }
    loadData();
  }, []);

  return (
    <div className="dashboard-container">
      <header className="page-header">
        <div>
          <h1 style={{ marginBottom: '0.5rem', color: 'var(--color-primary)' }}>Dashboard</h1>
          <p style={{ margin: 0 }}>Overview of your FFL operations</p>
        </div>
        <div className="page-actions">
           <button className="primary" onClick={() => window.location.reload()}>Refresh Data</button>
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon inventory-icon">📦</div>
          <div className="stat-content">
            <h3>Inventory</h3>
            <p className="stat-value">{inventoryCount}</p>
            <span className="stat-label">Items in stock</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon contacts-icon">👥</div>
          <div className="stat-content">
            <h3>Contacts</h3>
            <p className="stat-value">{contactCount}</p>
            <span className="stat-label">Active customers</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon forms-icon">📝</div>
          <div className="stat-content">
            <h3>4473 Forms</h3>
            <p className="stat-value">{formsCount}</p>
            <span className="stat-label">Total forms</span>
          </div>
        </div>
      </div>
      
      {/* Placeholder for future charts or recent activity */}
      <div className="dashboard-section">
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Quick Actions</h2>
        <div className="quick-actions-grid">
           <div className="action-card" onClick={() => (document.querySelector('li:nth-child(2)') as HTMLElement)?.click()}>
              <h4>Add Inventory</h4>
              <p>Process new acquisitions</p>
           </div>
           <div className="action-card" onClick={() => (document.querySelector('li:nth-child(5)') as HTMLElement)?.click()}>
              <h4>Start 4473</h4>
              <p>Begin a new transfer</p>
           </div>
        </div>
      </div>

      <style>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: var(--spacing-lg);
          margin-bottom: var(--spacing-xl);
        }

        .stat-card {
          background-color: var(--color-surface);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
          box-shadow: var(--shadow-sm);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          gap: var(--spacing-lg);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
        }

        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
        }

        .inventory-icon { background-color: #e0f2fe; color: #0284c7; }
        .contacts-icon { background-color: #dcfce7; color: #16a34a; }
        .forms-icon { background-color: #fef9c3; color: #ca8a04; }

        .stat-content h3 {
          margin: 0;
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          font-weight: 600;
        }

        .stat-value {
          margin: 0;
          font-size: 2rem;
          font-weight: 700;
          color: var(--color-text);
          line-height: 1.2;
        }

        .stat-label {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
        }
        
        .dashboard-section {
          margin-top: var(--spacing-xl);
        }

        .quick-actions-grid {
           display: grid;
           grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
           gap: var(--spacing-md);
        }

        .action-card {
           background-color: var(--color-surface);
           border: 1px solid var(--color-border); /* Dashed border for action look */
           border-radius: var(--radius-md);
           padding: var(--spacing-md);
           cursor: pointer;
           transition: all 0.2s;
           text-align: center;
        }

        .action-card:hover {
           border-color: var(--color-accent);
           background-color: #eff6ff;
        }
        
        .action-card h4 {
           margin: 0 0 var(--spacing-xs) 0;
           color: var(--color-accent);
        }
        
        .action-card p {
           margin: 0;
           font-size: 0.8rem;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
