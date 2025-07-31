// File: /src/components/settings/AnchorSettingsPanel.jsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './AnchorSettingsPanel.css'; // optional styling

const defaultSettings = {
  weights: {
    persona_continuity: 0.4,
    expression_accuracy: 0.3,
    response_depth: 0.2,
    memory_alignment: 0.1
  },
  signature: 'Emberveil-01',
  locked: false
};

const AnchorSettingsPanel = () => {
  const [settings, setSettings] = useState(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [lastSaved, setLastSaved] = useState(null);

  useEffect(() => {
    axios.get('/api/anchor/settings')
      .then(res => {
        setSettings(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleWeightChange = (key, value) => {
    const newWeights = { ...settings.weights, [key]: parseFloat(value) };
    setSettings(prev => ({ ...prev, weights: newWeights }));
  };

  const handleSave = () => {
    axios.post('/api/anchor/settings', settings)
      .then(() => setLastSaved(new Date().toLocaleString()));
  };

  const totalWeight = Object.values(settings.weights).reduce((a, b) => a + b, 0);

  if (loading) return <div>Loading Anchor AI settings...</div>;

  return (
    <div className="anchor-settings">
      <h2>🧭 Anchor AI Emotional Scoring Settings</h2>

      {Object.entries(settings.weights).map(([key, val]) => (
        <div key={key} className="slider-group">
          <label>{key.replace('_', ' ')}: {val.toFixed(2)}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={val}
            onChange={e => handleWeightChange(key, e.target.value)}
          />
        </div>
      ))}

      <p style={{ color: totalWeight !== 1 ? 'red' : 'green' }}>
        Total Weight: {totalWeight.toFixed(2)} {totalWeight !== 1 && "(should be 1.00)"}
      </p>

      <div className="field">
        <label>Signature:</label>
        <select
          value={settings.signature}
          onChange={e => setSettings(prev => ({ ...prev, signature: e.target.value }))}
        >
          <option>Emberveil-01</option>
          <option>Ashveil-02</option>
          <option>Skylace-03</option>
          <option>Custom...</option>
        </select>
      </div>

      <div className="field">
        <label>Anchor Override Lock:</label>
        <input
          type="checkbox"
          checked={settings.locked}
          onChange={e => setSettings(prev => ({ ...prev, locked: e.target.checked }))}
        />
      </div>

      <button onClick={handleSave} disabled={totalWeight !== 1}>Save Settings</button>
      {lastSaved && <p className="last-saved">Last updated: {lastSaved}</p>}
    </div>
  );
};

export default AnchorSettingsPanel;