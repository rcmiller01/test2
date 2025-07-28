// Core1 Frontend — React + Tailwind + Axios
// Minimal UI to chat with OpenRouter or local models via Node relay

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [model, setModel] = useState('gpt-4');
  const [useCloud, setUseCloud] = useState(true);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');

  // Check backend status on load
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/status');
        setStatus(res.data);
      } catch (err) {
        setError('Backend not available. Please start the server.');
      }
    };
    checkStatus();
  }, []);

  const handleSend = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError('');
    
    const userMessage = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const res = await axios.post('http://localhost:5000/api/chat', {
        prompt,
        model,
        useCloud,
      });
      
      const reply = res.data.choices?.[0]?.message?.content || 'No response.';
      const aiMessage = { role: 'assistant', content: reply };
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = err.response?.data?.error || 'Backend connection failed';
      setError(errorMsg);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ Error: ${errorMsg}` 
      }]);
    } finally {
      setPrompt('');
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
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">💬 Core1 AI Gateway</h1>
          <div className="flex items-center space-x-4">
            {status && (
              <div className="text-sm">
                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                  status.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                }`}></span>
                {status.openrouter_configured ? '🌐 Cloud Ready' : '⚠️ Cloud Not Configured'}
              </div>
            )}
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

        {/* Chat Messages */}
        <div className="bg-gray-800 rounded-lg p-4 h-96 overflow-y-auto mb-4 space-y-3">
          {messages.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              Start a conversation with your AI assistant...
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 ml-8' 
                    : 'bg-gray-700 mr-8'
                }`}
              >
                <div className="font-semibold mb-1">
                  {msg.role === 'user' ? '👤 You' : '🤖 AI'}
                </div>
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            ))
          )}
          {loading && (
            <div className="bg-gray-700 mr-8 p-3 rounded-lg">
              <div className="font-semibold mb-1">🤖 AI</div>
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <textarea
              className="p-3 rounded-lg bg-gray-800 flex-1 resize-none border border-gray-600 focus:border-blue-500 focus:outline-none"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask something... (Press Enter to send, Shift+Enter for new line)"
              rows="2"
            />
            <button
              className={`px-6 py-3 rounded-lg font-semibold ${
                loading 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-500'
              }`}
              onClick={handleSend}
              disabled={loading || !prompt.trim()}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between bg-gray-800 p-4 rounded-lg">
            <div className="flex items-center space-x-6">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useCloud}
                  onChange={(e) => setUseCloud(e.target.checked)}
                  className="w-4 h-4"
                />
                <span>🌐 Use OpenRouter (Cloud)</span>
              </label>

              <div className="flex items-center space-x-2">
                <span>Model:</span>
                <select
                  className="bg-gray-700 p-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                >
                  {useCloud ? (
                    <>
                      <option value="gpt-4">GPT-4</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                      <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                      <option value="meta-llama/llama-2-70b-chat">Llama 2 70B</option>
                    </>
                  ) : (
                    <>
                      <option value="dolphin-mixtral">Dolphin Mixtral</option>
                      <option value="kimik2">Kimi K2</option>
                      <option value="llama2">Llama 2</option>
                      <option value="codellama">Code Llama</option>
                    </>
                  )}
                </select>
              </div>
            </div>

            <div className="text-sm text-gray-400">
              {useCloud ? '☁️ Cloud Models' : '🖥️ Local Models'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
