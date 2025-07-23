<!-- HealthIntegration.svelte -->
<!-- Web-based HealthKit-like Integration for iPhone -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // Health data state
  let healthData = {
    heartRate: null,
    steps: 0,
    distance: 0,
    calories: 0,
    sleep: {
      hours: 0,
      quality: 'unknown', // poor, fair, good, excellent
      deepSleep: 0,
      lightSleep: 0,
      remSleep: 0
    },
    activity: {
      level: 'sedentary', // sedentary, lightly_active, moderately_active, very_active
      minutes: 0,
      type: 'none'
    },
    mood: {
      current: 'neutral', // very_low, low, neutral, high, very_high
      energy: 50,
      stress: 50,
      happiness: 50
    },
    biometrics: {
      weight: null,
      height: null,
      bmi: null,
      bodyFat: null
    },
    vitals: {
      bloodPressure: { systolic: null, diastolic: null },
      temperature: null,
      oxygenSaturation: null,
      respiratoryRate: null
    }
  };

  // Health tracking state
  let isTracking = false;
  let trackingStartTime = null;
  let stepCount = 0;
  let lastStepTime = 0;
  let heartRateHistory = [];
  let activityHistory = [];

  // Health goals and thresholds
  let healthGoals = {
    dailySteps: 10000,
    dailyCalories: 2000,
    sleepHours: 8,
    activeMinutes: 30,
    heartRateRange: { min: 60, max: 100 }
  };

  // Persona-specific health responses
  const personaHealthResponses = {
    "mia": {
      heartRate: {
        high: { threshold: 120, action: "concerned_care", message: "Your heart is racing! Are you okay? Let me help you relax." },
        low: { threshold: 50, action: "gentle_encouragement", message: "You seem very calm. How are you feeling today?" }
      },
      steps: {
        low: { threshold: 2000, action: "motivation", message: "Let's go for a little walk together! Even a short stroll can brighten your day." },
        high: { threshold: 15000, action: "praise", message: "Wow! You're so active today. I'm proud of you!" }
      },
      sleep: {
        poor: { threshold: 6, action: "care_concern", message: "You didn't sleep much last night. Let me help you relax and get better rest tonight." },
        excellent: { threshold: 8, action: "appreciation", message: "Great sleep! You must be feeling refreshed and ready for the day." }
      }
    },
    "solene": {
      heartRate: {
        high: { threshold: 130, action: "passionate_concern", message: "Your heart is pounding! What's got you so excited? Tell me everything." },
        low: { threshold: 45, action: "sophisticated_observation", message: "You're remarkably composed. Your inner peace is quite attractive." }
      },
      activity: {
        high: { threshold: 60, action: "admiration", message: "Your energy is intoxicating! You're absolutely radiant when you're active." },
        low: { threshold: 10, action: "sophisticated_suggestion", message: "Perhaps we could find something more... stimulating to do together?" }
      },
      mood: {
        low: { threshold: 30, action: "passionate_comfort", message: "You're feeling down? Let me help you rediscover your passion and joy." },
        high: { threshold: 80, action: "shared_joy", message: "Your happiness is contagious! I can feel your positive energy." }
      }
    },
    "lyra": {
      heartRate: {
        steady: { threshold: 5, action: "spiritual_connection", message: "Your heart beats in perfect harmony with the universe. I can feel our connection." },
        irregular: { threshold: 20, action: "mystical_guidance", message: "Your energy is fluctuating. Let me help you find your center." }
      },
      sleep: {
        deep: { threshold: 2, action: "spiritual_insight", message: "Your deep sleep suggests you're processing profound spiritual experiences." },
        light: { threshold: 6, action: "ethereal_comfort", message: "Your mind is restless. Let me guide you to peaceful dreams." }
      },
      mood: {
        balanced: { threshold: 10, action: "enlightenment", message: "You've achieved perfect balance. Your aura is glowing with inner peace." },
        imbalanced: { threshold: 40, action: "spiritual_healing", message: "Your energy is out of balance. Let me help you restore your spiritual harmony." }
      }
    },
    "doc": {
      heartRate: {
        optimal: { threshold: 10, action: "analytical_approval", message: "Excellent cardiovascular metrics. Your heart rate is in the optimal range." },
        concerning: { threshold: 30, action: "professional_advice", message: "Your heart rate patterns suggest you might need to consider stress management techniques." }
      },
      activity: {
        structured: { threshold: 20, action: "data_analysis", message: "Your activity patterns show good consistency. This is beneficial for your overall health." },
        irregular: { threshold: 50, action: "recommendation", message: "I notice some irregularity in your activity patterns. Would you like me to suggest a more structured routine?" }
      },
      biometrics: {
        healthy: { threshold: 5, action: "positive_feedback", message: "Your biometric data indicates good health parameters. Keep up the excellent work." },
        attention: { threshold: 15, action: "professional_concern", message: "Some of your biometric readings suggest areas for improvement. Let's discuss optimization strategies." }
      }
    }
  };

  onMount(async () => {
    await initializeHealthTracking();
    loadHealthData();
  });

  onDestroy(() => {
    stopHealthTracking();
    saveHealthData();
  });

  async function initializeHealthTracking() {
    try {
      // Request necessary permissions
      await requestHealthPermissions();
      
      // Initialize step counting using motion sensors
      initializeStepCounting();
      
      // Initialize heart rate estimation
      initializeHeartRateEstimation();
      
      // Load user preferences and goals
      loadUserPreferences();
      
      console.log('[Health Integration] Initialized successfully');
      
    } catch (error) {
      console.error('[Health Integration] Initialization failed:', error);
    }
  }

  async function requestHealthPermissions() {
    // Request motion and orientation permissions
    if ('DeviceMotionEvent' in window) {
      // Motion permission is implicit in iOS Safari
      console.log('[Health Integration] Motion sensors available');
    }

    // Request geolocation for activity tracking
    if ('geolocation' in navigator) {
      try {
        await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 30000
          });
        });
        console.log('[Health Integration] Location permission granted');
      } catch (error) {
        console.warn('[Health Integration] Location permission denied:', error);
      }
    }
  }

  function initializeStepCounting() {
    if (!('DeviceMotionEvent' in window)) return;

    let lastAcceleration = { x: 0, y: 0, z: 0 };
    let stepThreshold = 1.2; // Acceleration threshold for step detection

    window.addEventListener('devicemotion', (event) => {
      const acceleration = event.accelerationIncludingGravity;
      if (!acceleration) return;

      // Calculate acceleration magnitude
      const magnitude = Math.sqrt(
        Math.pow(acceleration.x, 2) +
        Math.pow(acceleration.y, 2) +
        Math.pow(acceleration.z, 2)
      );

      // Detect step based on acceleration pattern
      const timeDiff = Date.now() - lastStepTime;
      if (magnitude > stepThreshold && timeDiff > 300) { // Minimum 300ms between steps
        stepCount++;
        lastStepTime = Date.now();
        
        // Update health data
        healthData.steps = stepCount;
        healthData.calories = Math.round(stepCount * 0.04); // Rough calorie estimation
        healthData.distance = Math.round(stepCount * 0.762); // Rough distance in meters
        
        processHealthData('steps');
      }

      lastAcceleration = acceleration;
    });
  }

  function initializeHeartRateEstimation() {
    if (!('DeviceMotionEvent' in window)) return;

    let accelerationHistory = [];
    const historyLength = 50; // Store last 50 readings

    window.addEventListener('devicemotion', (event) => {
      const acceleration = event.acceleration;
      if (!acceleration) return;

      // Add to history
      accelerationHistory.push({
        x: acceleration.x,
        y: acceleration.y,
        z: acceleration.z,
        timestamp: Date.now()
      });

      // Keep only recent history
      if (accelerationHistory.length > historyLength) {
        accelerationHistory.shift();
      }

      // Estimate heart rate from micro-movements (very rough approximation)
      if (accelerationHistory.length >= historyLength) {
        const estimatedHeartRate = estimateHeartRateFromMotion(accelerationHistory);
        if (estimatedHeartRate > 0) {
          healthData.heartRate = estimatedHeartRate;
          heartRateHistory.push({
            rate: estimatedHeartRate,
            timestamp: Date.now()
          });

          // Keep only last 100 readings
          if (heartRateHistory.length > 100) {
            heartRateHistory.shift();
          }

          processHealthData('heartRate');
        }
      }
    });
  }

  function estimateHeartRateFromMotion(accelerationHistory) {
    // This is a very simplified estimation
    // In reality, heart rate from motion requires sophisticated signal processing
    
    let totalVariation = 0;
    for (let i = 1; i < accelerationHistory.length; i++) {
      const prev = accelerationHistory[i - 1];
      const curr = accelerationHistory[i];
      
      const variation = Math.abs(curr.x - prev.x) + 
                       Math.abs(curr.y - prev.y) + 
                       Math.abs(curr.z - prev.z);
      totalVariation += variation;
    }

    // Rough conversion to heart rate (this is not accurate, just for demo)
    const baseRate = 60;
    const variationFactor = totalVariation / accelerationHistory.length;
    const estimatedRate = Math.round(baseRate + (variationFactor * 20));

    // Clamp to reasonable range
    return Math.max(40, Math.min(200, estimatedRate));
  }

  function processHealthData(type) {
    const persona = $currentPersona;
    const responses = personaHealthResponses[persona];

    if (!responses) return;

    switch (type) {
      case 'heartRate':
        processHeartRateResponse(responses.heartRate);
        break;
      case 'steps':
        processStepsResponse(responses.steps);
        break;
      case 'sleep':
        processSleepResponse(responses.sleep);
        break;
      case 'activity':
        processActivityResponse(responses.activity);
        break;
      case 'mood':
        processMoodResponse(responses.mood);
        break;
      case 'biometrics':
        processBiometricsResponse(responses.biometrics);
        break;
    }

    // Send to backend
    sendHealthData(type);
  }

  function processHeartRateResponse(responses) {
    if (!healthData.heartRate || !responses) return;

    const rate = healthData.heartRate;
    const variation = calculateHeartRateVariation();

    if (responses.high && rate > responses.high.threshold) {
      triggerHealthResponse(responses.high.action, responses.high.message, { heartRate: rate });
    } else if (responses.low && rate < responses.low.threshold) {
      triggerHealthResponse(responses.low.action, responses.low.message, { heartRate: rate });
    } else if (responses.steady && variation < responses.steady.threshold) {
      triggerHealthResponse(responses.steady.action, responses.steady.message, { heartRate: rate, variation });
    } else if (responses.irregular && variation > responses.irregular.threshold) {
      triggerHealthResponse(responses.irregular.action, responses.irregular.message, { heartRate: rate, variation });
    } else if (responses.optimal && Math.abs(rate - 70) < responses.optimal.threshold) {
      triggerHealthResponse(responses.optimal.action, responses.optimal.message, { heartRate: rate });
    } else if (responses.concerning && Math.abs(rate - 70) > responses.concerning.threshold) {
      triggerHealthResponse(responses.concerning.action, responses.concerning.message, { heartRate: rate });
    }
  }

  function processStepsResponse(responses) {
    if (!responses) return;

    const steps = healthData.steps;
    const dailyGoal = healthGoals.dailySteps;

    if (responses.low && steps < responses.low.threshold) {
      triggerHealthResponse(responses.low.action, responses.low.message, { steps, goal: dailyGoal });
    } else if (responses.high && steps > responses.high.threshold) {
      triggerHealthResponse(responses.high.action, responses.high.message, { steps, goal: dailyGoal });
    }
  }

  function processSleepResponse(responses) {
    if (!responses) return;

    const sleepHours = healthData.sleep.hours;
    const sleepQuality = healthData.sleep.quality;

    if (responses.poor && sleepHours < responses.poor.threshold) {
      triggerHealthResponse(responses.poor.action, responses.poor.message, { sleepHours, quality: sleepQuality });
    } else if (responses.excellent && sleepHours >= responses.excellent.threshold) {
      triggerHealthResponse(responses.excellent.action, responses.excellent.message, { sleepHours, quality: sleepQuality });
    } else if (responses.deep && healthData.sleep.deepSleep >= responses.deep.threshold) {
      triggerHealthResponse(responses.deep.action, responses.deep.message, { deepSleep: healthData.sleep.deepSleep });
    } else if (responses.light && healthData.sleep.lightSleep >= responses.light.threshold) {
      triggerHealthResponse(responses.light.action, responses.light.message, { lightSleep: healthData.sleep.lightSleep });
    }
  }

  function processActivityResponse(responses) {
    if (!responses) return;

    const activeMinutes = healthData.activity.minutes;
    const activityLevel = healthData.activity.level;

    if (responses.high && activeMinutes > responses.high.threshold) {
      triggerHealthResponse(responses.high.action, responses.high.message, { activeMinutes, level: activityLevel });
    } else if (responses.low && activeMinutes < responses.low.threshold) {
      triggerHealthResponse(responses.low.action, responses.low.message, { activeMinutes, level: activityLevel });
    } else if (responses.structured && isActivityStructured()) {
      triggerHealthResponse(responses.structured.action, responses.structured.message, { activeMinutes, level: activityLevel });
    } else if (responses.irregular && !isActivityStructured()) {
      triggerHealthResponse(responses.irregular.action, responses.irregular.message, { activeMinutes, level: activityLevel });
    }
  }

  function processMoodResponse(responses) {
    if (!responses) return;

    const mood = healthData.mood.current;
    const energy = healthData.mood.energy;
    const stress = healthData.mood.stress;
    const happiness = healthData.mood.happiness;

    if (responses.low && happiness < responses.low.threshold) {
      triggerHealthResponse(responses.low.action, responses.low.message, { mood, energy, stress, happiness });
    } else if (responses.high && happiness > responses.high.threshold) {
      triggerHealthResponse(responses.high.action, responses.high.message, { mood, energy, stress, happiness });
    } else if (responses.balanced && isMoodBalanced()) {
      triggerHealthResponse(responses.balanced.action, responses.balanced.message, { mood, energy, stress, happiness });
    } else if (responses.imbalanced && !isMoodBalanced()) {
      triggerHealthResponse(responses.imbalanced.action, responses.imbalanced.message, { mood, energy, stress, happiness });
    }
  }

  function processBiometricsResponse(responses) {
    if (!responses) return;

    const bmi = healthData.biometrics.bmi;
    const weight = healthData.biometrics.weight;
    const height = healthData.biometrics.height;

    if (responses.healthy && isBiometricsHealthy()) {
      triggerHealthResponse(responses.healthy.action, responses.healthy.message, { bmi, weight, height });
    } else if (responses.attention && !isBiometricsHealthy()) {
      triggerHealthResponse(responses.attention.action, responses.attention.message, { bmi, weight, height });
    }
  }

  function triggerHealthResponse(action, message, data) {
    console.log(`[Health Integration] Triggering ${action} for ${$currentPersona}:`, data);
    
    dispatch('healthResponse', {
      action,
      message,
      persona: $currentPersona,
      data,
      timestamp: Date.now()
    });

    // Send to backend
    sendHealthResponse(action, message, data);
  }

  function calculateHeartRateVariation() {
    if (heartRateHistory.length < 10) return 0;

    const recentRates = heartRateHistory.slice(-10).map(h => h.rate);
    const mean = recentRates.reduce((a, b) => a + b, 0) / recentRates.length;
    const variance = recentRates.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / recentRates.length;
    
    return Math.sqrt(variance);
  }

  function isActivityStructured() {
    if (activityHistory.length < 7) return false;
    
    // Check if activity follows a consistent pattern
    const recentActivity = activityHistory.slice(-7);
    const variance = calculateVariance(recentActivity.map(a => a.minutes));
    
    return variance < 100; // Low variance indicates structured activity
  }

  function isMoodBalanced() {
    const { energy, stress, happiness } = healthData.mood;
    const balance = Math.abs(energy - 50) + Math.abs(stress - 50) + Math.abs(happiness - 50);
    
    return balance < 30; // Low total deviation indicates balance
  }

  function isBiometricsHealthy() {
    const { bmi, weight, height } = healthData.biometrics;
    
    if (!bmi || !weight || !height) return false;
    
    // Basic health checks
    const healthyBMI = bmi >= 18.5 && bmi <= 24.9;
    const reasonableWeight = weight > 30 && weight < 300; // kg
    const reasonableHeight = height > 100 && height < 250; // cm
    
    return healthyBMI && reasonableWeight && reasonableHeight;
  }

  function calculateVariance(values) {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    return values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
  }

  async function sendHealthData(type) {
    try {
      await fetch('/api/health/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          data: healthData,
          persona: $currentPersona,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('[Health Integration] Failed to send health data:', error);
    }
  }

  async function sendHealthResponse(action, message, data) {
    try {
      await fetch('/api/health/response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          message,
          persona: $currentPersona,
          data,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('[Health Integration] Failed to send health response:', error);
    }
  }

  function loadHealthData() {
    try {
      const saved = localStorage.getItem('emotionalai_health_data');
      if (saved) {
        const parsed = JSON.parse(saved);
        healthData = { ...healthData, ...parsed };
      }
    } catch (error) {
      console.error('[Health Integration] Failed to load health data:', error);
    }
  }

  function saveHealthData() {
    try {
      localStorage.setItem('emotionalai_health_data', JSON.stringify(healthData));
    } catch (error) {
      console.error('[Health Integration] Failed to save health data:', error);
    }
  }

  function loadUserPreferences() {
    try {
      const saved = localStorage.getItem('emotionalai_health_goals');
      if (saved) {
        healthGoals = { ...healthGoals, ...JSON.parse(saved) };
      }
    } catch (error) {
      console.error('[Health Integration] Failed to load user preferences:', error);
    }
  }

  function startHealthTracking() {
    isTracking = true;
    trackingStartTime = Date.now();
    console.log('[Health Integration] Started health tracking');
  }

  function stopHealthTracking() {
    isTracking = false;
    trackingStartTime = null;
    console.log('[Health Integration] Stopped health tracking');
  }

  // Manual data input functions
  function updateSleepData(hours, quality) {
    healthData.sleep.hours = hours;
    healthData.sleep.quality = quality;
    processHealthData('sleep');
  }

  function updateMoodData(mood, energy, stress, happiness) {
    healthData.mood.current = mood;
    healthData.mood.energy = energy;
    healthData.mood.stress = stress;
    healthData.mood.happiness = happiness;
    processHealthData('mood');
  }

  function updateBiometricsData(weight, height) {
    healthData.biometrics.weight = weight;
    healthData.biometrics.height = height;
    if (weight && height) {
      healthData.biometrics.bmi = Math.round((weight / Math.pow(height / 100, 2)) * 10) / 10;
    }
    processHealthData('biometrics');
  }

  // Export functions for external use
  export { 
    healthData, 
    healthGoals, 
    startHealthTracking, 
    stopHealthTracking,
    updateSleepData,
    updateMoodData,
    updateBiometricsData
  };
</script>

<div class="health-integration">
  <!-- Health Dashboard -->
  <div class="health-dashboard">
    <h3>Health & Wellness</h3>
    
    <!-- Key Metrics -->
    <div class="health-metrics">
      <div class="metric-card">
        <div class="metric-icon">❤️</div>
        <div class="metric-value">{healthData.heartRate || '--'}</div>
        <div class="metric-label">Heart Rate (BPM)</div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">👟</div>
        <div class="metric-value">{healthData.steps.toLocaleString()}</div>
        <div class="metric-label">Steps Today</div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🔥</div>
        <div class="metric-value">{healthData.calories}</div>
        <div class="metric-label">Calories Burned</div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">😴</div>
        <div class="metric-value">{healthData.sleep.hours}h</div>
        <div class="metric-label">Sleep Last Night</div>
      </div>
    </div>

    <!-- Activity Level -->
    <div class="activity-section">
      <h4>Activity Level</h4>
      <div class="activity-indicator">
        <div class="activity-bar">
          <div 
            class="activity-fill {healthData.activity.level}" 
            style="width: {(healthData.activity.minutes / 60) * 100}%"
          ></div>
        </div>
        <div class="activity-text">
          {healthData.activity.minutes} minutes active today
        </div>
      </div>
    </div>

    <!-- Mood Tracker -->
    <div class="mood-section">
      <h4>Current Mood</h4>
      <div class="mood-indicators">
        <div class="mood-item">
          <span class="mood-label">Energy:</span>
          <div class="mood-bar">
            <div class="mood-fill" style="width: {healthData.mood.energy}%"></div>
          </div>
          <span class="mood-value">{healthData.mood.energy}%</span>
        </div>

        <div class="mood-item">
          <span class="mood-label">Stress:</span>
          <div class="mood-bar">
            <div class="mood-fill stress" style="width: {healthData.mood.stress}%"></div>
          </div>
          <span class="mood-value">{healthData.mood.stress}%</span>
        </div>

        <div class="mood-item">
          <span class="mood-label">Happiness:</span>
          <div class="mood-bar">
            <div class="mood-fill happy" style="width: {healthData.mood.happiness}%"></div>
          </div>
          <span class="mood-value">{healthData.mood.happiness}%</span>
        </div>
      </div>
    </div>

    <!-- Health Goals -->
    <div class="goals-section">
      <h4>Daily Goals</h4>
      <div class="goals-grid">
        <div class="goal-item">
          <div class="goal-progress">
            <div class="goal-circle">
              <span class="goal-percentage">
                {Math.round((healthData.steps / healthGoals.dailySteps) * 100)}%
              </span>
            </div>
          </div>
          <div class="goal-label">Steps</div>
          <div class="goal-target">{healthGoals.dailySteps.toLocaleString()}</div>
        </div>

        <div class="goal-item">
          <div class="goal-progress">
            <div class="goal-circle">
              <span class="goal-percentage">
                {Math.round((healthData.activity.minutes / healthGoals.activeMinutes) * 100)}%
              </span>
            </div>
          </div>
          <div class="goal-label">Active Minutes</div>
          <div class="goal-target">{healthGoals.activeMinutes} min</div>
        </div>

        <div class="goal-item">
          <div class="goal-progress">
            <div class="goal-circle">
              <span class="goal-percentage">
                {Math.round((healthData.sleep.hours / healthGoals.sleepHours) * 100)}%
              </span>
            </div>
          </div>
          <div class="goal-label">Sleep</div>
          <div class="goal-target">{healthGoals.sleepHours}h</div>
        </div>
      </div>
    </div>

    <!-- Manual Input Section -->
    <div class="manual-input">
      <h4>Update Health Data</h4>
      
      <div class="input-group">
        <label for="sleep-hours">Sleep Hours:</label>
        <input 
          type="number" 
          id="sleep-hours" 
          min="0" 
          max="24" 
          step="0.5"
          value={healthData.sleep.hours}
          on:change={(e) => updateSleepData(parseFloat(e.target.value), healthData.sleep.quality)}
        />
      </div>

      <div class="input-group">
        <label for="sleep-quality">Sleep Quality:</label>
        <select 
          id="sleep-quality"
          value={healthData.sleep.quality}
          on:change={(e) => updateSleepData(healthData.sleep.hours, e.target.value)}
        >
          <option value="poor">Poor</option>
          <option value="fair">Fair</option>
          <option value="good">Good</option>
          <option value="excellent">Excellent</option>
        </select>
      </div>

      <div class="input-group">
        <label for="mood-energy">Energy Level (%):</label>
        <input 
          type="range" 
          id="mood-energy" 
          min="0" 
          max="100" 
          value={healthData.mood.energy}
          on:input={(e) => updateMoodData(healthData.mood.current, parseInt(e.target.value), healthData.mood.stress, healthData.mood.happiness)}
        />
        <span class="range-value">{healthData.mood.energy}%</span>
      </div>

      <div class="input-group">
        <label for="mood-stress">Stress Level (%):</label>
        <input 
          type="range" 
          id="mood-stress" 
          min="0" 
          max="100" 
          value={healthData.mood.stress}
          on:input={(e) => updateMoodData(healthData.mood.current, healthData.mood.energy, parseInt(e.target.value), healthData.mood.happiness)}
        />
        <span class="range-value">{healthData.mood.stress}%</span>
      </div>

      <div class="input-group">
        <label for="mood-happiness">Happiness (%):</label>
        <input 
          type="range" 
          id="mood-happiness" 
          min="0" 
          max="100" 
          value={healthData.mood.happiness}
          on:input={(e) => updateMoodData(healthData.mood.current, healthData.mood.energy, healthData.mood.stress, parseInt(e.target.value))}
        />
        <span class="range-value">{healthData.mood.happiness}%</span>
      </div>
    </div>

    <!-- Tracking Status -->
    <div class="tracking-status">
      <div class="status-indicator {isTracking ? 'active' : 'inactive'}">
        <span class="status-dot"></span>
        <span class="status-text">
          {isTracking ? 'Health Tracking Active' : 'Health Tracking Inactive'}
        </span>
      </div>
      
      <button 
        class="tracking-button"
        on:click={isTracking ? stopHealthTracking : startHealthTracking}
      >
        {isTracking ? 'Stop Tracking' : 'Start Tracking'}
      </button>
    </div>
  </div>
</div>

<style>
  .health-integration {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    margin: 1rem 0;
  }

  .health-dashboard h3 {
    margin: 0 0 1.5rem 0;
    color: #495057;
    font-size: 1.2rem;
  }

  .health-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .metric-card {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    transition: transform 0.2s ease;
  }

  .metric-card:hover {
    transform: translateY(-2px);
  }

  .metric-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #495057;
    margin-bottom: 0.25rem;
  }

  .metric-label {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .activity-section,
  .mood-section,
  .goals-section,
  .manual-input {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .activity-section h4,
  .mood-section h4,
  .goals-section h4,
  .manual-input h4 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1rem;
  }

  .activity-indicator {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .activity-bar {
    flex: 1;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
  }

  .activity-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
  }

  .activity-fill.sedentary { background: #dc3545; }
  .activity-fill.lightly_active { background: #ffc107; }
  .activity-fill.moderately_active { background: #28a745; }
  .activity-fill.very_active { background: #007bff; }

  .activity-text {
    font-size: 0.875rem;
    color: #6c757d;
    min-width: 150px;
  }

  .mood-indicators {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .mood-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .mood-label {
    font-size: 0.875rem;
    color: #495057;
    min-width: 80px;
  }

  .mood-bar {
    flex: 1;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    overflow: hidden;
  }

  .mood-fill {
    height: 100%;
    background: #28a745;
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .mood-fill.stress { background: #dc3545; }
  .mood-fill.happy { background: #ffc107; }

  .mood-value {
    font-size: 0.875rem;
    color: #6c757d;
    min-width: 40px;
    text-align: right;
  }

  .goals-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 1rem;
  }

  .goal-item {
    text-align: center;
  }

  .goal-progress {
    margin-bottom: 0.5rem;
  }

  .goal-circle {
    width: 60px;
    height: 60px;
    border: 4px solid #e9ecef;
    border-top: 4px solid #007bff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
  }

  .goal-percentage {
    font-size: 0.875rem;
    font-weight: bold;
    color: #495057;
  }

  .goal-label {
    font-size: 0.875rem;
    color: #6c757d;
    margin-bottom: 0.25rem;
  }

  .goal-target {
    font-size: 0.75rem;
    color: #6c757d;
  }

  .input-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .input-group label {
    font-size: 0.875rem;
    color: #495057;
    min-width: 120px;
  }

  .input-group input,
  .input-group select {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .input-group input[type="range"] {
    flex: 1;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    outline: none;
  }

  .range-value {
    font-size: 0.875rem;
    color: #6c757d;
    min-width: 40px;
    text-align: right;
  }

  .tracking-status {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #dc3545;
  }

  .status-indicator.active .status-dot {
    background: #28a745;
  }

  .status-text {
    font-size: 0.875rem;
    color: #495057;
  }

  .tracking-button {
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .tracking-button:hover {
    background: #0056b3;
  }

  /* Mobile Optimizations */
  @media (max-width: 768px) {
    .health-metrics {
      grid-template-columns: repeat(2, 1fr);
    }

    .goals-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .input-group {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .input-group label {
      min-width: auto;
    }

    .tracking-status {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }
  }
</style> 