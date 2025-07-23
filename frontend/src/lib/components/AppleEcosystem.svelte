<!-- AppleEcosystem.svelte -->
<!-- Apple Ecosystem Integration for iPhone/iPad/macOS -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // Apple ecosystem state
  let ecosystemData = {
    deviceType: 'unknown', // iphone, ipad, mac, apple_watch
    deviceModel: '',
    osVersion: '',
    screenSize: { width: 0, height: 0 },
    pixelRatio: 1,
    colorScheme: 'light', // light, dark
    isStandalone: false,
    isInstalled: false
  };

  // Feature availability
  let features = {
    airdrop: false,
    handoff: false,
    icloud: false,
    appleWatch: false,
    siri: false,
    shortcuts: false,
    homekit: false,
    carplay: false,
    airplay: false,
    continuity: false,
    universalControl: false,
    sidecar: false
  };

  // Connection state
  let connections = {
    nearbyDevices: [],
    activeHandoff: null,
    icloudSync: {
      status: 'disconnected',
      lastSync: null,
      pendingChanges: 0
    },
    appleWatch: {
      connected: false,
      batteryLevel: null,
      heartRate: null,
      activityData: null
    }
  };

  // Handoff data
  let handoffData = {
    currentActivity: null,
    availableActivities: [],
    supportedTypes: ['conversation', 'memory', 'scene', 'mood', 'health']
  };

  // iCloud sync data
  let icloudData = {
    conversations: [],
    memories: [],
    settings: {},
    healthData: {},
    lastSyncTime: null
  };

  onMount(async () => {
    await initializeAppleEcosystem();
    setupEventListeners();
  });

  onDestroy(() => {
    cleanupEventListeners();
  });

  async function initializeAppleEcosystem() {
    try {
      // Detect device and capabilities
      detectDevice();
      detectFeatures();
      
      // Initialize available features
      await initializeAvailableFeatures();
      
      // Setup PWA detection
      detectPWAStatus();
      
      // Initialize iCloud-like sync
      await initializeCloudSync();
      
      console.log('[Apple Ecosystem] Initialized successfully');
      
    } catch (error) {
      console.error('[Apple Ecosystem] Initialization failed:', error);
    }
  }

  function detectDevice() {
    const userAgent = navigator.userAgent;
    const platform = navigator.platform;
    
    // Detect device type
    if (/iPhone/.test(userAgent)) {
      ecosystemData.deviceType = 'iphone';
    } else if (/iPad/.test(userAgent)) {
      ecosystemData.deviceType = 'ipad';
    } else if (/Mac/.test(platform)) {
      ecosystemData.deviceType = 'mac';
    } else if (/Apple Watch/.test(userAgent)) {
      ecosystemData.deviceType = 'apple_watch';
    }

    // Detect OS version
    const osMatch = userAgent.match(/OS (\d+)_(\d+)_?(\d+)?/);
    if (osMatch) {
      ecosystemData.osVersion = `${osMatch[1]}.${osMatch[2]}.${osMatch[3] || 0}`;
    }

    // Get screen information
    ecosystemData.screenSize = {
      width: window.screen.width,
      height: window.screen.height
    };
    ecosystemData.pixelRatio = window.devicePixelRatio || 1;

    // Detect color scheme
    ecosystemData.colorScheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

    console.log('[Apple Ecosystem] Device detected:', ecosystemData);
  }

  function detectFeatures() {
    // Check for Web Share API (AirDrop-like functionality)
    features.airdrop = 'share' in navigator;
    
    // Check for Service Worker (Handoff-like functionality)
    features.handoff = 'serviceWorker' in navigator;
    
    // Check for IndexedDB (iCloud-like storage)
    features.icloud = 'indexedDB' in window;
    
    // Check for Web Bluetooth (Apple Watch-like connectivity)
    features.appleWatch = 'bluetooth' in navigator;
    
    // Check for Web Speech API (Siri-like functionality)
    features.siri = 'speechSynthesis' in window && (window.SpeechRecognition || window.webkitSpeechRecognition);
    
    // Check for Web App Manifest (Shortcuts-like functionality)
    features.shortcuts = 'serviceWorker' in navigator && 'manifest' in document.createElement('link');
    
    // Check for Web Push API (HomeKit-like notifications)
    features.homekit = 'PushManager' in window;
    
    // Check for Web Audio API (CarPlay-like audio)
    features.carplay = 'AudioContext' in window || 'webkitAudioContext' in window;
    
    // Check for WebRTC (AirPlay-like streaming)
    features.airplay = 'RTCPeerConnection' in window;
    
    // Check for Web Workers (Continuity-like background processing)
    features.continuity = 'Worker' in window;
    
    // Check for Pointer Events (Universal Control-like input)
    features.universalControl = 'PointerEvent' in window;
    
    // Check for Screen Capture API (Sidecar-like display)
    features.sidecar = 'getDisplayMedia' in navigator;

    console.log('[Apple Ecosystem] Features detected:', features);
  }

  async function initializeAvailableFeatures() {
    // Initialize Web Share API for AirDrop-like functionality
    if (features.airdrop) {
      setupAirDrop();
    }

    // Initialize Service Worker for Handoff-like functionality
    if (features.handoff) {
      setupHandoff();
    }

    // Initialize IndexedDB for iCloud-like sync
    if (features.icloud) {
      await setupCloudSync();
    }

    // Initialize Web Bluetooth for Apple Watch-like connectivity
    if (features.appleWatch) {
      setupAppleWatchIntegration();
    }

    // Initialize Web Speech API for Siri-like functionality
    if (features.siri) {
      setupSiriIntegration();
    }

    // Initialize Web Push API for HomeKit-like notifications
    if (features.homekit) {
      setupHomeKitIntegration();
    }
  }

  function setupAirDrop() {
    // Web Share API provides AirDrop-like functionality
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      console.log('[Apple Ecosystem] Install prompt available');
    });

    // Handle shared data
    if ('share' in navigator) {
      window.addEventListener('DOMContentLoaded', () => {
        if (navigator.share) {
          console.log('[Apple Ecosystem] Web Share API available');
        }
      });
    }
  }

  function setupHandoff() {
    // Service Worker provides Handoff-like functionality
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'handoff') {
          handleHandoffData(event.data.payload);
        }
      });
    }

    // Broadcast Channel API for cross-tab communication
    if ('BroadcastChannel' in window) {
      const handoffChannel = new BroadcastChannel('emotionalai_handoff');
      
      handoffChannel.onmessage = (event) => {
        if (event.data.type === 'activity_transfer') {
          handleActivityTransfer(event.data.activity);
        }
      };
    }
  }

  async function setupCloudSync() {
    try {
      // Use IndexedDB for iCloud-like storage
      const dbName = 'EmotionalAI_Cloud';
      const dbVersion = 1;
      
      const request = indexedDB.open(dbName, dbVersion);
      
      request.onerror = () => {
        console.error('[Apple Ecosystem] IndexedDB error');
        connections.icloudSync.status = 'error';
      };

      request.onsuccess = (event) => {
        const db = event.target.result;
        console.log('[Apple Ecosystem] Cloud sync initialized');
        connections.icloudSync.status = 'connected';
        
        // Load existing data
        loadCloudData(db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create object stores
        if (!db.objectStoreNames.contains('conversations')) {
          db.createObjectStore('conversations', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('memories')) {
          db.createObjectStore('memories', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('settings')) {
          db.createObjectStore('settings', { keyPath: 'key' });
        }
        if (!db.objectStoreNames.contains('healthData')) {
          db.createObjectStore('healthData', { keyPath: 'date' });
        }
      };

    } catch (error) {
      console.error('[Apple Ecosystem] Cloud sync setup failed:', error);
    }
  }

  function setupAppleWatchIntegration() {
    // Web Bluetooth API for Apple Watch-like connectivity
    if ('bluetooth' in navigator) {
      console.log('[Apple Ecosystem] Web Bluetooth available for Apple Watch integration');
      
      // This would require user interaction to pair
      // For demo purposes, we'll simulate Apple Watch data
      simulateAppleWatchData();
    }
  }

  function setupSiriIntegration() {
    // Web Speech API provides Siri-like functionality
    if ('speechSynthesis' in window) {
      console.log('[Apple Ecosystem] Speech synthesis available for Siri integration');
    }

    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      console.log('[Apple Ecosystem] Speech recognition available for Siri integration');
    }
  }

  function setupHomeKitIntegration() {
    // Web Push API provides HomeKit-like notifications
    if ('PushManager' in window) {
      console.log('[Apple Ecosystem] Push notifications available for HomeKit integration');
    }
  }

  function detectPWAStatus() {
    // Check if app is running as PWA
    ecosystemData.isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    ecosystemData.isInstalled = window.navigator.standalone || ecosystemData.isStandalone;
    
    console.log('[Apple Ecosystem] PWA status:', {
      isStandalone: ecosystemData.isStandalone,
      isInstalled: ecosystemData.isInstalled
    });
  }

  function setupEventListeners() {
    // Listen for color scheme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      ecosystemData.colorScheme = e.matches ? 'dark' : 'light';
      dispatch('colorSchemeChanged', { scheme: ecosystemData.colorScheme });
    });

    // Listen for orientation changes
    window.addEventListener('orientationchange', () => {
      setTimeout(() => {
        ecosystemData.screenSize = {
          width: window.screen.width,
          height: window.screen.height
        };
        dispatch('orientationChanged', { screenSize: ecosystemData.screenSize });
      }, 100);
    });

    // Listen for online/offline status
    window.addEventListener('online', () => {
      connections.icloudSync.status = 'connected';
      dispatch('connectionChanged', { status: 'online' });
    });

    window.addEventListener('offline', () => {
      connections.icloudSync.status = 'disconnected';
      dispatch('connectionChanged', { status: 'offline' });
    });
  }

  function cleanupEventListeners() {
    // Cleanup would go here if needed
  }

  // Handoff functionality
  function createHandoffActivity(type, data) {
    const activity = {
      id: `activity_${Date.now()}`,
      type,
      data,
      timestamp: Date.now(),
      device: ecosystemData.deviceType,
      persona: $currentPersona
    };

    handoffData.currentActivity = activity;
    
    // Store in localStorage for cross-device access
    localStorage.setItem('emotionalai_handoff_activity', JSON.stringify(activity));
    
    // Broadcast to other tabs
    if ('BroadcastChannel' in window) {
      const handoffChannel = new BroadcastChannel('emotionalai_handoff');
      handoffChannel.postMessage({
        type: 'activity_created',
        activity
      });
    }

    console.log('[Apple Ecosystem] Handoff activity created:', activity);
    return activity;
  }

  function handleHandoffData(data) {
    console.log('[Apple Ecosystem] Handoff data received:', data);
    
    // Process the handoff data based on type
    switch (data.type) {
      case 'conversation':
        handleConversationHandoff(data);
        break;
      case 'memory':
        handleMemoryHandoff(data);
        break;
      case 'scene':
        handleSceneHandoff(data);
        break;
      case 'mood':
        handleMoodHandoff(data);
        break;
      case 'health':
        handleHealthHandoff(data);
        break;
    }
  }

  function handleActivityTransfer(activity) {
    console.log('[Apple Ecosystem] Activity transfer received:', activity);
    
    // Switch to the appropriate persona if needed
    if (activity.persona && activity.persona !== $currentPersona) {
      // This would trigger a persona switch
      dispatch('personaSwitch', { persona: activity.persona });
    }

    // Load the activity data
    dispatch('activityLoaded', { activity });
  }

  // Cloud sync functionality
  async function loadCloudData(db) {
    try {
      // Load conversations
      const conversationsStore = db.transaction(['conversations'], 'readonly').objectStore('conversations');
      const conversations = await getAllFromStore(conversationsStore);
      icloudData.conversations = conversations;

      // Load memories
      const memoriesStore = db.transaction(['memories'], 'readonly').objectStore('memories');
      const memories = await getAllFromStore(memoriesStore);
      icloudData.memories = memories;

      // Load settings
      const settingsStore = db.transaction(['settings'], 'readonly').objectStore('settings');
      const settings = await getAllFromStore(settingsStore);
      icloudData.settings = settings.reduce((acc, setting) => {
        acc[setting.key] = setting.value;
        return acc;
      }, {});

      // Load health data
      const healthStore = db.transaction(['healthData'], 'readonly').objectStore('healthData');
      const healthData = await getAllFromStore(healthStore);
      icloudData.healthData = healthData;

      icloudData.lastSyncTime = Date.now();
      connections.icloudSync.lastSync = new Date();

      console.log('[Apple Ecosystem] Cloud data loaded:', icloudData);
      
    } catch (error) {
      console.error('[Apple Ecosystem] Failed to load cloud data:', error);
    }
  }

  async function getAllFromStore(store) {
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function saveToCloud(type, data) {
    try {
      const dbName = 'EmotionalAI_Cloud';
      const request = indexedDB.open(dbName, 1);
      
      request.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        
        const saveRequest = store.put(data);
        saveRequest.onsuccess = () => {
          console.log(`[Apple Ecosystem] ${type} saved to cloud`);
          connections.icloudSync.pendingChanges++;
        };
        saveRequest.onerror = () => {
          console.error(`[Apple Ecosystem] Failed to save ${type} to cloud`);
        };
      };

    } catch (error) {
      console.error('[Apple Ecosystem] Cloud save failed:', error);
    }
  }

  // Apple Watch simulation
  function simulateAppleWatchData() {
    setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance of new data
        connections.appleWatch = {
          connected: true,
          batteryLevel: Math.random() * 100,
          heartRate: 60 + Math.random() * 40, // 60-100 BPM
          activityData: {
            steps: Math.floor(Math.random() * 1000),
            calories: Math.floor(Math.random() * 100),
            activeMinutes: Math.floor(Math.random() * 30)
          }
        };

        dispatch('appleWatchData', { data: connections.appleWatch });
      }
    }, 5000); // Update every 5 seconds
  }

  // Share functionality (AirDrop-like)
  async function shareContent(content, type = 'text') {
    if (!features.airdrop) {
      console.warn('[Apple Ecosystem] Web Share API not available');
      return false;
    }

    try {
      const shareData = {
        title: 'EmotionalAI',
        text: content,
        url: window.location.href
      };

      if (type === 'conversation') {
        shareData.text = `Conversation with ${$currentPersonaConfig?.name || 'companion'}: ${content}`;
      } else if (type === 'memory') {
        shareData.text = `Memory from EmotionalAI: ${content}`;
      }

      await navigator.share(shareData);
      console.log('[Apple Ecosystem] Content shared successfully');
      return true;

    } catch (error) {
      console.error('[Apple Ecosystem] Share failed:', error);
      return false;
    }
  }

  // Siri-like voice commands
  function processVoiceCommand(command) {
    const lowerCommand = command.toLowerCase();
    
    // Persona switching
    if (lowerCommand.includes('switch to mia')) {
      dispatch('personaSwitch', { persona: 'mia' });
      return 'Switching to Mia';
    } else if (lowerCommand.includes('switch to solene')) {
      dispatch('personaSwitch', { persona: 'solene' });
      return 'Switching to Solene';
    } else if (lowerCommand.includes('switch to lyra')) {
      dispatch('personaSwitch', { persona: 'lyra' });
      return 'Switching to Lyra';
    } else if (lowerCommand.includes('switch to doc')) {
      dispatch('personaSwitch', { persona: 'doc' });
      return 'Switching to Doc';
    }

    // App controls
    if (lowerCommand.includes('open memories')) {
      dispatch('openMemories');
      return 'Opening memories';
    } else if (lowerCommand.includes('start tracking')) {
      dispatch('startHealthTracking');
      return 'Starting health tracking';
    } else if (lowerCommand.includes('stop tracking')) {
      dispatch('stopHealthTracking');
      return 'Stopping health tracking';
    }

    // Default response
    return `I heard: "${command}". How can I help you?`;
  }

  // Export functions for external use
  export { 
    ecosystemData, 
    features, 
    connections, 
    handoffData, 
    icloudData,
    createHandoffActivity,
    shareContent,
    processVoiceCommand,
    saveToCloud
  };
</script>

<div class="apple-ecosystem">
  <!-- Device Information -->
  <div class="device-info">
    <h3>Apple Ecosystem</h3>
    
    <div class="device-details">
      <div class="device-item">
        <span class="device-icon">📱</span>
        <div class="device-text">
          <div class="device-name">{ecosystemData.deviceType.toUpperCase()}</div>
          <div class="device-version">iOS {ecosystemData.osVersion}</div>
        </div>
      </div>

      <div class="device-item">
        <span class="device-icon">🖥️</span>
        <div class="device-text">
          <div class="device-name">{ecosystemData.screenSize.width} × {ecosystemData.screenSize.height}</div>
          <div class="device-version">{ecosystemData.pixelRatio}x</div>
        </div>
      </div>

      <div class="device-item">
        <span class="device-icon">🌙</span>
        <div class="device-text">
          <div class="device-name">{ecosystemData.colorScheme}</div>
          <div class="device-version">Mode</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Feature Status -->
  <div class="features-section">
    <h4>Available Features</h4>
    
    <div class="features-grid">
      {#each Object.entries(features) as [feature, available]}
        <div class="feature-item {available ? 'available' : 'unavailable'}">
          <span class="feature-icon">
            {#if feature === 'airdrop'}📤
            {:else if feature === 'handoff'}🔄
            {:else if feature === 'icloud'}☁️
            {:else if feature === 'appleWatch'}⌚
            {:else if feature === 'siri'}🎤
            {:else if feature === 'shortcuts'}⚡
            {:else if feature === 'homekit'}🏠
            {:else if feature === 'carplay'}🚗
            {:else if feature === 'airplay'}📺
            {:else if feature === 'continuity'}🔗
            {:else if feature === 'universalControl'}🖱️
            {:else if feature === 'sidecar'}💻
            {:else}❓
            {/if}
          </span>
          <span class="feature-name">{feature.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
          <span class="feature-status">{available ? '✅' : '❌'}</span>
        </div>
      {/each}
    </div>
  </div>

  <!-- Connection Status -->
  <div class="connections-section">
    <h4>Connections</h4>
    
    <div class="connection-items">
      <!-- iCloud Sync -->
      <div class="connection-item">
        <div class="connection-header">
          <span class="connection-icon">☁️</span>
          <span class="connection-name">iCloud Sync</span>
          <span class="connection-status {connections.icloudSync.status}">
            {connections.icloudSync.status}
          </span>
        </div>
        {#if connections.icloudSync.lastSync}
          <div class="connection-details">
            Last sync: {new Date(connections.icloudSync.lastSync).toLocaleTimeString()}
          </div>
        {/if}
      </div>

      <!-- Apple Watch -->
      <div class="connection-item">
        <div class="connection-header">
          <span class="connection-icon">⌚</span>
          <span class="connection-name">Apple Watch</span>
          <span class="connection-status {connections.appleWatch.connected ? 'connected' : 'disconnected'}">
            {connections.appleWatch.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {#if connections.appleWatch.connected}
          <div class="connection-details">
            Battery: {Math.round(connections.appleWatch.batteryLevel)}% | 
            Heart Rate: {Math.round(connections.appleWatch.heartRate)} BPM
          </div>
        {/if}
      </div>

      <!-- Handoff -->
      <div class="connection-item">
        <div class="connection-header">
          <span class="connection-icon">🔄</span>
          <span class="connection-name">Handoff</span>
          <span class="connection-status {handoffData.currentActivity ? 'active' : 'inactive'}">
            {handoffData.currentActivity ? 'Active' : 'Inactive'}
          </span>
        </div>
        {#if handoffData.currentActivity}
          <div class="connection-details">
            {handoffData.currentActivity.type} activity ready
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Quick Actions -->
  <div class="actions-section">
    <h4>Quick Actions</h4>
    
    <div class="action-buttons">
      <button 
        class="action-button"
        on:click={() => createHandoffActivity('conversation', { persona: $currentPersona, timestamp: Date.now() })}
        disabled={!features.handoff}
      >
        <span class="action-icon">🔄</span>
        <span class="action-text">Create Handoff</span>
      </button>

      <button 
        class="action-button"
        on:click={() => shareContent('Check out my EmotionalAI companion!', 'app')}
        disabled={!features.airdrop}
      >
        <span class="action-icon">📤</span>
        <span class="action-text">Share App</span>
      </button>

      <button 
        class="action-button"
        on:click={() => saveToCloud('conversations', { id: Date.now(), persona: $currentPersona, timestamp: Date.now() })}
        disabled={!features.icloud}
      >
        <span class="action-icon">☁️</span>
        <span class="action-text">Sync to Cloud</span>
      </button>

      <button 
        class="action-button"
        on:click={() => processVoiceCommand('switch to mia')}
        disabled={!features.siri}
      >
        <span class="action-icon">🎤</span>
        <span class="action-text">Voice Command</span>
      </button>
    </div>
  </div>

  <!-- PWA Status -->
  <div class="pwa-status">
    <div class="status-indicator {ecosystemData.isInstalled ? 'installed' : 'not-installed'}">
      <span class="status-icon">{ecosystemData.isInstalled ? '📱' : '🌐'}</span>
      <span class="status-text">
        {ecosystemData.isInstalled ? 'Installed as App' : 'Running in Browser'}
      </span>
    </div>
  </div>
</div>

<style>
  .apple-ecosystem {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    margin: 1rem 0;
  }

  .apple-ecosystem h3 {
    margin: 0 0 1.5rem 0;
    color: #495057;
    font-size: 1.2rem;
  }

  .device-info {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .device-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .device-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .device-icon {
    font-size: 1.5rem;
  }

  .device-name {
    font-weight: 500;
    color: #495057;
    font-size: 0.875rem;
  }

  .device-version {
    font-size: 0.75rem;
    color: #6c757d;
  }

  .features-section,
  .connections-section,
  .actions-section {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .features-section h4,
  .connections-section h4,
  .actions-section h4 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1rem;
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .feature-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 6px;
    font-size: 0.875rem;
  }

  .feature-item.available {
    background: #d4edda;
    color: #155724;
  }

  .feature-item.unavailable {
    background: #f8d7da;
    color: #721c24;
    opacity: 0.7;
  }

  .feature-icon {
    font-size: 1rem;
  }

  .feature-name {
    flex: 1;
    text-transform: capitalize;
  }

  .feature-status {
    font-size: 0.75rem;
  }

  .connection-items {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .connection-item {
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 0.75rem;
  }

  .connection-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .connection-icon {
    font-size: 1.2rem;
  }

  .connection-name {
    flex: 1;
    font-weight: 500;
    color: #495057;
    font-size: 0.875rem;
  }

  .connection-status {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .connection-status.connected {
    background: #d4edda;
    color: #155724;
  }

  .connection-status.disconnected {
    background: #f8d7da;
    color: #721c24;
  }

  .connection-status.active {
    background: #d1ecf1;
    color: #0c5460;
  }

  .connection-status.inactive {
    background: #e2e3e5;
    color: #383d41;
  }

  .connection-details {
    font-size: 0.75rem;
    color: #6c757d;
    margin-left: 2.25rem;
  }

  .action-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .action-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.875rem;
  }

  .action-button:hover:not(:disabled) {
    background: #f8f9fa;
    border-color: #007bff;
  }

  .action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-icon {
    font-size: 1.5rem;
  }

  .action-text {
    font-weight: 500;
    color: #495057;
  }

  .pwa-status {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .status-icon {
    font-size: 1.2rem;
  }

  .status-text {
    font-size: 0.875rem;
    color: #495057;
    font-weight: 500;
  }

  .status-indicator.installed {
    color: #28a745;
  }

  .status-indicator.not-installed {
    color: #6c757d;
  }

  /* Mobile Optimizations */
  @media (max-width: 768px) {
    .device-details {
      grid-template-columns: 1fr;
    }

    .features-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .action-buttons {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style> 