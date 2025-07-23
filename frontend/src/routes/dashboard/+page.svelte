<!-- Dashboard Page -->
<!-- Comprehensive Phase 3 Features Dashboard -->

<script>
  import { onMount } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';
  
  import EmotionalTTSInterface from '$lib/components/EmotionalTTSInterface.svelte';
  import AvatarManagementInterface from '$lib/components/AvatarManagementInterface.svelte';
  import MemoryManagementInterface from '$lib/components/MemoryManagementInterface.svelte';
  import Phase3FeaturesInterface from '$lib/components/Phase3FeaturesInterface.svelte';
  import MobileVoiceIntegration from '$lib/components/MobileVoiceIntegration.svelte';
  import MobileSensors from '$lib/components/MobileSensors.svelte';
  import HealthIntegration from '$lib/components/HealthIntegration.svelte';
  import AppleEcosystem from '$lib/components/AppleEcosystem.svelte';

  // Dashboard State
  let currentTab = 'overview';
  let systemStatus = {
    backend: 'connected',
    tts: 'available',
    avatar: 'active',
    memory: 'connected',
    phase3: 'ready',
    mobile: 'available'
  };

  // Available tabs
  const tabs = [
    { id: 'overview', name: 'Overview', icon: '🏠', description: 'System overview and quick actions' },
    { id: 'voice', name: 'Voice & TTS', icon: '🎤', description: 'Emotional voice synthesis and recognition' },
    { id: 'avatar', name: 'Avatar', icon: '👤', description: 'Real-time avatar management and animations' },
    { id: 'memory', name: 'Memory', icon: '🧠', description: 'Memory management and relationship insights' },
    { id: 'phase3', name: 'Phase 3', icon: '🚀', description: 'Advanced features: haptic, biometric, VR, AI' },
    { id: 'mobile', name: 'Mobile', icon: '📱', description: 'iPhone capabilities and mobile integration' }
  ];

  // Persona configurations
  const personas = {
    mia: { name: 'Mia', icon: '💕', color: '#e83e8c', description: 'Warm, affectionate romantic companion' },
    solene: { name: 'Solene', icon: '🌙', color: '#6f42c1', description: 'Sophisticated, mysterious romantic companion' },
    lyra: { name: 'Lyra', icon: '✨', color: '#17a2b8', description: 'Mystical, ethereal entity' },
    doc: { name: 'Doc', icon: '💼', color: '#495057', description: 'Professional coding assistant' }
  };

  // Quick actions
  const quickActions = [
    { name: 'Start Voice Chat', icon: '🎤', action: () => switchTab('voice'), color: '#007bff' },
    { name: 'View Avatar', icon: '👤', action: () => switchTab('avatar'), color: '#28a745' },
    { name: 'Browse Memories', icon: '🧠', action: () => switchTab('memory'), color: '#ffc107' },
    { name: 'Phase 3 Features', icon: '🚀', action: () => switchTab('phase3'), color: '#dc3545' },
    { name: 'Mobile Integration', icon: '📱', action: () => switchTab('mobile'), color: '#6f42c1' }
  ];

  onMount(async () => {
    await checkSystemStatus();
  });

  async function checkSystemStatus() {
    try {
      // Check backend connectivity
      const response = await fetch('/api/health');
      if (response.ok) {
        systemStatus.backend = 'connected';
      } else {
        systemStatus.backend = 'disconnected';
      }
    } catch (error) {
      systemStatus.backend = 'error';
      console.error('[Dashboard] Backend health check failed:', error);
    }
  }

  function switchTab(tabId) {
    currentTab = tabId;
  }

  function switchPersona(personaId) {
    $currentPersona = personaId;
  }

  function getStatusColor(status) {
    switch (status) {
      case 'connected':
      case 'available':
      case 'active':
      case 'ready':
        return '#28a745';
      case 'disconnected':
      case 'unavailable':
      case 'inactive':
        return '#dc3545';
      case 'error':
        return '#ffc107';
      default:
        return '#6c757d';
    }
  }

  function getStatusIcon(status) {
    switch (status) {
      case 'connected':
      case 'available':
      case 'active':
      case 'ready':
        return '✅';
      case 'disconnected':
      case 'unavailable':
      case 'inactive':
        return '❌';
      case 'error':
        return '⚠️';
      default:
        return '⏸️';
    }
  }
</script>

<svelte:head>
  <title>Phase 3 Dashboard - {$currentPersonaConfig?.name || 'EmotionalAI'}</title>
  <meta name="description" content="Advanced Phase 3 features dashboard with voice, avatar, memory, and mobile integration" />
</svelte:head>

<div class="dashboard-container">
  <!-- Header -->
  <header class="dashboard-header">
    <div class="header-content">
      <div class="header-left">
        <h1>Phase 3 Dashboard</h1>
        <p>Advanced emotional AI companion system</p>
      </div>
      
      <div class="header-right">
        <div class="persona-selector">
          <span class="current-persona">
            {personas[$currentPersona].icon} {$currentPersonaConfig?.name || personas[$currentPersona].name}
          </span>
          <div class="persona-dropdown">
            {#each Object.entries(personas) as [id, persona]}
              <button 
                class="persona-option {id === $currentPersona ? 'active' : ''}"
                on:click={() => switchPersona(id)}
                style="--persona-color: {persona.color}"
              >
                <span class="persona-icon">{persona.icon}</span>
                <span class="persona-name">{persona.name}</span>
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <nav class="dashboard-nav">
    <div class="nav-tabs">
      {#each tabs as tab}
        <button 
          class="nav-tab {currentTab === tab.id ? 'active' : ''}"
          on:click={() => switchTab(tab.id)}
        >
          <span class="tab-icon">{tab.icon}</span>
          <span class="tab-name">{tab.name}</span>
        </button>
      {/each}
    </div>
  </nav>

  <!-- Main Content -->
  <main class="dashboard-main">
    {#if currentTab === 'overview'}
      <!-- Overview Tab -->
      <div class="overview-content">
        <!-- System Status -->
        <div class="status-section">
          <h2>System Status</h2>
          <div class="status-grid">
            {#each Object.entries(systemStatus) as [service, status]}
              <div class="status-card">
                <div class="status-icon" style="color: {getStatusColor(status)}">
                  {getStatusIcon(status)}
                </div>
                <div class="status-info">
                  <span class="status-name">{service}</span>
                  <span class="status-value">{status}</span>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="actions-section">
          <h2>Quick Actions</h2>
          <div class="actions-grid">
            {#each quickActions as action}
              <button 
                class="action-card"
                on:click={action.action}
                style="--action-color: {action.color}"
              >
                <span class="action-icon">{action.icon}</span>
                <span class="action-name">{action.name}</span>
              </button>
            {/each}
          </div>
        </div>

        <!-- Current Persona Info -->
        <div class="persona-section">
          <h2>Current Persona: {$currentPersonaConfig?.name || personas[$currentPersona].name}</h2>
          <div class="persona-card">
            <div class="persona-avatar">
              <span class="avatar-icon">{personas[$currentPersona].icon}</span>
            </div>
            <div class="persona-details">
              <h3>{personas[$currentPersona].name}</h3>
              <p>{personas[$currentPersona].description}</p>
              <div class="persona-features">
                <span class="feature">Voice Synthesis</span>
                <span class="feature">Avatar Animation</span>
                <span class="feature">Memory System</span>
                <span class="feature">Phase 3 Features</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="activity-section">
          <h2>Recent Activity</h2>
          <div class="activity-list">
            <div class="activity-item">
              <span class="activity-icon">🎤</span>
              <div class="activity-content">
                <span class="activity-title">Voice synthesis ready</span>
                <span class="activity-time">Just now</span>
              </div>
            </div>
            <div class="activity-item">
              <span class="activity-icon">👤</span>
              <div class="activity-content">
                <span class="activity-title">Avatar system active</span>
                <span class="activity-time">2 minutes ago</span>
              </div>
            </div>
            <div class="activity-item">
              <span class="activity-icon">🧠</span>
              <div class="activity-content">
                <span class="activity-title">Memory system connected</span>
                <span class="activity-time">5 minutes ago</span>
              </div>
            </div>
            <div class="activity-item">
              <span class="activity-icon">🚀</span>
              <div class="activity-content">
                <span class="activity-title">Phase 3 features loaded</span>
                <span class="activity-time">10 minutes ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    {:else if currentTab === 'voice'}
      <!-- Voice & TTS Tab -->
      <div class="tab-content">
        <EmotionalTTSInterface />
      </div>

    {:else if currentTab === 'avatar'}
      <!-- Avatar Tab -->
      <div class="tab-content">
        <AvatarManagementInterface />
      </div>

    {:else if currentTab === 'memory'}
      <!-- Memory Tab -->
      <div class="tab-content">
        <MemoryManagementInterface />
      </div>

    {:else if currentTab === 'phase3'}
      <!-- Phase 3 Tab -->
      <div class="tab-content">
        <Phase3FeaturesInterface />
      </div>

    {:else if currentTab === 'mobile'}
      <!-- Mobile Tab -->
      <div class="tab-content">
        <div class="mobile-integration">
          <h2>Mobile Integration</h2>
          <p>iPhone capabilities and mobile features</p>
          
          <div class="mobile-components">
            <div class="mobile-component">
              <h3>Voice Integration</h3>
              <MobileVoiceIntegration />
            </div>
            
            <div class="mobile-component">
              <h3>Device Sensors</h3>
              <MobileSensors />
            </div>
            
            <div class="mobile-component">
              <h3>Health Integration</h3>
              <HealthIntegration />
            </div>
            
            <div class="mobile-component">
              <h3>Apple Ecosystem</h3>
              <AppleEcosystem />
            </div>
          </div>
        </div>
      </div>
    {/if}
  </main>

  <!-- Footer -->
  <footer class="dashboard-footer">
    <div class="footer-content">
      <span class="footer-text">
        Phase 3 Dashboard - {$currentPersonaConfig?.name || 'EmotionalAI'} - {new Date().toLocaleDateString()}
      </span>
      <span class="footer-status">
        System: {systemStatus.backend} | TTS: {systemStatus.tts} | Avatar: {systemStatus.avatar}
      </span>
    </div>
  </footer>
</div>

<style>
  .dashboard-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    flex-direction: column;
  }

  .dashboard-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 2rem;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
  }

  .header-left h1 {
    margin: 0 0 0.25rem 0;
    color: #2c3e50;
    font-size: 1.8rem;
  }

  .header-left p {
    margin: 0;
    color: #6c757d;
    font-size: 1rem;
  }

  .persona-selector {
    position: relative;
    display: inline-block;
  }

  .current-persona {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    color: #495057;
  }

  .persona-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    min-width: 200px;
    display: none;
  }

  .persona-selector:hover .persona-dropdown {
    display: block;
  }

  .persona-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .persona-option:hover {
    background: #f8f9fa;
  }

  .persona-option.active {
    background: var(--persona-color);
    color: white;
  }

  .persona-icon {
    font-size: 1.2rem;
  }

  .persona-name {
    font-weight: 500;
  }

  .dashboard-nav {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0 2rem;
  }

  .nav-tabs {
    display: flex;
    max-width: 1400px;
    margin: 0 auto;
    gap: 0.5rem;
    padding: 1rem 0;
  }

  .nav-tab {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #6c757d;
    font-weight: 500;
  }

  .nav-tab:hover {
    background: rgba(0, 123, 255, 0.1);
    color: #007bff;
  }

  .nav-tab.active {
    background: #007bff;
    color: white;
  }

  .tab-icon {
    font-size: 1.2rem;
  }

  .dashboard-main {
    flex: 1;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  .tab-content {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  /* Overview Styles */
  .overview-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .status-section,
  .actions-section,
  .persona-section,
  .activity-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .status-section,
  .persona-section {
    grid-column: 1 / -1;
  }

  .status-section h2,
  .actions-section h2,
  .persona-section h2,
  .activity-section h2 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 1.3rem;
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .status-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }

  .status-icon {
    font-size: 1.5rem;
  }

  .status-info {
    display: flex;
    flex-direction: column;
  }

  .status-name {
    font-weight: 600;
    color: #495057;
    text-transform: capitalize;
  }

  .status-value {
    font-size: 0.875rem;
    color: #6c757d;
    text-transform: capitalize;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .action-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem;
    background: white;
    border: 2px solid var(--action-color);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--action-color);
  }

  .action-card:hover {
    background: var(--action-color);
    color: white;
    transform: translateY(-2px);
  }

  .action-icon {
    font-size: 2rem;
  }

  .action-name {
    font-weight: 600;
    text-align: center;
  }

  .persona-card {
    display: flex;
    align-items: center;
    gap: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 12px;
  }

  .persona-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: {personas[$currentPersona].color};
    border-radius: 50%;
    color: white;
  }

  .avatar-icon {
    font-size: 2.5rem;
  }

  .persona-details h3 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 1.5rem;
  }

  .persona-details p {
    margin: 0 0 1rem 0;
    color: #6c757d;
  }

  .persona-features {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .feature {
    padding: 0.25rem 0.75rem;
    background: #e9ecef;
    color: #495057;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .activity-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .activity-icon {
    font-size: 1.5rem;
  }

  .activity-content {
    display: flex;
    flex-direction: column;
  }

  .activity-title {
    font-weight: 500;
    color: #495057;
  }

  .activity-time {
    font-size: 0.875rem;
    color: #6c757d;
  }

  /* Mobile Integration Styles */
  .mobile-integration {
    padding: 2rem;
  }

  .mobile-integration h2 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
  }

  .mobile-integration p {
    margin: 0 0 2rem 0;
    color: #6c757d;
  }

  .mobile-components {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .mobile-component {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
  }

  .mobile-component h3 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
  }

  .dashboard-footer {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 2rem;
  }

  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
    font-size: 0.875rem;
    color: #6c757d;
  }

  /* Mobile Responsive */
  @media (max-width: 768px) {
    .dashboard-header {
      padding: 1rem;
    }

    .header-content {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }

    .nav-tabs {
      padding: 0.5rem;
      overflow-x: auto;
    }

    .nav-tab {
      white-space: nowrap;
    }

    .dashboard-main {
      padding: 1rem;
    }

    .overview-content {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .persona-card {
      flex-direction: column;
      text-align: center;
    }

    .footer-content {
      flex-direction: column;
      gap: 0.5rem;
      text-align: center;
    }
  }
</style> 