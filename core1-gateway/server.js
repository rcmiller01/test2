// Core1 Frontend Server — Enhanced Proxy to Dolphin Backend v2.0
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;
const DOLPHIN_BACKEND = process.env.DOLPHIN_BACKEND || 'http://localhost:8000';
const ALLOWED_ORIGINS = process.env.ALLOWED_ORIGINS || '*';


app.use(cors({ origin: ALLOWED_ORIGINS.split(',') }));

app.use(express.json());

// Anchor settings router
const anchorRoutes = require('./api/routes/anchor');
app.use('/api/anchor', anchorRoutes);

// Enhanced session management
let sessionCounter = 0;
const sessions = new Map();
const logStream = fs.createWriteStream('./logs/persona_routing.log', { flags: 'a' });

function generateSessionId() {
  return `session_${Date.now()}_${++sessionCounter}`;
}


// Enhanced chat endpoint with personality and memory support
app.post('/api/chat', async (req, res) => {
  const { message, sessionId: providedSessionId, persona } = req.body;
  if (!message) return res.status(400).send({ error: 'Missing message' });

  try {
    // Get or create session ID
    let sessionId = providedSessionId;
    if (!sessionId) {
      sessionId = generateSessionId();
    }

    // Store session context locally
    if (!sessions.has(sessionId)) {
      sessions.set(sessionId, {
        created: new Date().toISOString(),
        messages: [],
        persona: persona || 'companion'
      });
    }

    const session = sessions.get(sessionId);
    
    // Update persona if provided
    if (persona && persona !== session.persona) {
      session.persona = persona;
    }

    // Add user message to local context
    session.messages.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    });

    // Send enhanced payload to Dolphin backend
    const payload = {
      message,
      context: {
        session_history: session.messages.slice(-10), // Last 10 messages for context
        session_id: sessionId,
        local_session_data: {
          message_count: session.messages.length,
          session_duration: new Date() - new Date(session.created)
        }
      },
      session_id: sessionId,
      persona: session.persona
    };

    console.log(`📤 [${session.persona}] Sending to Dolphin Backend: ${message.slice(0, 50)}...`);

    const response = await axios.post(`${DOLPHIN_BACKEND}/api/chat`, payload, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000  // 30 second timeout
    });

    const aiResponse = response.data;
    
    // Add AI response to local session
    session.messages.push({
      role: 'assistant',
      content: aiResponse.response,
      handler: aiResponse.handler,
      persona_used: aiResponse.persona_used,
      timestamp: aiResponse.timestamp
    });

    const logLine = `[${new Date().toISOString()}] [${sessionId}] [Persona: ${aiResponse.persona_used}] [Handler: ${aiResponse.handler}]\n`;
    logStream.write(logLine);

    console.log(`✅ [${aiResponse.handler}] Response received (${aiResponse.persona_used})`);

    // Return enhanced response
    res.send({
      response: aiResponse.response,
      handler: aiResponse.handler,
      reasoning: aiResponse.reasoning,
      persona_used: aiResponse.persona_used,
      metadata: {
        ...aiResponse.metadata,
        session_id: sessionId,
        local_message_count: session.messages.length
      },
      sessionId,
      timestamp: aiResponse.timestamp
    });

  } catch (err) {
    console.error('❌ Dolphin Backend Error:', err.message);
    res.status(500).send({ 
      error: `AI backend request failed: ${err.response?.data?.detail || err.message}`,
      timestamp: new Date().toISOString()
    });
  }
});

// Proxy all enhanced API endpoints
const apiEndpoints = [
  { path: '/api/status', method: 'GET' },
  { path: '/api/handlers', method: 'GET' },
  { path: '/api/personas', method: 'GET' },
  { path: '/api/personas/:id', method: 'POST' },
  { path: '/api/personas/create', method: 'POST' },
  { path: '/api/memory/session/:sessionId', method: 'GET' },
  { path: '/api/memory/longterm', method: 'GET' },
  { path: '/api/memory/longterm/goal', method: 'POST' },
  { path: '/api/memory/flush', method: 'POST' },
  { path: '/api/memory/session/:sessionId', method: 'DELETE' },
  { path: '/api/analytics/realtime', method: 'GET' },
  { path: '/api/analytics/daily', method: 'GET' },
  { path: '/api/analytics/performance', method: 'GET' },
  { path: '/api/logs/search', method: 'GET' },
  { path: '/api/logs/export', method: 'GET' },
  { path: '/api/system/cleanup', method: 'POST' },
  { path: '/api/system/health', method: 'GET' },
  { path: '/api/vote_preference', method: 'POST' }
];

// Create proxy routes
apiEndpoints.forEach(({ path, method }) => {
  app[method.toLowerCase()](path, async (req, res) => {
    try {
      const config = {
        method: method.toLowerCase(),
        url: `${DOLPHIN_BACKEND}${req.originalUrl}`,
        headers: { 'Content-Type': 'application/json' },
        timeout: 15000
      };

      if (['POST', 'PUT', 'PATCH'].includes(method)) {
        config.data = req.body;
      }

      const response = await axios(config);
      res.send(response.data);

    } catch (err) {
      console.error(`❌ Proxy error for ${method} ${path}:`, err.message);
      res.status(err.response?.status || 500).send({
        error: 'Backend request failed',
        details: err.message,
        timestamp: new Date().toISOString()
      });
    }
  });
});

// Local session management
app.get('/api/sessions/local', (req, res) => {
  const sessionList = Array.from(sessions.entries()).map(([id, data]) => ({
    session_id: id,
    created: data.created,
    message_count: data.messages.length,
    current_persona: data.persona,
    last_activity: data.messages[data.messages.length - 1]?.timestamp
  }));
  
  res.send({ 
    sessions: sessionList,
    total_sessions: sessionList.length,
    timestamp: new Date().toISOString()
  });
});

app.delete('/api/sessions/local/:sessionId', (req, res) => {
  const { sessionId } = req.params;
  const session = sessions.get(sessionId);
  const deleted = sessions.delete(sessionId);
  
  res.send({ 
    success: deleted, 
    session_id: sessionId,
    message_count: session?.messages.length || 0,
    message: deleted ? 'Local session cleared' : 'Session not found',
    timestamp: new Date().toISOString()
  });
});

// Enhanced status endpoint
app.get('/api/status', async (req, res) => {
  try {
    const response = await axios.get(`${DOLPHIN_BACKEND}/api/status`, { timeout: 5000 });
    res.send({
      status: 'running',
      timestamp: new Date().toISOString(),
      dolphin_backend: response.data,
      frontend_server: {
        name: 'core1-gateway',
        version: '2.0.0',
        features: ['personality_system', 'memory_management', 'analytics_logging'],
        local_sessions: sessions.size,
        uptime_seconds: process.uptime()
      }
    });
  } catch (err) {
    res.status(500).send({ 
      error: 'Dolphin backend not available',
      status: 'degraded',
      local_sessions: sessions.size,
      timestamp: new Date().toISOString()
    });
  }
});

// Health check
app.get('/health', async (req, res) => {
  try {
    const backendHealth = await axios.get(`${DOLPHIN_BACKEND}/api/system/health`, { timeout: 5000 });
    
    res.send({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      components: {
        frontend_gateway: {
          status: 'healthy',
          local_sessions: sessions.size,
          uptime_seconds: process.uptime()
        },
        dolphin_backend: backendHealth.data
      }
    });
  } catch (err) {
    res.status(503).send({
      status: 'unhealthy', 
      error: err.message,
      local_sessions: sessions.size,
      timestamp: new Date().toISOString()
    });
  }
});

app.get('/', (req, res) => {
  res.send({
    message: 'Core1 Gateway v2.0 - Enhanced Frontend to Dolphin Backend',
    version: '2.0.0',
    status: 'running',
    features: [
      'Personality System Integration',
      'Session Memory Management', 
      'Real-time Analytics Proxy',
      'Enhanced Error Handling',
      'Multi-endpoint API Proxy'
    ],
    dolphin_backend: DOLPHIN_BACKEND,
    local_sessions: sessions.size,
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`🚀 [Core1] Enhanced Frontend Gateway v2.0 running on port ${PORT}`);
  console.log(`🐬 Dolphin Backend: ${DOLPHIN_BACKEND}`);
  console.log(`📡 Features: Personality • Memory • Analytics • Enhanced Routing`);
  console.log(`💫 Ready for next-generation AI orchestration!`);
  
  // Test connection to Dolphin Backend
  axios.get(`${DOLPHIN_BACKEND}/api/status`, { timeout: 5000 })
    .then(() => console.log('✅ Successfully connected to enhanced Dolphin Backend'))
    .catch(err => console.log('⚠️ Could not connect to Dolphin Backend:', err.message));
});
