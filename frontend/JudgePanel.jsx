import React, { useState, useEffect } from 'react';
import './JudgePanel.css';

const JudgePanel = ({ apiBaseUrl = 'http://localhost:8000' }) => {
  const [currentBaseline, setCurrentBaseline] = useState(null);
  const [replacementHistory, setReplacementHistory] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [candidatePath, setCandidatePath] = useState('');
  const [humanVote, setHumanVote] = useState(null);

  // Fetch current baseline model
  const fetchBaseline = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/model/current`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setCurrentBaseline(data);
    } catch (err) {
      setError(`Failed to fetch baseline: ${err.message}`);
    }
  };

  // Fetch replacement history
  const fetchHistory = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/model/history`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setReplacementHistory(data.replacements || []);
    } catch (err) {
      console.warn('Failed to fetch replacement history:', err.message);
    }
  };

  // Compare models
  const compareModels = async (candidatePath, baselinePath = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBaseUrl}/api/model/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_path: candidatePath,
          baseline_path: baselinePath
        })
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setComparisonResult(data.comparison);
    } catch (err) {
      setError(`Comparison failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Manual replacement
  const replaceModel = async (newModelPath, forceReplace = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBaseUrl}/api/model/replace`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          new_model_path: newModelPath,
          force_replace: forceReplace
        })
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Model replaced successfully!');
        fetchBaseline();
        fetchHistory();
        setComparisonResult(null);
        setCandidatePath('');
      } else {
        setError(data.message || 'Replacement failed');
      }
    } catch (err) {
      setError(`Replacement failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBaseline();
    fetchHistory();
    const interval = setInterval(() => {
      fetchBaseline();
      fetchHistory();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getGainColor = (gain) => {
    if (gain > 0.05) return '#10b981'; // Green
    if (gain > 0.02) return '#f59e0b'; // Yellow
    if (gain > -0.02) return '#6b7280'; // Gray
    return '#ef4444'; // Red
  };

  const getGainLabel = (gain) => {
    if (gain > 0.05) return 'Significant Improvement';
    if (gain > 0.02) return 'Moderate Improvement';
    if (gain > -0.02) return 'Minimal Change';
    return 'Degradation';
  };

  return (
    <div className="judge-panel">
      <div className="panel-header">
        <h2>🧪 Model Quality Judge Panel</h2>
        <p>Compare and evaluate model replacements with human feedback integration</p>
      </div>

      {/* Current Baseline Section */}
      <div className="baseline-section">
        <h3>📊 Current Baseline Model</h3>
        {currentBaseline ? (
          <div className="baseline-info">
            <div className="baseline-card">
              <div className="model-name">
                {currentBaseline.baseline_model || 'No baseline set'}
              </div>
              <div className="model-details">
                <div className="detail-item">
                  <span className="label">Path:</span>
                  <span className="value">{currentBaseline.baseline_path || 'N/A'}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Size:</span>
                  <span className="value">
                    {currentBaseline.model_info?.size_mb?.toFixed(1) || 'Unknown'} MB
                  </span>
                </div>
                <div className="detail-item">
                  <span className="label">Format:</span>
                  <span className="value">{currentBaseline.model_info?.format || 'Unknown'}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Last Updated:</span>
                  <span className="value">
                    {currentBaseline.last_updated !== 'never' 
                      ? formatTime(currentBaseline.last_updated) 
                      : 'Never'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="label">Status:</span>
                  <span className={`status ${currentBaseline.exists ? 'active' : 'missing'}`}>
                    {currentBaseline.exists ? '✅ Active' : '❌ Missing'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="loading-state">Loading baseline information...</div>
        )}
      </div>

      {/* Model Comparison Section */}
      <div className="comparison-section">
        <h3>⚖️ Model Comparison Tool</h3>
        <div className="comparison-controls">
          <div className="input-group">
            <label htmlFor="candidate-path">Candidate Model Path:</label>
            <input
              id="candidate-path"
              type="text"
              value={candidatePath}
              onChange={(e) => setCandidatePath(e.target.value)}
              placeholder="Enter path to candidate model..."
              className="path-input"
            />
          </div>
          <div className="button-group">
            <button 
              onClick={() => compareModels(candidatePath)}
              disabled={!candidatePath || loading}
              className="compare-button"
            >
              {loading ? '🔄 Comparing...' : '🔍 Compare Models'}
            </button>
          </div>
        </div>

        {/* Comparison Results */}
        {comparisonResult && (
          <div className="comparison-results">
            <h4>📈 Comparison Results</h4>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-label">Emotionality Gain</div>
                <div 
                  className="metric-value"
                  style={{ color: getGainColor(comparisonResult.emotionality_gain) }}
                >
                  {(comparisonResult.emotionality_gain * 100).toFixed(1)}%
                </div>
                <div className="metric-description">
                  {getGainLabel(comparisonResult.emotionality_gain)}
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Fluency Gain</div>
                <div 
                  className="metric-value"
                  style={{ color: getGainColor(comparisonResult.fluency_gain) }}
                >
                  {(comparisonResult.fluency_gain * 100).toFixed(1)}%
                </div>
                <div className="metric-description">
                  {getGainLabel(comparisonResult.fluency_gain)}
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Size Reduction</div>
                <div 
                  className="metric-value"
                  style={{ color: getGainColor(comparisonResult.size_reduction) }}
                >
                  {(comparisonResult.size_reduction * 100).toFixed(1)}%
                </div>
                <div className="metric-description">
                  {comparisonResult.size_reduction > 0 ? 'Smaller Model' : 'Larger Model'}
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Speed Improvement</div>
                <div 
                  className="metric-value"
                  style={{ color: getGainColor(comparisonResult.speed_improvement) }}
                >
                  {(comparisonResult.speed_improvement * 100).toFixed(1)}%
                </div>
                <div className="metric-description">
                  {comparisonResult.speed_improvement > 0 ? 'Faster Response' : 'Slower Response'}
                </div>
              </div>
            </div>

            <div className="recommendation-section">
              <div className={`recommendation ${comparisonResult.replacement_recommended ? 'positive' : 'negative'}`}>
                <div className="recommendation-icon">
                  {comparisonResult.replacement_recommended ? '✅' : '❌'}
                </div>
                <div className="recommendation-text">
                  <strong>
                    {comparisonResult.replacement_recommended 
                      ? 'Replacement Recommended' 
                      : 'Replacement Not Recommended'}
                  </strong>
                  <div className="confidence">
                    Confidence: {(comparisonResult.confidence_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Human Feedback Section */}
            <div className="human-feedback">
              <h5>🧑‍⚖️ Human Override (Optional)</h5>
              <p>Which model felt more emotionally resonant in your testing?</p>
              <div className="vote-buttons">
                <button 
                  className={`vote-button ${humanVote === 'candidate' ? 'selected' : ''}`}
                  onClick={() => setHumanVote('candidate')}
                >
                  Candidate Model (New)
                </button>
                <button 
                  className={`vote-button ${humanVote === 'baseline' ? 'selected' : ''}`}
                  onClick={() => setHumanVote('baseline')}
                >
                  Baseline Model (Current)
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
              {comparisonResult.replacement_recommended && (
                <button 
                  onClick={() => replaceModel(candidatePath)}
                  className="replace-button recommended"
                  disabled={loading}
                >
                  🎉 Accept & Replace Model
                </button>
              )}
              <button 
                onClick={() => replaceModel(candidatePath, true)}
                className="replace-button force"
                disabled={loading}
              >
                ⚡ Force Replace (Override Quality Check)
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Replacement History */}
      <div className="history-section">
        <h3>📜 Replacement History</h3>
        {replacementHistory.length > 0 ? (
          <div className="history-list">
            {replacementHistory.slice(-5).reverse().map((replacement, index) => (
              <div key={index} className="history-item">
                <div className="history-header">
                  <span className="timestamp">{formatTime(replacement.timestamp)}</span>
                  <span className="loop-id">Loop: {replacement.loop_id}</span>
                </div>
                <div className="history-details">
                  <div className="model-change">
                    <span className="old-model">{replacement.old_baseline.name}</span>
                    <span className="arrow">→</span>
                    <span className="new-model">{replacement.new_model.name}</span>
                  </div>
                  <div className="quality-gains">
                    <span className="gain">
                      Emotion: {(replacement.quality_gains.emotionality * 100).toFixed(1)}%
                    </span>
                    <span className="gain">
                      Fluency: {(replacement.quality_gains.fluency * 100).toFixed(1)}%
                    </span>
                    <span className="gain">
                      Confidence: {(replacement.quality_gains.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-history">
            <p>No model replacements have occurred yet.</p>
            <p>Successful quantization loops will trigger automatic quality evaluation.</p>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
    </div>
  );
};

export default JudgePanel;
