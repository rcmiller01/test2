<!-- MobileSensors.svelte -->
<!-- iPhone Motion Sensors and Device Capabilities Integration -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // Sensor state
  let isMotionActive = false;
  let isOrientationActive = false;
  let isProximityActive = false;
  let isLightActive = false;
  let isBatteryActive = false;
  let isNetworkActive = false;
  let isGeolocationActive = false;

  // Sensor data
  let motionData = {
    acceleration: { x: 0, y: 0, z: 0 },
    accelerationIncludingGravity: { x: 0, y: 0, z: 0 },
    rotationRate: { alpha: 0, beta: 0, gamma: 0 },
    interval: 0
  };

  let orientationData = {
    alpha: 0, // Z-axis rotation (0-360)
    beta: 0,  // X-axis rotation (-180 to 180)
    gamma: 0  // Y-axis rotation (-90 to 90)
  };

  let proximityData = {
    distance: null,
    near: false
  };

  let lightData = {
    illuminance: null,
    level: 'unknown' // low, medium, high
  };

  let batteryData = {
    level: 0,
    charging: false,
    chargingTime: 0,
    dischargingTime: 0
  };

  let networkData = {
    effectiveType: 'unknown', // slow-2g, 2g, 3g, 4g
    downlink: 0,
    rtt: 0,
    saveData: false
  };

  let geolocationData = {
    latitude: null,
    longitude: null,
    accuracy: null,
    altitude: null,
    heading: null,
    speed: null
  };

  // Sensor objects
  let motionSensor = null;
  let orientationSensor = null;
  let proximitySensor = null;
  let lightSensor = null;
  let batteryManager = null;
  let networkInfo = null;
  let geolocationWatch = null;

  // Capability flags
  let capabilities = {
    motion: false,
    orientation: false,
    proximity: false,
    light: false,
    battery: false,
    network: false,
    geolocation: false,
    vibration: false,
    notifications: false,
    bluetooth: false,
    nfc: false
  };

  // Persona-specific sensor triggers
  const personaTriggers = {
    "mia": {
      motion: {
        gentleShake: { threshold: 0.5, action: "affectionate_response" },
        heartBeat: { threshold: 0.1, action: "emotional_connection" }
      },
      proximity: {
        near: { action: "intimate_interaction" },
        far: { action: "longing_response" }
      }
    },
    "solene": {
      motion: {
        dramaticGesture: { threshold: 1.0, action: "passionate_response" },
        elegantMovement: { threshold: 0.3, action: "sophisticated_interaction" }
      },
      orientation: {
        tilt: { threshold: 15, action: "mood_shift" }
      }
    },
    "lyra": {
      motion: {
        mysticalGesture: { threshold: 0.8, action: "ethereal_response" },
        gentleFloat: { threshold: 0.2, action: "spiritual_connection" }
      },
      light: {
        dark: { threshold: 10, action: "mystical_mode" },
        bright: { threshold: 1000, action: "enlightened_mode" }
      }
    },
    "doc": {
      motion: {
        preciseMovement: { threshold: 0.1, action: "analytical_response" },
        steadyHand: { threshold: 0.05, action: "professional_mode" }
      },
      orientation: {
        level: { threshold: 5, action: "focus_mode" }
      }
    }
  };

  onMount(async () => {
    await initializeSensors();
    checkCapabilities();
  });

  onDestroy(() => {
    cleanupSensors();
  });

  async function initializeSensors() {
    try {
      // Initialize motion sensor
      if ('DeviceMotionEvent' in window) {
        capabilities.motion = true;
        setupMotionSensor();
      }

      // Initialize device orientation
      if ('DeviceOrientationEvent' in window) {
        capabilities.orientation = true;
        setupOrientationSensor();
      }

      // Initialize proximity sensor
      if ('ProximitySensor' in window) {
        capabilities.proximity = true;
        setupProximitySensor();
      }

      // Initialize ambient light sensor
      if ('AmbientLightSensor' in window) {
        capabilities.light = true;
        setupLightSensor();
      }

      // Initialize battery API
      if ('getBattery' in navigator) {
        capabilities.battery = true;
        setupBatterySensor();
      }

      // Initialize network information
      if ('connection' in navigator) {
        capabilities.network = true;
        setupNetworkSensor();
      }

      // Initialize geolocation
      if ('geolocation' in navigator) {
        capabilities.geolocation = true;
        setupGeolocationSensor();
      }

      // Check other capabilities
      capabilities.vibration = 'vibrate' in navigator;
      capabilities.notifications = 'Notification' in window;
      capabilities.bluetooth = 'bluetooth' in navigator;
      capabilities.nfc = 'NDEFReader' in window;

      console.log('[Mobile Sensors] Initialized with capabilities:', capabilities);

    } catch (error) {
      console.error('[Mobile Sensors] Initialization failed:', error);
    }
  }

  function setupMotionSensor() {
    if (!capabilities.motion) return;

    window.addEventListener('devicemotion', (event) => {
      motionData = {
        acceleration: event.acceleration || { x: 0, y: 0, z: 0 },
        accelerationIncludingGravity: event.accelerationIncludingGravity || { x: 0, y: 0, z: 0 },
        rotationRate: event.rotationRate || { alpha: 0, beta: 0, gamma: 0 },
        interval: event.interval || 0
      };

      isMotionActive = true;
      processMotionData();
    });
  }

  function setupOrientationSensor() {
    if (!capabilities.orientation) return;

    window.addEventListener('deviceorientation', (event) => {
      orientationData = {
        alpha: event.alpha || 0,
        beta: event.beta || 0,
        gamma: event.gamma || 0
      };

      isOrientationActive = true;
      processOrientationData();
    });
  }

  function setupProximitySensor() {
    if (!capabilities.proximity) return;

    try {
      proximitySensor = new ProximitySensor();
      proximitySensor.addEventListener('reading', () => {
        proximityData = {
          distance: proximitySensor.distance,
          near: proximitySensor.distance < 5 // 5cm threshold
        };

        isProximityActive = true;
        processProximityData();
      });

      proximitySensor.start();
    } catch (error) {
      console.warn('[Mobile Sensors] Proximity sensor not available:', error);
    }
  }

  function setupLightSensor() {
    if (!capabilities.light) return;

    try {
      lightSensor = new AmbientLightSensor();
      lightSensor.addEventListener('reading', () => {
        lightData = {
          illuminance: lightSensor.illuminance,
          level: getLightLevel(lightSensor.illuminance)
        };

        isLightActive = true;
        processLightData();
      });

      lightSensor.start();
    } catch (error) {
      console.warn('[Mobile Sensors] Light sensor not available:', error);
    }
  }

  function setupBatterySensor() {
    if (!capabilities.battery) return;

    navigator.getBattery().then(battery => {
      batteryManager = battery;
      
      const updateBatteryInfo = () => {
        batteryData = {
          level: battery.level,
          charging: battery.charging,
          chargingTime: battery.chargingTime,
          dischargingTime: battery.dischargingTime
        };

        isBatteryActive = true;
        processBatteryData();
      };

      battery.addEventListener('levelchange', updateBatteryInfo);
      battery.addEventListener('chargingchange', updateBatteryInfo);
      battery.addEventListener('chargingtimechange', updateBatteryInfo);
      battery.addEventListener('dischargingtimechange', updateBatteryInfo);

      updateBatteryInfo();
    });
  }

  function setupNetworkSensor() {
    if (!capabilities.network) return;

    networkInfo = navigator.connection;
    
    const updateNetworkInfo = () => {
      networkData = {
        effectiveType: networkInfo.effectiveType,
        downlink: networkInfo.downlink,
        rtt: networkInfo.rtt,
        saveData: networkInfo.saveData
      };

      isNetworkActive = true;
      processNetworkData();
    };

    networkInfo.addEventListener('change', updateNetworkInfo);
    updateNetworkInfo();
  }

  function setupGeolocationSensor() {
    if (!capabilities.geolocation) return;

    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 30000
    };

    geolocationWatch = navigator.geolocation.watchPosition(
      (position) => {
        geolocationData = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          heading: position.coords.heading,
          speed: position.coords.speed
        };

        isGeolocationActive = true;
        processGeolocationData();
      },
      (error) => {
        console.error('[Mobile Sensors] Geolocation error:', error);
      },
      options
    );
  }

  function processMotionData() {
    const persona = $currentPersona;
    const triggers = personaTriggers[persona]?.motion;

    if (!triggers) return;

    // Calculate motion magnitude
    const magnitude = Math.sqrt(
      Math.pow(motionData.acceleration.x, 2) +
      Math.pow(motionData.acceleration.y, 2) +
      Math.pow(motionData.acceleration.z, 2)
    );

    // Check for gentle shake (Mia)
    if (triggers.gentleShake && magnitude > triggers.gentleShake.threshold) {
      triggerPersonaAction(triggers.gentleShake.action, { magnitude, motionData });
    }

    // Check for dramatic gesture (Solene)
    if (triggers.dramaticGesture && magnitude > triggers.dramaticGesture.threshold) {
      triggerPersonaAction(triggers.dramaticGesture.action, { magnitude, motionData });
    }

    // Check for mystical gesture (Lyra)
    if (triggers.mysticalGesture && magnitude > triggers.mysticalGesture.threshold) {
      triggerPersonaAction(triggers.mysticalGesture.action, { magnitude, motionData });
    }

    // Check for precise movement (Doc)
    if (triggers.preciseMovement && magnitude < triggers.preciseMovement.threshold) {
      triggerPersonaAction(triggers.preciseMovement.action, { magnitude, motionData });
    }

    // Send to backend
    sendSensorData('motion', motionData);
  }

  function processOrientationData() {
    const persona = $currentPersona;
    const triggers = personaTriggers[persona]?.orientation;

    if (!triggers) return;

    // Check for tilt (Solene)
    if (triggers.tilt && Math.abs(orientationData.beta) > triggers.tilt.threshold) {
      triggerPersonaAction(triggers.tilt.action, { orientationData });
    }

    // Check for level (Doc)
    if (triggers.level && Math.abs(orientationData.beta) < triggers.level.threshold) {
      triggerPersonaAction(triggers.level.action, { orientationData });
    }

    sendSensorData('orientation', orientationData);
  }

  function processProximityData() {
    const persona = $currentPersona;
    const triggers = personaTriggers[persona]?.proximity;

    if (!triggers) return;

    if (proximityData.near && triggers.near) {
      triggerPersonaAction(triggers.near.action, { proximityData });
    } else if (!proximityData.near && triggers.far) {
      triggerPersonaAction(triggers.far.action, { proximityData });
    }

    sendSensorData('proximity', proximityData);
  }

  function processLightData() {
    const persona = $currentPersona;
    const triggers = personaTriggers[persona]?.light;

    if (!triggers) return;

    if (lightData.illuminance < triggers.dark.threshold && triggers.dark) {
      triggerPersonaAction(triggers.dark.action, { lightData });
    } else if (lightData.illuminance > triggers.bright.threshold && triggers.bright) {
      triggerPersonaAction(triggers.bright.action, { lightData });
    }

    sendSensorData('light', lightData);
  }

  function processBatteryData() {
    // Battery-based persona adjustments
    if (batteryData.level < 0.2) {
      // Low battery - reduce intensive features
      dispatch('batteryLow', { level: batteryData.level });
    }

    sendSensorData('battery', batteryData);
  }

  function processNetworkData() {
    // Network-based persona adjustments
    if (networkData.effectiveType === 'slow-2g' || networkData.effectiveType === '2g') {
      // Slow connection - reduce data usage
      dispatch('networkSlow', { networkData });
    }

    sendSensorData('network', networkData);
  }

  function processGeolocationData() {
    // Location-based persona adjustments
    if (geolocationData.latitude && geolocationData.longitude) {
      // Could trigger location-specific responses
      dispatch('locationUpdate', { geolocationData });
    }

    sendSensorData('geolocation', geolocationData);
  }

  function triggerPersonaAction(action, data) {
    console.log(`[Mobile Sensors] Triggering ${action} for ${$currentPersona}:`, data);
    
    dispatch('personaAction', {
      action,
      persona: $currentPersona,
      data,
      timestamp: Date.now()
    });

    // Send to backend
    sendPersonaAction(action, data);
  }

  async function sendSensorData(type, data) {
    try {
      await fetch('/api/sensors/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          data,
          persona: $currentPersona,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('[Mobile Sensors] Failed to send sensor data:', error);
    }
  }

  async function sendPersonaAction(action, data) {
    try {
      await fetch('/api/sensors/action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          persona: $currentPersona,
          data,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('[Mobile Sensors] Failed to send persona action:', error);
    }
  }

  function getLightLevel(illuminance) {
    if (illuminance < 10) return 'low';
    if (illuminance < 1000) return 'medium';
    return 'high';
  }

  function checkCapabilities() {
    // Request permissions for sensors that need them
    if (capabilities.geolocation) {
      navigator.geolocation.getCurrentPosition(
        () => console.log('[Mobile Sensors] Geolocation permission granted'),
        () => console.warn('[Mobile Sensors] Geolocation permission denied')
      );
    }

    if (capabilities.notifications) {
      Notification.requestPermission().then(permission => {
        console.log('[Mobile Sensors] Notification permission:', permission);
      });
    }
  }

  function cleanupSensors() {
    if (proximitySensor) {
      proximitySensor.stop();
    }

    if (lightSensor) {
      lightSensor.stop();
    }

    if (geolocationWatch) {
      navigator.geolocation.clearWatch(geolocationWatch);
    }

    // Remove event listeners
    window.removeEventListener('devicemotion', null);
    window.removeEventListener('deviceorientation', null);
  }

  // Utility functions for external use
  export function vibrate(pattern) {
    if (capabilities.vibration) {
      navigator.vibrate(pattern);
    }
  }

  export function requestNotification(title, options) {
    if (capabilities.notifications && Notification.permission === 'granted') {
      new Notification(title, options);
    }
  }

  // Expose sensor data for external components
  export { 
    motionData, 
    orientationData, 
    proximityData, 
    lightData, 
    batteryData, 
    networkData, 
    geolocationData,
    capabilities 
  };
</script>

<div class="mobile-sensors">
  <!-- Sensor Status Display -->
  <div class="sensor-status">
    <h3>Device Sensors</h3>
    
    <div class="sensor-grid">
      <!-- Motion Sensor -->
      <div class="sensor-item {isMotionActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">📱</span>
        <span class="sensor-name">Motion</span>
        <span class="sensor-status">{isMotionActive ? 'Active' : 'Inactive'}</span>
      </div>

      <!-- Orientation Sensor -->
      <div class="sensor-item {isOrientationActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">🔄</span>
        <span class="sensor-name">Orientation</span>
        <span class="sensor-status">{isOrientationActive ? 'Active' : 'Inactive'}</span>
      </div>

      <!-- Proximity Sensor -->
      <div class="sensor-item {isProximityActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">👁️</span>
        <span class="sensor-name">Proximity</span>
        <span class="sensor-status">{isProximityActive ? 'Active' : 'Inactive'}</span>
      </div>

      <!-- Light Sensor -->
      <div class="sensor-item {isLightActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">💡</span>
        <span class="sensor-name">Light</span>
        <span class="sensor-status">{isLightActive ? 'Active' : 'Inactive'}</span>
      </div>

      <!-- Battery -->
      <div class="sensor-item {isBatteryActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">🔋</span>
        <span class="sensor-name">Battery</span>
        <span class="sensor-status">{isBatteryActive ? `${Math.round(batteryData.level * 100)}%` : 'Unknown'}</span>
      </div>

      <!-- Network -->
      <div class="sensor-item {isNetworkActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">📶</span>
        <span class="sensor-name">Network</span>
        <span class="sensor-status">{isNetworkActive ? networkData.effectiveType : 'Unknown'}</span>
      </div>

      <!-- Geolocation -->
      <div class="sensor-item {isGeolocationActive ? 'active' : 'inactive'}">
        <span class="sensor-icon">📍</span>
        <span class="sensor-name">Location</span>
        <span class="sensor-status">{isGeolocationActive ? 'Active' : 'Inactive'}</span>
      </div>
    </div>
  </div>

  <!-- Real-time Sensor Data (Debug) -->
  {#if isMotionActive || isOrientationActive}
    <div class="sensor-data">
      <h4>Real-time Data</h4>
      
      {#if isMotionActive}
        <div class="data-item">
          <strong>Motion:</strong>
          <span>X: {motionData.acceleration.x?.toFixed(2) || '0.00'}</span>
          <span>Y: {motionData.acceleration.y?.toFixed(2) || '0.00'}</span>
          <span>Z: {motionData.acceleration.z?.toFixed(2) || '0.00'}</span>
        </div>
      {/if}

      {#if isOrientationActive}
        <div class="data-item">
          <strong>Orientation:</strong>
          <span>α: {orientationData.alpha?.toFixed(1) || '0.0'}°</span>
          <span>β: {orientationData.beta?.toFixed(1) || '0.0'}°</span>
          <span>γ: {orientationData.gamma?.toFixed(1) || '0.0'}°</span>
        </div>
      {/if}

      {#if isProximityActive}
        <div class="data-item">
          <strong>Proximity:</strong>
          <span>{proximityData.near ? 'Near' : 'Far'}</span>
          {#if proximityData.distance}
            <span>({proximityData.distance.toFixed(1)}cm)</span>
          {/if}
        </div>
      {/if}

      {#if isLightActive}
        <div class="data-item">
          <strong>Light:</strong>
          <span>{lightData.level}</span>
          {#if lightData.illuminance}
            <span>({lightData.illuminance.toFixed(0)} lux)</span>
          {/if}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Capability Information -->
  <div class="capabilities">
    <h4>Device Capabilities</h4>
    <div class="capability-list">
      {#each Object.entries(capabilities) as [capability, available]}
        <div class="capability-item {available ? 'available' : 'unavailable'}">
          <span class="capability-icon">{available ? '✅' : '❌'}</span>
          <span class="capability-name">{capability}</span>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .mobile-sensors {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    margin: 1rem 0;
  }

  .sensor-status h3 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1.1rem;
  }

  .sensor-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .sensor-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.75rem;
    background: white;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    transition: all 0.3s ease;
  }

  .sensor-item.active {
    border-color: #28a745;
    background: #d4edda;
  }

  .sensor-item.inactive {
    border-color: #dc3545;
    background: #f8d7da;
    opacity: 0.7;
  }

  .sensor-icon {
    font-size: 1.5rem;
  }

  .sensor-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: #495057;
  }

  .sensor-status {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .sensor-item.active .sensor-status {
    color: #155724;
  }

  .sensor-item.inactive .sensor-status {
    color: #721c24;
  }

  .sensor-data {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .sensor-data h4 {
    margin: 0 0 0.75rem 0;
    color: #495057;
    font-size: 1rem;
  }

  .data-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  .data-item strong {
    min-width: 80px;
    color: #495057;
  }

  .data-item span {
    background: #e9ecef;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.75rem;
  }

  .capabilities {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
  }

  .capabilities h4 {
    margin: 0 0 0.75rem 0;
    color: #495057;
    font-size: 1rem;
  }

  .capability-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
  }

  .capability-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .capability-item.available {
    background: #d4edda;
    color: #155724;
  }

  .capability-item.unavailable {
    background: #f8d7da;
    color: #721c24;
  }

  .capability-icon {
    font-size: 1rem;
  }

  .capability-name {
    text-transform: capitalize;
    font-weight: 500;
  }

  /* Mobile Optimizations */
  @media (max-width: 768px) {
    .sensor-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .capability-list {
      grid-template-columns: repeat(2, 1fr);
    }

    .data-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.25rem;
    }

    .data-item strong {
      min-width: auto;
    }
  }
</style> 