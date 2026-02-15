import { useEffect, useState } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';
import Contacts from './pages/Contacts';
import BoundBook from './pages/BoundBook';
import Inventory from './pages/Inventory';
import Forms4473 from './pages/Forms4473';
import Form4473Editor from './pages/Form4473Editor';

type Page = 'dashboard' | 'contacts' | 'bound-book' | 'inventory' | 'forms-4473' | 'form-4473-editor';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [editingFormId, setEditingFormId] = useState<number | null>(null);

  useEffect(() => {
    const handleNavigate = (e: CustomEvent) => {
      setEditingFormId(e.detail.id);
      setCurrentPage('form-4473-editor');
    };
    
    window.addEventListener('navigate-to-form-editor', handleNavigate as EventListener);
    return () => window.removeEventListener('navigate-to-form-editor', handleNavigate as EventListener);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'contacts':
        return <Contacts />;
      case 'bound-book':
        return <BoundBook />;
      case 'inventory':
        return <Inventory />;
      case 'forms-4473':
        return <Forms4473 />;
      case 'form-4473-editor':
        if (!editingFormId) return <Forms4473 />;
        return <Form4473Editor formId={editingFormId} onClose={() => setCurrentPage('forms-4473')} />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <nav className="sidebar">
        <h1>Praetor</h1>
        <ul>
          <li className={currentPage === 'dashboard' ? 'active' : ''} onClick={() => setCurrentPage('dashboard')}>Dashboard</li>
          <li className={currentPage === 'contacts' ? 'active' : ''} onClick={() => setCurrentPage('contacts')}>Contacts</li>
          <li className={currentPage === 'bound-book' ? 'active' : ''} onClick={() => setCurrentPage('bound-book')}>Bound Book (A&D)</li>
          <li className={currentPage === 'inventory' ? 'active' : ''} onClick={() => setCurrentPage('inventory')}>Current Inventory</li>
          <li className={currentPage === 'forms-4473' ? 'active' : ''} onClick={() => setCurrentPage('forms-4473')}>ATF Forms 4473</li>
        </ul>
      </nav>
      <main className="content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
