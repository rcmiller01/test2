const express = require('express');
const fs = require('fs');
const path = require('path');

const router = express.Router();
const settingsPath = path.join(__dirname, '../../config/anchor_settings.json');

// Default fallback config
const defaultSettings = {
  weights: {
    persona_continuity: 0.4,
    expression_accuracy: 0.3,
    response_depth: 0.2,
    memory_alignment: 0.1
  },
  signature: 'Emberveil-01',
  locked: false
};

// Load settings from file or use defaults
function loadSettings() {
  try {
    if (fs.existsSync(settingsPath)) {
      const data = fs.readFileSync(settingsPath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error('Failed to load Anchor settings:', err);
  }
  return defaultSettings;
}

// Save settings to file
function saveSettings(settings) {
  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
}

// GET /api/anchor/settings
router.get('/settings', (req, res) => {
  const settings = loadSettings();
  res.json(settings);
});

// POST /api/anchor/settings
router.post('/settings', (req, res) => {
  const updated = req.body;
  if (!updated || !updated.weights) {
    return res.status(400).json({ error: 'Invalid settings payload' });
  }
  saveSettings(updated);
  res.json({ success: true });
});

module.exports = router;
