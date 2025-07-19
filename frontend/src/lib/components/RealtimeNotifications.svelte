<!-- RealtimeNotifications.svelte -->
<!-- Real-time Notification System for EmotionalAI Phase 3 Features -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { 
    realtimeMemory, 
    realtimeEvents, 
    realtimeAvatar, 
    realtimeHaptic, 
    realtimeBiometric, 
    realtimeVR, 
    realtimeVoice,
    realtimeRelationship,
    realtimeStatus
  } from '$lib/stores/realtimeStore.js';
  import { realtimeActions } from '$lib/stores/realtimeStore.js';

  // Notification state
  let notifications = [];
  let isExpanded = false;
  let autoHide = true;
  let notificationTimeout = 5000; // 5 seconds

  // Notification types and their configurations
  const notificationTypes = {
    memory: {
      icon: '🧠',
      color: '#28a745',
      title: 'Memory Update',
      sound: '/audio/notification.mp3'
    },
    avatar: {
      icon: '👤',
      color: '#007bff',
      title: 'Avatar Update',
      sound: null
    },
    haptic: {
      icon: '📳',
      color: '#ffc107',
      title: 'Haptic Feedback',
      sound: null
    },
    biometric: {
      icon: '❤️',
      color: '#dc3545',
      title: 'Biometric Data',
      sound: null
    },
    vr: {
      icon: '🥽',
      color: '#6f42c1',
      title: 'VR Experience',
      sound: null
    },
    voice: {
      icon: '🎤',
      color: '#17a2b8',
      title: 'Voice Activity',
      sound: null
    },
    relationship: {
      icon: '💕',
      color: '#e83e8c',
      title: 'Relationship Insight',
      sound: '/audio/greeting.mp3'
    },
    system: {
      icon: '⚙️',
      color: '#6c757d',
      title: 'System Event',
      sound: null
    },
    recommendation: {
      icon: '💡',
      color: '#fd7e14',
      title: 'Recommendation',
      sound: '/audio/notification.mp3'
    }
  };

  onMount(() => {
    // Listen for custom notification events
    document.addEventListener('notification', handleCustomNotification);
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  });

  onDestroy(() => {
    document.removeEventListener('notification', handleCustomNotification);
  });

  // Handle custom notification events
  function handleCustomNotification(event) {
    const { title, message, type, timestamp } = event.detail;
    addNotification({
      id: timestamp || Date.now(),
      type: type || 'system',
      title,
      message,
      timestamp: timestamp || Date.now(),
      isRead: false
    });
  }

  // Add a new notification
  function addNotification(notification) {
    notifications = [notification, ...notifications].slice(0, 20); // Keep last 20
    
    // Play sound if configured
    const config = notificationTypes[notification.type];
    if (config?.sound) {
      playNotificationSound(config.sound);
    }

    // Auto-hide after timeout
    if (autoHide) {
      setTimeout(() => {
        removeNotification(notification.id);
      }, notificationTimeout);
    }
  }

  // Remove a notification
  function removeNotification(id) {
    notifications = notifications.filter(n => n.id !== id);
  }

  // Mark notification as read
  function markAsRead(id) {
    notifications = notifications.map(n => 
      n.id === id ? { ...n, isRead: true } : n
    );
  }

  // Play notification sound
  function playNotificationSound(soundPath) {
    try {
      const audio = new Audio(soundPath);
      audio.volume = 0.5;
      audio.play().catch(err => console.log('Audio play failed:', err));
    } catch (error) {
      console.log('Audio not available:', error);
    }
  }

  // Toggle expanded view
  function toggleExpanded() {
    isExpanded = !isExpanded;
  }

  // Clear all notifications
  function clearAll() {
    notifications = [];
  }

  // Get notification count
  $: unreadCount = notifications.filter(n => !n.isRead).length;
  $: totalCount = notifications.length;

  // Watch for real-time updates and create notifications
  $: if ($realtimeMemory.notifications.length > 0) {
    const latest = $realtimeMemory.notifications[$realtimeMemory.notifications.length - 1];
    if (!notifications.find(n => n.id === latest.id)) {
      addNotification({
        ...latest,
        type: 'memory'
      });
    }
  }

  $: if ($realtimeEvents.events.length > 0) {
    const latest = $realtimeEvents.events[$realtimeEvents.events.length - 1];
    if (!notifications.find(n => n.id === latest.id)) {
      addNotification({
        ...latest,
        type: 'system'
      });
    }
  }

  $: if ($realtimeRelationship.recentInsights.length > 0) {
    const latest = $realtimeRelationship.recentInsights[$realtimeRelationship.recentInsights.length - 1];
    if (!notifications.find(n => n.id === latest.id)) {
      addNotification({
        ...latest,
        type: 'relationship'
      });
    }
  }

  $: if ($realtimeRelationship.recommendations.length > 0) {
    const latest = $realtimeRelationship.recommendations[$realtimeRelationship.recommendations.length - 1];
    if (!notifications.find(n => n.id === latest.id)) {
      addNotification({
        ...latest,
        type: 'recommendation'
      });
    }
  }

  // Watch for avatar state changes
  $: if ($realtimeAvatar.lastUpdate) {
    const avatarNotification = {
      id: $realtimeAvatar.lastUpdate,
      type: 'avatar',
      title: 'Avatar Updated',
      message: `Mood: ${$realtimeAvatar.currentMood}, Expression: ${$realtimeAvatar.currentExpression}`,
      timestamp: $realtimeAvatar.lastUpdate,
      isRead: false
    };
    
    if (!notifications.find(n => n.id === avatarNotification.id)) {
      addNotification(avatarNotification);
    }
  }

  // Watch for haptic triggers
  $: if ($realtimeHaptic.lastTrigger) {
    const hapticNotification = {
      id: $realtimeHaptic.lastTrigger,
      type: 'haptic',
      title: 'Haptic Feedback',
      message: `Pattern: ${$realtimeHaptic.currentPattern}, Intensity: ${$realtimeHaptic.intensity}%`,
      timestamp: $realtimeHaptic.lastTrigger,
      isRead: false
    };
    
    if (!notifications.find(n => n.id === hapticNotification.id)) {
      addNotification(hapticNotification);
    }
  }

  // Watch for VR scene changes
  $: if ($realtimeVR.lastUpdate) {
    const vrNotification = {
      id: $realtimeVR.lastUpdate,
      type: 'vr',
      title: 'VR Experience',
      message: $realtimeVR.isActive 
        ? `Scene: ${$realtimeVR.currentScene}, Progress: ${Math.round($realtimeVR.sceneProgress)}%`
        : 'VR session ended',
      timestamp: $realtimeVR.lastUpdate,
      isRead: false
    };
    
    if (!notifications.find(n => n.id === vrNotification.id)) {
      addNotification(vrNotification);
    }
  }

  // Watch for voice activity
  $: if ($realtimeVoice.lastUtterance) {
    const voiceNotification = {
      id: $realtimeVoice.lastUtterance,
      type: 'voice',
      title: 'Voice Activity',
      message: $realtimeVoice.isSpeaking 
        ? `Speaking with ${$realtimeVoice.emotion} emotion`
        : 'Voice session ended',
      timestamp: $realtimeVoice.lastUtterance,
      isRead: false
    };
    
    if (!notifications.find(n => n.id === voiceNotification.id)) {
      addNotification(voiceNotification);
    }
  }

  // Format timestamp
  function formatTime(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return new Date(timestamp).toLocaleDateString();
  }
</script>

<div class="realtime-notifications">
  <!-- Notification Bell -->
  <div class="notification-bell" on:click={toggleExpanded}>
    <div class="bell-icon">
      🔔
      {#if unreadCount > 0}
        <span class="notification-badge">{unreadCount}</span>
      {/if}
    </div>
    
    <!-- Connection Status -->
    <div class="connection-status {$realtimeStatus.isConnected ? 'connected' : 'disconnected'}">
      <span class="status-dot"></span>
    </div>
  </div>

  <!-- Notification Panel -->
  {#if isExpanded}
    <div class="notification-panel">
      <div class="panel-header">
        <h3>Real-time Updates</h3>
        <div class="panel-controls">
          <button class="control-btn" on:click={clearAll} title="Clear all">
            🗑️
          </button>
          <button class="control-btn" on:click={toggleExpanded} title="Close">
            ✕
          </button>
        </div>
      </div>

      <!-- System Status -->
      <div class="system-status">
        <div class="status-item">
          <span class="status-icon">👤</span>
          <span class="status-text">{$realtimeStatus.systemHealth.avatar}</span>
        </div>
        <div class="status-item">
          <span class="status-icon">🧠</span>
          <span class="status-text">{$realtimeStatus.systemHealth.memory}</span>
        </div>
        <div class="status-item">
          <span class="status-icon">📳</span>
          <span class="status-text">{$realtimeStatus.systemHealth.haptic}</span>
        </div>
        <div class="status-item">
          <span class="status-icon">❤️</span>
          <span class="status-text">{$realtimeStatus.systemHealth.biometric}</span>
        </div>
        <div class="status-item">
          <span class="status-icon">🥽</span>
          <span class="status-text">{$realtimeStatus.systemHealth.vr}</span>
        </div>
        <div class="status-item">
          <span class="status-icon">🎤</span>
          <span class="status-text">{$realtimeStatus.systemHealth.voice}</span>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="notifications-list">
        {#if notifications.length === 0}
          <div class="empty-state">
            <span class="empty-icon">📭</span>
            <p>No notifications yet</p>
            <small>Real-time updates will appear here</small>
          </div>
        {:else}
          {#each notifications as notification (notification.id)}
            <div 
              class="notification-item {notification.isRead ? 'read' : 'unread'}"
              style="--notification-color: {notificationTypes[notification.type]?.color || '#6c757d'}"
            >
              <div class="notification-icon">
                {notificationTypes[notification.type]?.icon || '📢'}
              </div>
              
              <div class="notification-content">
                <div class="notification-header">
                  <span class="notification-title">{notification.title}</span>
                  <span class="notification-time">{formatTime(notification.timestamp)}</span>
                </div>
                
                <p class="notification-message">{notification.message}</p>
                
                <div class="notification-actions">
                  {#if !notification.isRead}
                    <button 
                      class="action-btn"
                      on:click={() => markAsRead(notification.id)}
                    >
                      Mark Read
                    </button>
                  {/if}
                  <button 
                    class="action-btn"
                    on:click={() => removeNotification(notification.id)}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          {/each}
        {/if}
      </div>

      <!-- Panel Footer -->
      <div class="panel-footer">
        <span class="footer-text">
          {totalCount} total, {unreadCount} unread
        </span>
        <label class="auto-hide-toggle">
          <input type="checkbox" bind:checked={autoHide}>
          Auto-hide
        </label>
      </div>
    </div>
  {/if}
</div>

<style>
  .realtime-notifications {
    position: relative;
    display: inline-block;
  }

  .notification-bell {
    position: relative;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    transition: background-color 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .notification-bell:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }

  .bell-icon {
    position: relative;
    font-size: 1.5rem;
  }

  .notification-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    background: #dc3545;
    color: white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }

  .connection-status {
    display: flex;
    align-items: center;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #dc3545;
    transition: background-color 0.3s ease;
  }

  .connection-status.connected .status-dot {
    background: #28a745;
  }

  .notification-panel {
    position: absolute;
    top: 100%;
    right: 0;
    width: 400px;
    max-height: 600px;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    overflow: hidden;
    margin-top: 0.5rem;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
    background: #f8f9fa;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #495057;
  }

  .panel-controls {
    display: flex;
    gap: 0.5rem;
  }

  .control-btn {
    background: none;
    border: none;
    padding: 0.25rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .control-btn:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }

  .system-status {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  .status-icon {
    font-size: 1rem;
  }

  .status-text {
    color: #6c757d;
    text-transform: capitalize;
  }

  .notifications-list {
    max-height: 400px;
    overflow-y: auto;
    padding: 0.5rem;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
  }

  .empty-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
  }

  .notification-item {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border-left: 4px solid var(--notification-color);
    background: white;
    transition: all 0.2s ease;
  }

  .notification-item:hover {
    background: #f8f9fa;
  }

  .notification-item.unread {
    background: #f8f9fa;
    border-left-width: 6px;
  }

  .notification-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  .notification-content {
    flex: 1;
    min-width: 0;
  }

  .notification-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .notification-title {
    font-weight: 600;
    color: #495057;
    font-size: 0.9rem;
  }

  .notification-time {
    font-size: 0.75rem;
    color: #6c757d;
    flex-shrink: 0;
  }

  .notification-message {
    margin: 0 0 0.75rem 0;
    font-size: 0.875rem;
    color: #6c757d;
    line-height: 1.4;
  }

  .notification-actions {
    display: flex;
    gap: 0.5rem;
  }

  .action-btn {
    background: none;
    border: 1px solid #dee2e6;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .action-btn:hover {
    background: #f8f9fa;
    border-color: #adb5bd;
  }

  .panel-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-top: 1px solid #dee2e6;
    background: #f8f9fa;
  }

  .footer-text {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .auto-hide-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #6c757d;
    cursor: pointer;
  }

  .auto-hide-toggle input {
    margin: 0;
  }

  /* Mobile responsive */
  @media (max-width: 768px) {
    .notification-panel {
      position: fixed;
      top: 0;
      right: 0;
      left: 0;
      bottom: 0;
      width: 100%;
      max-height: none;
      border-radius: 0;
      margin-top: 0;
    }

    .system-status {
      grid-template-columns: repeat(2, 1fr);
    }

    .notifications-list {
      max-height: none;
      flex: 1;
    }
  }
</style> 