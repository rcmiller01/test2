import React, { useState, useEffect } from 'react';
import './QuantDashboard.css';

const QuantDashboard = ({ apiBaseUrl = 'http://localhost:8000' }) => {
  const [history, setHistory] = useState([]);
  const [summary, setSummary] = useState({});
  const [performance, setPerformance] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch quantization history
  const fetchHistory = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/quantization/history?limit=20`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      
      setHistory(data.history || []);
      setSummary(data.summary || {});
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(`Failed to fetch history: ${err.message}`);
    }
  };

  // Fetch performance analytics
  const fetchPerformance = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/quantization/performance`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      
      setPerformance(data);
    } catch (err) {
      console.warn('Performance data unavailable:', err.message);
    }
  };

  // Initial load and auto-refresh
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchHistory(), fetchPerformance()]);
      setLoading(false);
    };

    loadData();
    const interval = setInterval(loadData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getScoreColor = (score) => {
    if (score >= 0.9) return '#10b981'; // Green
    if (score >= 0.8) return '#f59e0b'; // Yellow
    if (score >= 0.6) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 0.9) return 'Excellent';
    if (score >= 0.8) return 'Good';
    if (score >= 0.6) return 'Fair';
    return 'Poor';
  };

  if (loading) {
    return (
      <div className="quant-dashboard loading">
        <div className="loading-spinner">🔄</div>
        <p>Loading quantization data...</p>
      </div>
    );
  }

  return (
    <div className="quant-dashboard">
      <div className="dashboard-header">
        <h2>📊 Quantization Quality Dashboard</h2>
        <div className="last-updated">
          Last updated: {lastUpdated ? formatTime(lastUpdated) : 'Never'}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Performance Summary */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-header">
            <h3>🎯 Total Loops</h3>
          </div>
          <div className="card-value">{summary.total_loops || 0}</div>
        </div>

        <div className="summary-card">
          <div className="card-header">
            <h3>✅ Success Rate</h3>
          </div>
          <div className="card-value">
            {((summary.success_rate || 0) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="summary-card">
          <div className="card-header">
            <h3>💝 Avg Emotion</h3>
          </div>
          <div className="card-value" style={{ color: getScoreColor(summary.avg_emotional_score || 0) }}>
            {(summary.avg_emotional_score || 0).toFixed(3)}
          </div>
        </div>

        <div className="summary-card">
          <div className="card-header">
            <h3>🔤 Avg Quality</h3>
          </div>
          <div className="card-value" style={{ color: getScoreColor(summary.avg_token_quality || 0) }}>
            {(summary.avg_token_quality || 0).toFixed(3)}
          </div>
        </div>
      </div>

      {/* Trend Analysis */}
      {performance.trend_analysis && (
        <div className="trend-section">
          <h3>📈 Performance Trend</h3>
          <div className="trend-card">
            <div className="trend-item">
              <span className="trend-label">Direction:</span>
              <span className={`trend-value trend-${performance.trend_analysis.trend_direction}`}>
                {performance.trend_analysis.trend_direction.toUpperCase()}
                {performance.trend_analysis.percent_change > 0 ? ' ⬆️' : 
                 performance.trend_analysis.percent_change < 0 ? ' ⬇️' : ' ➡️'}
              </span>
            </div>
            <div className="trend-item">
              <span className="trend-label">Change:</span>
              <span className="trend-value">
                {performance.trend_analysis.percent_change?.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Quality Distribution */}
      {performance.quality_distribution && (
        <div className="quality-distribution">
          <h3>🎭 Quality Distribution</h3>
          <div className="quality-bars">
            {Object.entries(performance.quality_distribution).map(([quality, count]) => (
              <div key={quality} className="quality-bar">
                <div className="quality-label">{quality}</div>
                <div className="quality-bar-container">
                  <div 
                    className={`quality-bar-fill quality-${quality}`}
                    style={{ width: `${(count / Math.max(...Object.values(performance.quality_distribution))) * 100}%` }}
                  >
                    {count}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* History Table */}
      <div className="history-section">
        <div className="history-header">
          <h3>📋 Recent Quantization History</h3>
          <button onClick={fetchHistory} className="refresh-button">
            🔄 Refresh
          </button>
        </div>

        {history.length === 0 ? (
          <div className="no-data">
            <p>No quantization history available yet.</p>
            <p>Start a quantization loop to see results here.</p>
          </div>
        ) : (
          <div className="history-table-container">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Loop ID</th>
                  <th>Model Name</th>
                  <th>Format</th>
                  <th>Size (MB)</th>
                  <th>Emotion Score</th>
                  <th>Token Quality</th>
                  <th>Passed</th>
                  <th>Duration</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {history.map((result, index) => (
                  <tr key={result.loop_id || index} className={result.passed_threshold ? 'passed' : 'failed'}>
                    <td className="loop-id">{result.loop_id?.substring(0, 12)}...</td>
                    <td className="model-name">{result.model_name}</td>
                    <td className="quant-format">{result.quant_format}</td>
                    <td className="size">{result.size_mb?.toFixed(1)}</td>
                    <td className="emotion-score">
                      <span 
                        className="score-badge"
                        style={{ backgroundColor: getScoreColor(result.emotional_score) }}
                      >
                        {result.emotional_score?.toFixed(3)}
                      </span>
                      <div className="score-label">{getScoreLabel(result.emotional_score)}</div>
                    </td>
                    <td className="token-quality">
                      <span 
                        className="score-badge"
                        style={{ backgroundColor: getScoreColor(result.token_quality) }}
                      >
                        {result.token_quality?.toFixed(3)}
                      </span>
                    </td>
                    <td className="passed">
                      {result.passed_threshold ? '✅' : '❌'}
                    </td>
                    <td className="duration">
                      {result.duration_seconds ? `${result.duration_seconds.toFixed(1)}s` : 'N/A'}
                    </td>
                    <td className="timestamp">
                      {formatTime(result.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Emotional Score Chart */}
      {history.length > 0 && (
        <div className="chart-section">
          <h3>📈 Emotional Score Over Time</h3>
          <div className="simple-chart">
            {history.map((result, index) => (
              <div 
                key={index}
                className="chart-bar"
                style={{ 
                  height: `${(result.emotional_score || 0) * 100}%`,
                  backgroundColor: getScoreColor(result.emotional_score)
                }}
                title={`${result.loop_id}: ${(result.emotional_score || 0).toFixed(3)}`}
              />
            ))}
          </div>
          <div className="chart-labels">
            <span>Oldest</span>
            <span>Latest</span>
          </div>
        </div>
      )}

      <div className="dashboard-footer">
        <p>💡 Tip: Higher emotional and token quality scores indicate better model performance.</p>
        <p>🎯 Target thresholds: Emotional ≥ 0.82, Token Quality ≥ 0.75</p>
      </div>
    </div>
  );
};

export default QuantDashboard;
