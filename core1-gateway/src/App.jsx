// Core1 Frontend — Enhanced React + Tailwind for Dolphin Backend v2.0
// Multi-server AI architecture with personality system, memory management, and analytics

import { useState, useEffect } from 'react';
import axios from 'axios';
import n8nIcon from './assets/n8n.svg';

import EmotionEval from './EmotionEval.jsx';
import AnchorSettingsPanel from './components/settings/AnchorSettingsPanel.jsx';


const API_BASE = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:5000';

export default function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [handlers, setHandlers] = useState([]);
  const [sessionHandlers, setSessionHandlers] = useState([]);
  
  // Enhanced state for new features
  const [personas, setPersonas] = useState([]);
  const [currentPersona, setCurrentPersona] = useState('companion');
  const [analytics, setAnalytics] = useState(null);
  const [memoryStatus, setMemoryStatus] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [mcpStatus, setMcpStatus] = useState(null);
  const [mcpResponse, setMcpResponse] = useState(null);

  // Check backend status and load initial data
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Get system status
        const statusRes = await axios.get(`${API_BASE}/api/status`);
        setStatus(statusRes.data);
        
        // Get available handlers
        const handlersRes = await axios.get(`${API_BASE}/api/handlers`);
        setHandlers(handlersRes.data.handlers);
        
        // Get available personas
        const personasRes = await axios.get(`${API_BASE}/api/personas`);
        setPersonas(Object.entries(personasRes.data.personas));
        setCurrentPersona(personasRes.data.current_persona);
        
        // Get real-time analytics
        const analyticsRes = await axios.get(`${API_BASE}/api/analytics/realtime`);
        setAnalytics(analyticsRes.data);
        
      } catch (err) {
        setError('Backend not available. Please start the Dolphin server.');
      }
    };
    
    initializeApp();
    
    // Set up periodic status updates
    const interval = setInterval(async () => {
      try {
        const analyticsRes = await axios.get(`${API_BASE}/api/analytics/realtime`);
        setAnalytics(analyticsRes.data);
      } catch (err) {
        // Silently handle polling errors
      }
    }, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${import.meta.env.VITE_GATEWAY_URL}/api/mcp/status`);
        setMcpStatus(res.data);
      } catch (err) {
        setMcpStatus({ status: 'unreachable' });
      }
    };
    fetchStatus();
  }, []);
  const handlePersonaChange = async (personaId) => {
    try {
      await axios.post(`${API_BASE}/api/personas/${personaId}`);
      setCurrentPersona(personaId);
      
      // Add system message about persona change
      const systemMessage = {
        role: 'system',
        content: `🎭 Switched to ${personas.find(([id]) => id === personaId)?.[1]?.name || personaId} persona`,
        handler: 'SYSTEM',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
      
    } catch (err) {
      setError('Failed to change persona');
    }
  };

  const handleSend = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setError('');
    
    const userMessage = { 
      role: 'user', 
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const res = await axios.post(`${API_BASE}/api/chat`, {
        message,
        session_id: sessionId,
        persona: currentPersona,
      });
      
      const response = res.data;
      const aiMessage = {
        role: 'assistant',
        content: response.response,
        handler: response.handler,
        reasoning: response.reasoning,
        persona_used: response.persona_used,
        metadata: response.metadata,
        timestamp: response.timestamp
      };

      setMessages(prev => [...prev, aiMessage]);

      setSessionHandlers(prev =>
        prev.includes(aiMessage.handler) ? prev : [...prev, aiMessage.handler]
      );
      
      // Update session ID if not set
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }
      
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = err.response?.data?.error || 'Backend connection failed';
      setError(errorMsg);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ Error: ${errorMsg}`,
        handler: 'ERROR',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setMessage('');
      setLoading(false);
    }
  };

  const clearChat = async () => {
    setMessages([]);
    setError('');
    if (sessionId) {
      try {
        await axios.delete(`${API_BASE}/api/memory/session/${sessionId}`);
        setSessionId(null);
      } catch (err) {
        console.error('Error clearing session:', err);
      }
    }
  };

  const flushMemory = async () => {
    try {
      await axios.post(`${API_BASE}/api/memory/flush`);
      setMessages(prev => [...prev, {
        role: 'system',
        content: '🧠 Short-term memory has been flushed',
        handler: 'SYSTEM',
        timestamp: new Date().toISOString()
      }]);
    } catch (err) {
      setError('Failed to flush memory');
    }
  };

  const exportAnalytics = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/logs/export`);
      alert(`Analytics exported to: ${res.data.export_path}`);
    } catch (err) {
      setError('Failed to export analytics');
    }
  };

  const testReminder = async () => {
    try {
      const res = await axios.post(`${import.meta.env.VITE_GATEWAY_URL}/api/internal/test-mcp`);
      setMcpResponse(res.data);
    } catch (err) {
      setMcpResponse({ error: err.message });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getHandlerIcon = (handler) => {

    const h = (handler || '').toUpperCase();
    const iconMap = {
      'DOLPHIN': '🐬',
      'OPENROUTER': '☁️',
      'KIMI_K2': '📊',
      'SYSTEM': '⚙️',
      'ERROR': '❌'
    };

    if (h === 'N8N') {
      return <img src={n8nIcon} alt="Utility" className="inline-block w-4 h-4 mr-1" />;
    }
    return iconMap[h] || '🤖';
  };

  const getHandlerColor = (handler) => {
    const h = (handler || '').toUpperCase();
    const colorMap = {
      'DOLPHIN': 'bg-blue-600',
      'OPENROUTER': 'bg-green-600',
      'N8N': 'bg-orange-600',
      'KIMI_K2': 'bg-purple-600',
      'SYSTEM': 'bg-gray-600',
      'ERROR': 'bg-red-600'
    };

    return colorMap[h] || 'bg-gray-600';

  };

  const getPersonaIcon = (personaId) => {
    const persona = personas.find(([id]) => id === personaId)?.[1];
    return persona?.icon || '🤖';
  };

  const renderN8nStatus = (msg) => {
    const meta = msg.metadata || {};
    const status = meta.status || meta.workflow_status;
    const successFlag =
      typeof meta.success === 'boolean'
        ? meta.success
        : /success|completed/i.test(status || '');
    if (!status && typeof meta.success !== 'boolean') return null;
    const baseClass = successFlag
      ? 'bg-green-900 text-green-300'
      : 'bg-red-900 text-red-300';
    const text = successFlag
      ? 'Success'
      : status || 'Failed';
    return (
      <span className={`ml-2 px-2 py-1 rounded text-xs ${baseClass}`}>{text}</span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">🐬 Dolphin AI Gateway v2.0</h1>
            <p className="text-gray-400 text-sm">Personality • Memory • Analytics • Multi-server Routing</p>
          </div>
          <div className="flex items-center space-x-4">
            {status && (
              <div className="text-sm flex items-center space-x-2">
                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                  status.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                }`}></span>
                {status.backend_status?.services?.openrouter_configured
                  ? '☁️ Cloud Ready'
                  : '🖥️ Local Only'}
                {status.backend_status?.services?.n8n !== undefined && (
                  <span title="N8n Automation Agent">
                    {status.backend_status.services.n8n ? (
                      <img src={n8nIcon} className="inline w-4 h-4 ml-1" alt="n8n" />
                    ) : (
                      '❌'
                    )}
                  </span>
                )}
              </div>
            )}
            {sessionId && (
              <div className="text-xs text-gray-400">
                Session: {sessionId.slice(-8)}
              </div>
            )}
            {sessionHandlers.length > 0 && (
              <div className="flex space-x-1 text-xs" title="Handlers used this session">
                {sessionHandlers.map((h, i) => (
                  <span key={i}>{getHandlerIcon(h)}</span>
                ))}
              </div>
            )}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="bg-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-600"
            >
              {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
            </button>
          </div>
        </div>

        {/* Advanced Controls */}
        {showAdvanced && (
          <div className="bg-gray-800 rounded-lg p-4 mb-4 space-y-4">
            <h3 className="text-lg font-semibold mb-2">🎛️ Advanced Controls</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Session Management */}
              <div>
                <h4 className="font-medium mb-2">Session</h4>
                <div className="space-y-2">
                  <button onClick={clearChat} className="w-full bg-blue-600 px-3 py-1 rounded text-sm hover:bg-blue-500">
                    Clear Chat
                  </button>
                  <button onClick={flushMemory} className="w-full bg-red-600 px-3 py-1 rounded text-sm hover:bg-red-500">
                    Flush Memory
                  </button>
                </div>
              </div>
              
              {/* Analytics */}
              <div>
                <h4 className="font-medium mb-2">Analytics</h4>
                {analytics && (
                  <div className="text-xs space-y-1">
                    <div>Requests: {analytics.recent_requests}</div>
                    <div>Avg Latency: {analytics.performance?.avg_latency_seconds}s</div>
                    <button onClick={exportAnalytics} className="w-full bg-purple-600 px-3 py-1 rounded text-sm hover:bg-purple-500">
                      Export Data
                    </button>
                  </div>
                )}
              </div>
              
              {/* Memory Status */}
              <div>
                <h4 className="font-medium mb-2">Memory</h4>
                {status?.backend_status?.memory && (
                  <div className="text-xs space-y-1">
                    <div>Sessions: {status.backend_status.memory.short_term.active_sessions}</div>
                    <div>Messages: {status.backend_status.memory.short_term.total_messages}</div>
                    <div>Goals: {status.backend_status.memory.long_term.goals_count}</div>
                  </div>
                )}
              </div>

              {/* Anchor Settings */}
              <AnchorSettingsPanel />
            </div>
          </div>
        )}

        {/* Persona Selection */}
        <div className="bg-gray-800 rounded-lg p-4 mb-4">
          <h3 className="text-sm font-semibold mb-3">🎭 AI Persona</h3>
          <div className="flex flex-wrap gap-2">
            {personas.map(([id, persona]) => (
              <button
                key={id}
                onClick={() => handlePersonaChange(id)}
                className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                  currentPersona === id 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                {persona.icon} {persona.name}
              </button>
            ))}
          </div>
          {personas.find(([id]) => id === currentPersona) && (
            <p className="text-xs text-gray-400 mt-2">
              {personas.find(([id]) => id === currentPersona)[1].description}
            </p>
          )}
        </div>

        {error && (
          <div className="bg-red-900 border border-red-500 text-red-200 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Handler Information */}
        {handlers.length > 0 && (
          <div className="bg-gray-800 rounded-lg p-4 mb-4">
            <h3 className="text-sm font-semibold mb-2">🎯 Available AI Handlers:</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              {handlers.map((handler, idx) => (
                <div key={idx} className="flex items-center space-x-2">
                  <span>{handler.icon}</span>
                  <div>
                    <div className="font-medium">{handler.name}</div>
                    <div className="text-gray-400">{handler.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Emotion Evaluation Example */}
        <EmotionEval
          prompt="How do you comfort someone who's grieving?"
          responseA="I'm here. Not to fix the pain, but to sit with you in it."
          responseB="You shouldn't be sad. Everything happens for a reason."
        />

        {/* Chat Messages */}
        <div className="bg-gray-800 rounded-lg p-4 h-96 overflow-y-auto mb-4 space-y-3">
          {messages.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              <div className="text-2xl mb-2">{getPersonaIcon(currentPersona)}</div>
              <div>Start a conversation with {personas.find(([id]) => id === currentPersona)?.[1]?.name || 'Dolphin AI'}...</div>
              <div className="text-sm mt-2">
                Messages are intelligently routed with personality-aware responses
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                title={
                  msg.handler && msg.handler.toUpperCase() === 'N8N'
                    ? 'Task routed to N8n Automation Agent'
                    : undefined
                }
                className={`p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-blue-600 ml-8'
                    : `${getHandlerColor(msg.handler)} mr-8`
                }`}
              >
                <div className="font-semibold mb-1 flex items-center justify-between">
                  <span className="flex items-center" title={msg.handler && msg.handler.toLowerCase() === 'n8n' ? 'Task routed to N8n Automation Agent' : undefined}>
                    {msg.role === 'user' ? (
                      '👤 You'
                    ) : (
                      <>
                        <span className="mr-1">{getHandlerIcon(msg.handler)}</span>
                        {msg.handler || 'AI'}{msg.persona_used ? ` (${msg.persona_used})` : ''}
                        {msg.handler && msg.handler.toLowerCase() === 'n8n' && (
                          <span className="ml-2 px-2 py-0.5 text-xs rounded bg-black/30">Utility Action</span>
                        )}
                      </>
                    )}
                  </span>
                  {msg.timestamp && (
                    <span className="text-xs opacity-70">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  )}
                </div>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                {msg.reasoning && (
                  <div className="text-xs mt-2 opacity-80 italic">
                    💭 {msg.reasoning}
                  </div>
                )}
                {msg.handler && msg.handler.toUpperCase() === 'N8N' && (
                  <div className="mt-2 flex items-center">
                    <span className="text-xs bg-gray-900 px-2 py-1 rounded" title="Task routed to N8n Automation Agent">Utility Action</span>
                    {renderN8nStatus(msg)}
                  </div>
                )}
                {msg.metadata && showAdvanced && (
                  <div className="text-xs mt-2 opacity-60">
                    📊 Confidence: {msg.metadata.confidence?.toFixed(2)} |
                    Latency: {msg.metadata.latency_seconds}s
                    {msg.metadata.sentiment_trend && ` | Sentiment: ${msg.metadata.sentiment_trend.toFixed(2)}`}
                  </div>
                )}
                {msg.handler && msg.handler.toLowerCase() === 'n8n' && (
                  msg.metadata?.status || msg.metadata?.success !== undefined) && (
                  <div className={`text-xs mt-2 font-semibold ${
                    msg.metadata.status === 'completed' || msg.metadata.success
                      ? 'text-green-300'
                      : 'text-red-300'
                  }`}>
                    {msg.metadata.status
                      ? msg.metadata.status
                      : msg.metadata.success
                      ? 'success'
                      : 'failed'}
                    {msg.metadata.error && ` - ${msg.metadata.error}`}
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="bg-gray-700 mr-8 p-3 rounded-lg">
              <div className="font-semibold mb-1 flex items-center space-x-2">
                <span>{getPersonaIcon(currentPersona)} {personas.find(([id]) => id === currentPersona)?.[1]?.name || 'AI'}</span>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              </div>
              <div className="text-sm opacity-80">
                Analyzing request and routing to best handler...
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <textarea
              className="p-3 rounded-lg bg-gray-800 flex-1 resize-none border border-gray-600 focus:border-blue-500 focus:outline-none"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask anything... ${personas.find(([id]) => id === currentPersona)?.[1]?.name || 'AI'} will route to the best handler`}
              rows="2"
            />
            <button
              className={`px-6 py-3 rounded-lg font-semibold ${
                loading 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-500'
              }`}
              onClick={handleSend}
              disabled={loading || !message.trim()}
            >
              {loading ? '🔄' : 'Send'}
            </button>
          </div>

          {/* System Status */}
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-4">
                <span className="font-medium">🎛️ System Status:</span>
                {status ? (
                  <span className={`${status.status === 'running' ? 'text-green-400' : 'text-red-400'}`}>
                    {status.status === 'running' ? '✅ Online' : '❌ Offline'}
                  </span>
                ) : (
                  <span className="text-yellow-400">🔄 Checking...</span>
                )}
              </div>
              
              <div className="text-gray-400">
                Enhanced AI with personality, memory & analytics
              </div>
            </div>
            
            {status?.backend_status && (
              <div className="mt-2 text-xs text-gray-400 grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  🐬 Dolphin: {status.backend_status.services?.ollama ? '✅' : '❌'}
                </div>
                <div>
                  ☁️ OpenRouter: {status.backend_status.services?.openrouter_configured ? '✅' : '❌'}
                </div>
                <div>
                  🧠 Memory: {status.backend_status.memory ? '✅' : '❌'}
                </div>
                <div>
                  📊 Analytics: {status.backend_status.analytics ? '✅' : '❌'}
                </div>
                <div>
                  ⚙️ N8n: {status.backend_status.services?.n8n ? '✅' : '❌'}
                </div>
              </div>
            )}
          </div>

          <div className="mcp-section">
            <h3>MCP Server Status:</h3>
            <p>{mcpStatus ? mcpStatus.status : 'Loading...'}</p>

            <button onClick={testReminder}>Test Reminder Task</button>

            {mcpResponse && (
              <pre className="mcp-response">
                {JSON.stringify(mcpResponse, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
