import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:5000';

/**
 * AnchorSettingsPanel - Configure Anchor AI emotional evaluation weights.
 */
export default function AnchorSettingsPanel() {
  const [settings, setSettings] = useState(null);
  const [warning, setWarning] = useState('');

  // Fetch settings on mount
  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/anchor/settings`);
        setSettings(res.data);
      } catch (err) {
        setWarning('Failed to load settings');
      }
    };
    load();
  }, []);

  // Save settings whenever they change (debounced)
  useEffect(() => {
    if (!settings) return;
    const timeout = setTimeout(async () => {
      try {
        await axios.post(`${API_BASE}/api/anchor/settings`, settings);
      } catch (err) {
        setWarning('Failed to save settings');
      }
    }, 500);
    return () => clearTimeout(timeout);
  }, [settings]);

  const updateWeight = (key, value) => {
    const newSettings = {
      ...settings,
      weights: { ...settings.weights, [key]: value }
    };
    const sum =
      newSettings.weights.persona_continuity +
      newSettings.weights.expression_accuracy +
      newSettings.weights.response_depth +
      newSettings.weights.memory_alignment;
    setWarning(Math.abs(sum - 1) > 0.01 ? 'Weights should sum to 1.0' : '');
    setSettings(newSettings);
  };

  if (!settings) {
    return <div className="text-sm">Loading anchor settings...</div>;
  }

  return (
    <div className="space-y-4 bg-gray-800 p-4 rounded-lg">
      <h4 className="font-medium">⚓ Anchor Settings</h4>

      <div className="space-y-3">
        {Object.entries(settings.weights).map(([key, val]) => (
          <div key={key} className="text-sm">
            <label className="block mb-1 capitalize">
              {key.replace('_', ' ')}: {val.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={val}
              onChange={e => updateWeight(key, parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        ))}
      </div>

      <div className="text-sm">
        <label className="block mb-1">Signature</label>
        <input
          type="text"
          value={settings.signature}
          onChange={e => setSettings({ ...settings, signature: e.target.value })}
          className="w-full p-1 rounded bg-gray-700"
        />
      </div>

      <div className="flex items-center space-x-2 text-sm">
        <input
          id="locked"
          type="checkbox"
          checked={settings.locked}
          onChange={e => setSettings({ ...settings, locked: e.target.checked })}
        />
        <label htmlFor="locked">Anchor Override Lock</label>
      </div>

      {warning && <div className="text-red-400 text-xs">{warning}</div>}

      {settings.last_updated && (
        <div className="text-xs text-gray-400">
          Last updated: {new Date(settings.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
}
