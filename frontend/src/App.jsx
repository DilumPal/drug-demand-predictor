import { useState } from 'react';
import './index.css';

function App() {
  const [formData, setFormData] = useState({
    daily_sales_avg: 25.2,
    current_stock: 40,
    lead_time_days: 10,
    category: 'Painkiller',
    supplier_tier: 'B'
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const categories = ["Antibiotic", "Painkiller", "Vitamin", "Vaccine", "Antihistamine"];
  const suppliers = ["A", "B", "C", "D"];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: (name === 'category' || name === 'supplier_tier') ? value : Number(value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('API Request failed');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (prob) => {
    if (prob > 0.65) return '#ef4444'; // Danger
    if (prob > 0.3) return '#f59e0b'; // Warning
    return '#10b981'; // Success
  };

  return (
    <div className="dashboard-container">
      <div className="header">
        <h1>Intelligence Hub</h1>
        <p>Real-Time Drug Demand & Stockout Predictor</p>
      </div>

      <div className="grid">
        <div className="glass-panel">
          <h2 className="panel-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
            Inventory Parameters
          </h2>
          
          <form onSubmit={handleSubmit} className="form-grid">
            <div className="input-group">
              <label>Daily Sales Avg</label>
              <input type="number" step="0.1" name="daily_sales_avg" value={formData.daily_sales_avg} onChange={handleChange} required />
            </div>

            <div className="input-group">
              <label>Current Stock (units)</label>
              <input type="number" name="current_stock" value={formData.current_stock} onChange={handleChange} required />
            </div>

            <div className="input-group">
              <label>Lead Time (days)</label>
              <input type="number" name="lead_time_days" value={formData.lead_time_days} onChange={handleChange} required />
            </div>

            <div className="input-group">
              <label>Drug Category</label>
              <select name="category" value={formData.category} onChange={handleChange}>
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div className="input-group full-width">
              <label>Supplier Tier</label>
              <select name="supplier_tier" value={formData.supplier_tier} onChange={handleChange}>
                {suppliers.map(s => <option key={s} value={s}>Tier {s}</option>)}
              </select>
            </div>

            <div className="input-group full-width">
              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? <div className="loader"></div> : 'Analyze Stockout Risk'}
              </button>
            </div>
            
            {error && <div style={{color: 'var(--danger-color)', gridColumn: '1/-1'}}>{error}</div>}
          </form>
        </div>

        <div className="glass-panel results-panel">
          {!result ? (
            <div className="placeholder-result">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              <p>Enter parameters to run the prediction model.</p>
            </div>
          ) : (
            <div className="result-content">
              <h2 className="panel-title" style={{justifyContent: 'center'}}>Risk Analysis</h2>
              
              <div className={`risk-level ${result.out_of_stock_risk ? 'high' : 'low'}`}>
                {result.out_of_stock_risk ? 'HIGH STOCKOUT RISK' : 'HEALTHY INVENTORY'}
              </div>

              <div className="gauge-container">
                <div className="gauge-bg"></div>
                <div 
                  className="gauge-fill" 
                  style={{
                    background: getRiskColor(result.risk_probability),
                    transform: `rotate(${result.risk_probability * 180 - 180}deg)`
                  }}
                ></div>
                <div className="gauge-center">
                  <span className="gauge-percentage">
                    {(result.risk_probability * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="recommendation-card">
                <h4>AI Recommendation</h4>
                <p style={{color: getRiskColor(result.risk_probability)}}>
                  {result.recommendation}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
