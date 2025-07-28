// Core1 Frontend Server — Proxy to Dolphin Backend
const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;
const DOLPHIN_BACKEND = process.env.DOLPHIN_BACKEND || 'http://localhost:8000';

app.use(cors());
app.use(express.json());

// Session management
let sessionCounter = 0;
const sessions = new Map();

function generateSessionId() {
  return `session_${Date.now()}_${++sessionCounter}`;
}

app.post('/api/chat', async (req, res) => {
  const { message, sessionId: providedSessionId } = req.body;
  if (!message) return res.status(400).send({ error: 'Missing message' });

  try {
    // Get or create session ID
    let sessionId = providedSessionId;
    if (!sessionId) {
      sessionId = generateSessionId();
    }

    // Store session context
    if (!sessions.has(sessionId)) {
      sessions.set(sessionId, {
        created: new Date().toISOString(),
        messages: []
      });
    }

    const session = sessions.get(sessionId);
    
    // Add user message to context
    session.messages.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    });

    // Send to Dolphin backend
    const payload = {
      message,
      context: {
        session_history: session.messages.slice(-10), // Last 10 messages for context
        session_id: sessionId
      },
      session_id: sessionId
    };

    const response = await axios.post(`${DOLPHIN_BACKEND}/api/chat`, payload, {
      headers: { 'Content-Type': 'application/json' }
    });

    const aiResponse = response.data;
    
    // Add AI response to session
    session.messages.push({
      role: 'assistant',
      content: aiResponse.response,
      handler: aiResponse.handler,
      timestamp: aiResponse.timestamp
    });

    // Return response in format expected by frontend
    res.send({
      response: aiResponse.response,
      handler: aiResponse.handler,
      reasoning: aiResponse.reasoning,
      metadata: {
        ...aiResponse.metadata,
        session_id: sessionId
      },
      sessionId
    });

  } catch (err) {
    console.error('Dolphin Backend Error:', err.message);
    res.status(500).send({ 
      error: `AI backend request failed: ${err.response?.data?.detail || err.message}` 
    });
  }
});

app.get('/api/models', async (req, res) => {
  try {
    const response = await axios.get(`${DOLPHIN_BACKEND}/api/models`);
    res.send(response.data);
  } catch (err) {
    res.status(500).send({ error: 'Failed to fetch models from Dolphin backend' });
  }
});

app.get('/api/status', async (req, res) => {
  try {
    const response = await axios.get(`${DOLPHIN_BACKEND}/api/status`);
    res.send({
      status: 'running',
      timestamp: new Date().toISOString(),
      dolphin_backend: response.data,
      frontend_server: 'core1-gateway'
    });
  } catch (err) {
    res.status(500).send({ 
      error: 'Dolphin backend not available',
      status: 'degraded',
      timestamp: new Date().toISOString()
    });
  }
});

app.get('/', (req, res) => {
  res.send({
    message: 'Core1 Gateway - Frontend to Dolphin Backend',
    version: '1.0.0',
    status: 'running',
    dolphin_backend: DOLPHIN_BACKEND,
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`[Core1] Frontend Gateway running on port ${PORT}`);
  console.log(`🐬 Dolphin Backend: ${DOLPHIN_BACKEND}`);
  console.log(`📡 Ready to route requests to Dolphin orchestrator`);
});
