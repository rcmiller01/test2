// Core1 — OpenRouter Relay + Local Model Router
const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;
const OPENROUTER_API = 'https://openrouter.ai/api/v1/chat/completions';
const LOCAL_MODEL_API = process.env.LOCAL_MODEL_API || 'http://localhost:11434';
const OPENROUTER_KEY = process.env.OPENROUTER_KEY;

app.use(cors());
app.use(express.json());

app.post('/api/chat', async (req, res) => {
  const { prompt, model, useCloud } = req.body;
  if (!prompt) return res.status(400).send({ error: 'Missing prompt' });

  try {
    const payload = {
      model: model || 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      stream: false
    };

    if (useCloud) {
      if (!OPENROUTER_KEY) {
        return res.status(500).send({ error: 'OpenRouter API key not configured' });
      }
      
      const response = await axios.post(OPENROUTER_API, payload, {
        headers: {
          'Authorization': `Bearer ${OPENROUTER_KEY}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'http://localhost:3000',
          'X-Title': 'Core1 Gateway'
        }
      });
      res.send(response.data);
    } else {
      const response = await axios.post(`${LOCAL_MODEL_API}/api/generate`, {
        model: model || 'dolphin-mixtral',
        prompt,
        stream: false
      });
      res.send({ 
        choices: [{ 
          message: { 
            role: 'assistant', 
            content: response.data.response || 'No response from local model' 
          } 
        }] 
      });
    }
  } catch (err) {
    console.error('AI Routing Error:', err.message);
    res.status(500).send({ 
      error: `AI model request failed: ${err.response?.data?.error || err.message}` 
    });
  }
});

app.get('/api/models/cloud', async (req, res) => {
  try {
    if (!OPENROUTER_KEY) {
      return res.status(500).send({ error: 'OpenRouter API key not configured' });
    }
    
    const response = await axios.get('https://openrouter.ai/api/v1/models', {
      headers: { 'Authorization': `Bearer ${OPENROUTER_KEY}` }
    });
    res.send(response.data);
  } catch (err) {
    res.status(500).send({ error: 'Failed to fetch cloud models' });
  }
});

app.get('/api/models/local', async (req, res) => {
  try {
    const response = await axios.get(`${LOCAL_MODEL_API}/api/tags`);
    res.send(response.data);
  } catch (err) {
    res.status(500).send({ error: 'Failed to fetch local models' });
  }
});

app.get('/api/status', (req, res) => {
  res.send({
    status: 'running',
    timestamp: new Date().toISOString(),
    openrouter_configured: !!OPENROUTER_KEY,
    local_api: LOCAL_MODEL_API
  });
});

app.listen(PORT, () => {
  console.log(`[Core1] OpenRouter Gateway running on port ${PORT}`);
  console.log(`OpenRouter configured: ${!!OPENROUTER_KEY}`);
  console.log(`Local model API: ${LOCAL_MODEL_API}`);
});
