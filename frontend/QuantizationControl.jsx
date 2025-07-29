import React, { useState, useEffect } from 'react';
import './QuantizationControl.css';

const QuantizationControl = ({ apiBaseUrl = 'http://localhost:8000' }) => {
  const [status, setStatus] = useState({
    quantization_running: false,
    bootloader_running: false,
    system_metrics: {},
    integration_status: 'unknown',
    last_log_entries: [],
    error: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch current status
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/quantization/status`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setStatus(data);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(`Failed to fetch status: ${err.message}`);
    }
  };

  // Start quantization loop
  const startQuantization = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/quantization/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      
      // Show success message
      setError(null);
      
      // Refresh status after a delay
      setTimeout(fetchStatus, 2000);
      
    } catch (err) {
      setError(`Failed to start quantization: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Stop quantization loop
  const stopQuantization = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/quantization/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      
      setError(null);
      
      // Refresh status after a delay
      setTimeout(fetchStatus, 2000);
      
    } catch (err) {
      setError(`Failed to stop quantization: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh status every 30 seconds
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp).toLocaleTimeString();
  };

  const getStatusColor = () => {
    if (status.quantization_running) return '#4ade80'; // green
    if (status.bootloader_running) return '#fbbf24'; // yellow
    return '#ef4444'; // red
  };

  const getStatusText = () => {
    if (status.quantization_running) return 'Running';
    if (status.bootloader_running) return 'Standby';
    return 'Stopped';
  };

  return (
    <div className="quantization-control">
      <div className="header">
        <h2>Quantization Loop Control</h2>
        <div className="status-indicator" style={{ backgroundColor: getStatusColor() }}>
          {getStatusText()}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="control-panel">
        <div className="status-grid">
          <div className="status-item">
            <span className="label">Quantization Running:</span>
            <span className={`value ${status.quantization_running ? 'active' : 'inactive'}`}>
              {status.quantization_running ? '✅ Yes' : '❌ No'}
            </span>
          </div>
          
          <div className="status-item">
            <span className="label">Bootloader Running:</span>
            <span className={`value ${status.bootloader_running ? 'active' : 'inactive'}`}>
              {status.bootloader_running ? '✅ Yes' : '❌ No'}
            </span>
          </div>
          
          <div className="status-item">
            <span className="label">Integration Status:</span>
            <span className={`value ${status.integration_status === 'available' ? 'active' : 'inactive'}`}>
              {status.integration_status || 'Unknown'}
            </span>
          </div>
          
          <div className="status-item">
            <span className="label">Last Updated:</span>
            <span className="value">{formatTime(lastUpdated)}</span>
          </div>
        </div>

        <div className="action-buttons">
          <button 
            onClick={startQuantization}
            disabled={loading || status.quantization_running}
            className="btn btn-primary"
          >
            {loading ? '⏳ Starting...' : '▶️ Start Quantization'}
          </button>
          
          <button 
            onClick={stopQuantization}
            disabled={loading || !status.quantization_running}
            className="btn btn-secondary"
          >
            {loading ? '⏳ Stopping...' : '⏹️ Stop Quantization'}
          </button>
          
          <button 
            onClick={fetchStatus}
            disabled={loading}
            className="btn btn-outline"
          >
            🔄 Refresh Status
          </button>
        </div>
      </div>

      {/* System Metrics */}
      {status.system_metrics && Object.keys(status.system_metrics).length > 0 && (
        <div className="system-metrics">
          <h3>System Metrics</h3>
          <div className="metrics-grid">
            {Object.entries(status.system_metrics).map(([key, value]) => (
              <div key={key} className="metric-item">
                <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                <span className="metric-value">
                  {typeof value === 'number' ? value.toFixed(2) : value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Log Entries */}
      {status.last_log_entries && status.last_log_entries.length > 0 && (
        <div className="log-entries">
          <h3>Recent Log Entries</h3>
          <div className="log-container">
            {status.last_log_entries.map((entry, index) => (
              <div key={index} className="log-entry">
                {entry}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="footer">
        <span className="help-text">
          💡 Tip: The quantization loop automatically manages emotional processing. 
          Manual control is available for testing and troubleshooting.
        </span>
      </div>
    </div>
  );
};

export default QuantizationControl;
