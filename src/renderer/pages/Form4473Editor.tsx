import React, { useEffect, useState, ChangeEvent } from 'react';

interface Props {
  formId: number;
  onClose: () => void;
}

const Form4473Editor: React.FC<Props> = ({ formId, onClose }) => {
  const [formData, setFormData] = useState<any>(null);
  const [inventory, setInventory] = useState<any[]>([]);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [formId]);

  const loadData = async () => {
    setLoading(true);
    const form = await window.api.get4473ById(formId);
    setFormData(form);
    const inv = await window.api.getInventory();
    setInventory(inv);
    setLoading(false);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData((prev: any) => ({
      ...prev,
      [name]: type === 'checkbox' ? (checked ? 1 : 0) : value
    }));
  };

  const handleSave = async () => {
    await window.api.update4473(formId, formData);
  };

  const handleAddFirearm = async (firearmId: number) => {
    await window.api.addFirearmTo4473(formId, firearmId);
    loadData();
  };

  const handleComplete = async () => {
    if (confirm('Are you sure you want to complete this form? This will mark the firearms as disposed.')) {
      await handleSave();
      await window.api.complete4473(formId);
      onClose();
    }
  };

  if (loading || !formData) return <div className="loading-state">Loading Form Data...</div>;

  return (
    <div className="form-editor-container">
      <header className="page-header">
        <div>
           <h2>Editing 4473 #{formId} <span className={`badge ${formData.status === 'completed' ? 'completed' : 'draft'}`}>{formData.status}</span></h2>
        </div>
        <div className="page-actions">
           <button className="secondary" onClick={onClose}>Back to List</button>
        </div>
      </header>

      {/* Wizard Steps */}
      <div className="wizard-steps">
        <div className={`step ${step === 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`} onClick={() => setStep(1)}>
           <div className="step-circle">1</div>
           <div className="step-label">Firearms</div>
        </div>
        <div className="step-line"></div>
        <div className={`step ${step === 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`} onClick={() => setStep(2)}>
           <div className="step-circle">2</div>
           <div className="step-label">Buyer Info</div>
        </div>
        <div className="step-line"></div>
        <div className={`step ${step === 3 ? 'active' : ''} ${step > 3 ? 'completed' : ''}`} onClick={() => setStep(3)}>
           <div className="step-circle">3</div>
           <div className="step-label">Questionnaire</div>
        </div>
        <div className="step-line"></div>
        <div className={`step ${step === 4 ? 'active' : ''} ${step > 4 ? 'completed' : ''}`} onClick={() => setStep(4)}>
           <div className="step-circle">4</div>
           <div className="step-label">Review</div>
        </div>
      </div>

      <div className="card wizard-content">
        {step === 1 && (
          <div className="step-content">
            <h3>Section A: Firearms</h3>
            <div className="table-container" style={{ marginBottom: 'var(--spacing-lg)' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Manufacturer</th>
                    <th>Model</th>
                    <th>Serial</th>
                    <th>Type</th>
                    <th>Caliber</th>
                  </tr>
                </thead>
                <tbody>
                  {formData.items && formData.items.length > 0 ? (
                    formData.items.map((item: any) => (
                      <tr key={item.id}>
                        <td>{item.manufacturer}</td>
                        <td>{item.model}</td>
                        <td>{item.serial_number}</td>
                        <td>{item.type}</td>
                        <td>{item.caliber}</td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan={5} style={{ textAlign: 'center', padding: '1rem' }}>No firearms attached yet.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {formData.status === 'draft' && (
              <div className="inventory-selector">
                <h4>Select from Inventory</h4>
                <div className="inventory-list">
                  {inventory.filter(i => !formData.items?.some((fi: any) => fi.id === i.id)).map(item => (
                    <div key={item.id} className="inventory-item">
                      <div className="item-details">
                        <span className="item-name">{item.manufacturer} {item.model}</span>
                        <span className="item-serial">{item.serial_number}</span>
                      </div>
                      <button className="secondary small" onClick={() => handleAddFirearm(item.id)}>Add</button>
                    </div>
                  ))}
                  {inventory.length === 0 && <p>No inventory available.</p>}
                </div>
              </div>
            )}
          </div>
        )}

        {step === 2 && (
          <div className="step-content form-grid-layout">
            <h3>Section B: Transferee Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input name="transferee_first_name" value={formData.transferee_first_name || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>Middle Name</label>
                <input name="transferee_middle_name" value={formData.transferee_middle_name || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input name="transferee_last_name" value={formData.transferee_last_name || ''} onChange={handleInputChange} />
              </div>
            </div>
            
            <div className="form-group full-width">
              <label>Current Residence Address (No PO Box)</label>
              <input name="transferee_address" value={formData.transferee_address || ''} onChange={handleInputChange} />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>City</label>
                <input name="transferee_city" value={formData.transferee_city || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>State</label>
                <input name="transferee_state" value={formData.transferee_state || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>Zip Code</label>
                <input name="transferee_zip" value={formData.transferee_zip || ''} onChange={handleInputChange} />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>County</label>
                <input name="transferee_county" value={formData.transferee_county || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>Date of Birth</label>
                <input type="date" name="transferee_dob" value={formData.transferee_dob || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>Place of Birth</label>
                <input name="transferee_birth_place" value={formData.transferee_birth_place || ''} onChange={handleInputChange} />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="step-content">
            <h3>Section B: Questionnaire (11.a - 11.e)</h3>
            <div className="questionnaire">
              <div className="question-row">
                <label>11.a. Are you the actual transferee/buyer of the firearm(s)?</label>
                <input type="checkbox" name="q_11_a" checked={!!formData.q_11_a} onChange={handleInputChange} />
              </div>
              <div className="question-row">
                <label>11.b. Are you under indictment or information in any court for a felony?</label>
                <input type="checkbox" name="q_11_b" checked={!!formData.q_11_b} onChange={handleInputChange} />
              </div>
              <div className="question-row">
                <label>11.c. Have you ever been convicted in any court of a felony?</label>
                <input type="checkbox" name="q_11_c" checked={!!formData.q_11_c} onChange={handleInputChange} />
              </div>
              <div className="question-row">
                <label>11.d. Are you a fugitive from justice?</label>
                <input type="checkbox" name="q_11_d" checked={!!formData.q_11_d} onChange={handleInputChange} />
              </div>
              <div className="question-row">
                <label>11.e. Are you an unlawful user of, or addicted to, marijuana or any depressant, stimulant, narcotic drug, or any other controlled substance?</label>
                <input type="checkbox" name="q_11_e" checked={!!formData.q_11_e} onChange={handleInputChange} />
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="step-content review-step">
            <h3>Review & Complete</h3>
            <p className="instruction-text">Please review all information below before completing the transaction. Once completed, the attached firearms will be automatically removed from your inventory and logged in the disposition record.</p>
            
            <div className="review-summary">
              <div className="summary-item">
                <span className="label">Transferee:</span>
                <span className="value">{formData.transferee_first_name} {formData.transferee_last_name}</span>
              </div>
              <div className="summary-item">
                <span className="label">Total Items:</span>
                <span className="value">{formData.items?.length || 0}</span>
              </div>
              <div className="summary-item">
                 <span className="label">Status:</span>
                 <span className="badge draft">{formData.status}</span>
              </div>
            </div>
            
            <div className="review-actions">
              <button className="secondary" onClick={handleSave}>Save Draft</button>
              {formData.status === 'draft' && (
                <button className="primary" onClick={handleComplete}>Complete Transaction</button>
              )}
            </div>
          </div>
        )}
      </div>
      
      <div className="wizard-navigation">
        <button className="secondary" disabled={step === 1} onClick={() => setStep(step - 1)}>Previous</button>
        <button className="primary" disabled={step === 4} onClick={() => setStep(step + 1)}>Next</button>
      </div>

      <style>{`
        .wizard-steps {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--spacing-xl);
          padding: 0 var(--spacing-xl);
        }
        
        .step {
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;
          opacity: 0.6;
          transition: opacity 0.2s;
          position: relative;
          z-index: 2;
        }
        
        .step.active, .step.completed {
          opacity: 1;
        }
        
        .step-circle {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background-color: var(--color-background);
          border: 2px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          margin-bottom: var(--spacing-xs);
          transition: all 0.2s;
        }
        
        .step.active .step-circle {
          background-color: var(--color-accent);
          color: white;
          border-color: var(--color-accent);
        }
        
        .step.completed .step-circle {
          background-color: var(--color-success);
          color: white;
          border-color: var(--color-success);
        }
        
        .step-label {
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .step-line {
          flex: 1;
          height: 2px;
          background-color: var(--color-border);
          margin: 0 var(--spacing-sm);
          margin-bottom: 20px; /* Align with circle center roughly */
        }
        
        .wizard-content {
          min-height: 400px;
        }
        
        .wizard-navigation {
          display: flex;
          justify-content: space-between;
          margin-top: var(--spacing-lg);
        }
        
        /* Step 1 Styles */
        .inventory-selector {
           margin-top: var(--spacing-lg);
           border-top: 1px solid var(--color-border);
           padding-top: var(--spacing-md);
        }
        
        .inventory-list {
           display: grid;
           grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
           gap: var(--spacing-md);
           margin-top: var(--spacing-md);
        }
        
        .inventory-item {
           border: 1px solid var(--color-border);
           padding: var(--spacing-sm) var(--spacing-md);
           border-radius: var(--radius-sm);
           display: flex;
           justify-content: space-between;
           align-items: center;
           background-color: #f8fafc;
        }
        
        .inventory-item:hover {
           background-color: white;
           box-shadow: var(--shadow-sm);
        }
        
        .item-details {
           display: flex;
           flex-direction: column;
        }
        
        .item-name {
           font-weight: 500;
           font-size: 0.9rem;
        }
        
        .item-serial {
           font-size: 0.75rem;
           color: var(--color-text-secondary);
        }
        
        /* Step 2 Grid */
        .form-grid-layout {
           display: flex;
           flex-direction: column;
           gap: var(--spacing-md);
        }
        
        .form-row {
           display: grid;
           grid-template-columns: repeat(3, 1fr);
           gap: var(--spacing-md);
        }
        
        .full-width {
           width: 100%;
        }
        
        .form-group {
           display: flex;
           flex-direction: column;
           gap: 4px;
        }
        
        .form-group label {
           font-size: 0.8rem;
           font-weight: 500;
           color: var(--color-text-secondary);
        }
        
        /* Step 3 Questionnaire */
        .questionnaire {
           display: flex;
           flex-direction: column;
           gap: 0;
        }
        
        .question-row {
           display: flex;
           justify-content: space-between;
           align-items: center;
           padding: var(--spacing-md);
           border-bottom: 1px solid var(--color-border);
        }
        
        .question-row:last-child {
           border-bottom: none;
        }
        
        .question-row:hover {
           background-color: #f8fafc;
        }
        
        .question-row label {
           flex: 1;
           font-size: 0.9rem;
           padding-right: var(--spacing-lg);
        }
        
        .question-row input[type="checkbox"] {
           width: 20px;
           height: 20px;
        }
        
        /* Step 4 Review */
        .instruction-text {
           font-size: 1rem;
           color: var(--color-text-secondary);
           margin-bottom: var(--spacing-lg);
        }
        
        .review-summary {
           background-color: #f8fafc;
           padding: var(--spacing-lg);
           border-radius: var(--radius-md);
           border: 1px solid var(--color-border);
           margin-bottom: var(--spacing-lg);
        }
        
        .summary-item {
           display: flex;
           margin-bottom: var(--spacing-sm);
           font-size: 1.1rem;
        }
        
        .summary-item .label {
           width: 150px;
           color: var(--color-text-secondary);
        }
        
        .summary-item .value {
           font-weight: 600;
        }
        
        .review-actions {
           display: flex;
           gap: var(--spacing-md);
           justify-content: center;
        }
        
        button.small {
           padding: 2px 8px;
           font-size: 0.75rem;
        }
      `}</style>
    </div>
  );
};

export default Form4473Editor;
