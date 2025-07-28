// Core1 Frontend — React + Tailwind for Dolphin Backend
// Multi-server AI architecture with intelligent routing

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [handlers, setHandlers] = useState([]);

  // Check backend status on load
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/status');
        setStatus(res.data);
        
        // Get available handlers
        const handlersRes = await axios.get('http://localhost:5000/api/handlers');
        setHandlers(handlersRes.data.handlers);
        
      } catch (err) {
        setError('Backend not available. Please start the servers.');
      }
    };
    checkStatus();
  }, []);

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
      const res = await axios.post('http://localhost:5000/api/chat', {
        message,
        sessionId,
      });
      
      const response = res.data;
      const aiMessage = { 
        role: 'assistant', 
        content: response.response,
        handler: response.handler,
        reasoning: response.reasoning,
        timestamp: response.metadata?.timestamp || new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Update session ID if not set
      if (!sessionId && response.sessionId) {
        setSessionId(response.sessionId);
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

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
    if (sessionId) {
      axios.delete(`http://localhost:5000/api/sessions/${sessionId}`)
        .catch(err => console.error('Error clearing session:', err));
      setSessionId(null);
    }
  };

  const newSession = () => {
    clearChat();
    setSessionId(null);
  };

  const getHandlerIcon = (handler) => {
    switch(handler) {
      case 'DOLPHIN': return '🐬';
      case 'OPENROUTER': return '☁️';
      case 'N8N': return '🔧';
      case 'KIMI_K2': return '📊';
      case 'ERROR': return '❌';
      default: return '🤖';
    }
  };

  const getHandlerColor = (handler) => {
    switch(handler) {
      case 'DOLPHIN': return 'bg-blue-600';
      case 'OPENROUTER': return 'bg-green-600';
      case 'N8N': return 'bg-orange-600';
      case 'KIMI_K2': return 'bg-purple-600';
      case 'ERROR': return 'bg-red-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">🐬 Dolphin AI Gateway</h1>
            <p className="text-gray-400 text-sm">Multi-server intelligent routing</p>
          </div>
          <div className="flex items-center space-x-4">
            {status && (
              <div className="text-sm">
                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                  status.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                }`}></span>
                {status.backend_status?.services?.openrouter_configured 
                  ? '☁️ Cloud Ready' 
                  : '🖥️ Local Only'
                }
              </div>
            )}
            {sessionId && (
              <div className="text-xs text-gray-400">
                Session: {sessionId.slice(-8)}
              </div>
            )}
            <button
              onClick={newSession}
              className="bg-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-600"
            >
              New Session
            </button>
            <button
              onClick={clearChat}
              className="bg-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-600"
            >
              Clear Chat
            </button>
          </div>
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
                  <span>{getHandlerIcon(handler.name)}</span>
                  <div>
                    <div className="font-medium">{handler.name}</div>
                    <div className="text-gray-400">{handler.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Chat Messages */}
        <div className="bg-gray-800 rounded-lg p-4 h-96 overflow-y-auto mb-4 space-y-3">
          {messages.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              <div className="text-2xl mb-2">🐬</div>
              <div>Start a conversation with Dolphin AI...</div>
              <div className="text-sm mt-2">
                Messages are intelligently routed to the best AI handler
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 ml-8' 
                    : `${getHandlerColor(msg.handler)} mr-8`
                }`}
              >
                <div className="font-semibold mb-1 flex items-center justify-between">
                  <span>
                    {msg.role === 'user' ? '👤 You' : `${getHandlerIcon(msg.handler)} ${msg.handler || 'AI'}`}
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
              </div>
            ))
          )}
          {loading && (
            <div className="bg-gray-700 mr-8 p-3 rounded-lg">
              <div className="font-semibold mb-1 flex items-center space-x-2">
                <span>🐬 Dolphin</span>
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
              placeholder="Ask anything... Dolphin will route to the best AI handler"
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
                Multi-server AI with intelligent routing
              </div>
            </div>
            
            {status?.backend_status && (
              <div className="mt-2 text-xs text-gray-400 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  🐬 Dolphin: {status.backend_status.services?.ollama ? '✅' : '❌'}
                </div>
                <div>
                  ☁️ OpenRouter: {status.backend_status.services?.openrouter_configured ? '✅' : '❌'}
                </div>
                <div>
                  🔧 n8n: {status.backend_status.services?.n8n ? '✅' : '❌'}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
