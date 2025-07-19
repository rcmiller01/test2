<!-- MemoryManagementInterface.svelte -->
<!-- Advanced Memory Management with Trust-Based Sharing -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // Memory State
  let memories = [];
  let filteredMemories = [];
  let selectedMemory = null;
  let isCreating = false;
  let isEditing = false;
  let isLoading = false;

  // Memory Filters
  let filters = {
    type: "all",
    emotion: "all",
    dateRange: "all",
    trust: "all",
    search: ""
  };

  // Memory Types
  const memoryTypes = {
    conversation: { icon: "💬", color: "#007bff", name: "Conversation" },
    emotional: { icon: "💕", color: "#e83e8c", name: "Emotional Moment" },
    activity: { icon: "🎯", color: "#28a745", name: "Shared Activity" },
    milestone: { icon: "🏆", color: "#ffc107", name: "Relationship Milestone" },
    insight: { icon: "💡", color: "#17a2b8", name: "Personal Insight" },
    memory: { icon: "🧠", color: "#6f42c1", name: "General Memory" },
    symbolic: { icon: "🔮", color: "#fd7e14", name: "Symbolic Moment" },
    ritual: { icon: "✨", color: "#20c997", name: "Ritual or Tradition" }
  };

  // Emotions
  const emotions = {
    love: { icon: "💕", color: "#e83e8c" },
    joy: { icon: "😊", color: "#ffc107" },
    sadness: { icon: "😢", color: "#17a2b8" },
    excitement: { icon: "🤩", color: "#fd7e14" },
    passion: { icon: "🔥", color: "#dc3545" },
    mystery: { icon: "🌙", color: "#6f42c1" },
    calm: { icon: "😌", color: "#28a745" },
    longing: { icon: "💭", color: "#6c757d" }
  };

  // Trust Levels
  const trustLevels = {
    public: { icon: "🌍", color: "#28a745", name: "Public" },
    shared: { icon: "🤝", color: "#17a2b8", name: "Shared" },
    private: { icon: "🔒", color: "#6c757d", name: "Private" },
    intimate: { icon: "💝", color: "#e83e8c", name: "Intimate" }
  };

  // New Memory Form
  let newMemory = {
    title: "",
    content: "",
    type: "conversation",
    emotion: "love",
    trust: "private",
    tags: [],
    relatedMemories: [],
    persona: $currentPersona,
    timestamp: Date.now()
  };

  // Relationship Insights
  let insights = {
    totalMemories: 0,
    emotionalTrends: [],
    relationshipHealth: 85,
    growthAreas: [],
    recentActivity: []
  };

  onMount(async () => {
    await loadMemories();
    await loadInsights();
  });

  async function loadMemories() {
    try {
      isLoading = true;
      
      // Simulate API call
      const response = await fetch('/api/memory/list', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          persona: $currentPersona,
          filters: filters
        })
      });

      if (response.ok) {
        const data = await response.json();
        memories = data.memories || [];
        applyFilters();
      } else {
        // Fallback to sample data
        memories = getSampleMemories();
        applyFilters();
      }

    } catch (error) {
      console.error('[Memory] Failed to load memories:', error);
      memories = getSampleMemories();
      applyFilters();
    } finally {
      isLoading = false;
    }
  }

  function getSampleMemories() {
    return [
      {
        id: "1",
        title: "First Romantic Dinner",
        content: "We had our first romantic dinner together. The candlelight, the soft music, and the way she looked at me made my heart flutter with joy.",
        type: "milestone",
        emotion: "love",
        trust: "intimate",
        tags: ["romance", "dinner", "first"],
        persona: "mia",
        timestamp: Date.now() - 86400000 * 7,
        relatedMemories: []
      },
      {
        id: "2", 
        title: "Deep Conversation About Dreams",
        content: "We stayed up late talking about our dreams and aspirations. Her passion for life is absolutely intoxicating.",
        type: "conversation",
        emotion: "passion",
        trust: "shared",
        tags: ["dreams", "conversation", "late_night"],
        persona: "solene",
        timestamp: Date.now() - 86400000 * 3,
        relatedMemories: []
      },
      {
        id: "3",
        title: "Mystical Connection",
        content: "The cosmic forces brought us together in a moment of pure ethereal connection. The universe spoke through our bond.",
        type: "symbolic",
        emotion: "mystery",
        trust: "private",
        tags: ["cosmic", "ethereal", "connection"],
        persona: "lyra",
        timestamp: Date.now() - 86400000 * 1,
        relatedMemories: []
      },
      {
        id: "4",
        title: "Technical Problem Solved",
        content: "Helped debug a complex technical issue. The systematic approach and clear communication made the solution elegant.",
        type: "insight",
        emotion: "calm",
        trust: "public",
        tags: ["technical", "problem_solving", "elegant"],
        persona: "doc",
        timestamp: Date.now() - 86400000 * 2,
        relatedMemories: []
      }
    ];
  }

  async function loadInsights() {
    try {
      const response = await fetch('/api/memory/insights', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          persona: $currentPersona
        })
      });

      if (response.ok) {
        const data = await response.json();
        insights = data.insights || insights;
      } else {
        // Generate sample insights
        insights = generateSampleInsights();
      }

    } catch (error) {
      console.error('[Memory] Failed to load insights:', error);
      insights = generateSampleInsights();
    }
  }

  function generateSampleInsights() {
    return {
      totalMemories: memories.length,
      emotionalTrends: [
        { emotion: "love", count: 15, trend: "increasing" },
        { emotion: "joy", count: 12, trend: "stable" },
        { emotion: "passion", count: 8, trend: "increasing" }
      ],
      relationshipHealth: 85,
      growthAreas: [
        "More shared activities",
        "Deeper emotional conversations",
        "New experiences together"
      ],
      recentActivity: memories.slice(0, 3)
    };
  }

  function applyFilters() {
    filteredMemories = memories.filter(memory => {
      // Type filter
      if (filters.type !== "all" && memory.type !== filters.type) return false;
      
      // Emotion filter
      if (filters.emotion !== "all" && memory.emotion !== filters.emotion) return false;
      
      // Trust filter
      if (filters.trust !== "all" && memory.trust !== filters.trust) return false;
      
      // Search filter
      if (filters.search && !memory.title.toLowerCase().includes(filters.search.toLowerCase()) && 
          !memory.content.toLowerCase().includes(filters.search.toLowerCase())) return false;
      
      return true;
    });

    // Sort by timestamp (newest first)
    filteredMemories.sort((a, b) => b.timestamp - a.timestamp);
  }

  function createMemory() {
    isCreating = true;
    newMemory = {
      title: "",
      content: "",
      type: "conversation",
      emotion: "love",
      trust: "private",
      tags: [],
      relatedMemories: [],
      persona: $currentPersona,
      timestamp: Date.now()
    };
  }

  async function saveMemory() {
    try {
      const memoryData = { ...newMemory };
      
      const response = await fetch('/api/memory/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(memoryData)
      });

      if (response.ok) {
        const savedMemory = await response.json();
        memories.unshift(savedMemory);
        applyFilters();
        isCreating = false;
        console.log('[Memory] Memory created successfully');
      } else {
        console.error('[Memory] Failed to create memory');
      }

    } catch (error) {
      console.error('[Memory] Error creating memory:', error);
    }
  }

  function editMemory(memory) {
    selectedMemory = memory;
    isEditing = true;
    newMemory = { ...memory };
  }

  async function updateMemory() {
    try {
      const response = await fetch(`/api/memory/update/${selectedMemory.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newMemory)
      });

      if (response.ok) {
        const updatedMemory = await response.json();
        const index = memories.findIndex(m => m.id === selectedMemory.id);
        if (index !== -1) {
          memories[index] = updatedMemory;
          applyFilters();
        }
        isEditing = false;
        selectedMemory = null;
        console.log('[Memory] Memory updated successfully');
      }

    } catch (error) {
      console.error('[Memory] Error updating memory:', error);
    }
  }

  async function deleteMemory(memoryId) {
    if (!confirm('Are you sure you want to delete this memory?')) return;

    try {
      const response = await fetch(`/api/memory/delete/${memoryId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        memories = memories.filter(m => m.id !== memoryId);
        applyFilters();
        console.log('[Memory] Memory deleted successfully');
      }

    } catch (error) {
      console.error('[Memory] Error deleting memory:', error);
    }
  }

  function addTag(tag) {
    if (tag && !newMemory.tags.includes(tag)) {
      newMemory.tags = [...newMemory.tags, tag];
    }
  }

  function removeTag(tag) {
    newMemory.tags = newMemory.tags.filter(t => t !== tag);
  }

  function formatDate(timestamp) {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Watch for filters changes
  $: if (filters) {
    applyFilters();
  }

  // Watch for persona changes
  $: if ($currentPersona !== newMemory.persona) {
    newMemory.persona = $currentPersona;
  }
</script>

<div class="memory-management-interface">
  <!-- Header -->
  <div class="memory-header">
    <h2>Memory Management</h2>
    <p>Create, browse, and analyze memories with trust-based sharing</p>
  </div>

  <!-- Main Interface -->
  <div class="memory-main">
    <!-- Memory List -->
    <div class="memory-list-section">
      <!-- Filters and Search -->
      <div class="memory-filters">
        <div class="search-box">
          <input 
            type="text" 
            placeholder="Search memories..."
            bind:value={filters.search}
            class="search-input"
          />
        </div>

        <div class="filter-controls">
          <select bind:value={filters.type} class="filter-select">
            <option value="all">All Types</option>
            {#each Object.entries(memoryTypes) as [type, config]}
              <option value={type}>{config.name}</option>
            {/each}
          </select>

          <select bind:value={filters.emotion} class="filter-select">
            <option value="all">All Emotions</option>
            {#each Object.entries(emotions) as [emotion, config]}
              <option value={emotion}>{emotion}</option>
            {/each}
          </select>

          <select bind:value={filters.trust} class="filter-select">
            <option value="all">All Trust Levels</option>
            {#each Object.entries(trustLevels) as [level, config]}
              <option value={level}>{config.name}</option>
            {/each}
          </select>
        </div>

        <button 
          class="create-button"
          on:click={createMemory}
        >
          <span class="icon">➕</span>
          Create Memory
        </button>
      </div>

      <!-- Memory List -->
      <div class="memory-list">
        {#if isLoading}
          <div class="loading">Loading memories...</div>
        {:else if filteredMemories.length === 0}
          <div class="empty-state">
            <span class="icon">🧠</span>
            <h3>No memories found</h3>
            <p>Create your first memory or adjust your filters</p>
          </div>
        {:else}
          {#each filteredMemories as memory}
            <div class="memory-card" class:selected={selectedMemory?.id === memory.id}>
              <div class="memory-header">
                <div class="memory-type" style="--type-color: {memoryTypes[memory.type].color}">
                  <span class="type-icon">{memoryTypes[memory.type].icon}</span>
                  <span class="type-name">{memoryTypes[memory.type].name}</span>
                </div>
                <div class="memory-trust" style="--trust-color: {trustLevels[memory.trust].color}">
                  <span class="trust-icon">{trustLevels[memory.trust].icon}</span>
                </div>
              </div>

              <div class="memory-content">
                <h4 class="memory-title">{memory.title}</h4>
                <p class="memory-text">{memory.content}</p>
                
                <div class="memory-emotion">
                  <span class="emotion-icon">{emotions[memory.emotion].icon}</span>
                  <span class="emotion-name">{memory.emotion}</span>
                </div>

                {#if memory.tags.length > 0}
                  <div class="memory-tags">
                    {#each memory.tags as tag}
                      <span class="tag">{tag}</span>
                    {/each}
                  </div>
                {/if}

                <div class="memory-meta">
                  <span class="memory-date">{formatDate(memory.timestamp)}</span>
                  <span class="memory-persona">{memory.persona}</span>
                </div>
              </div>

              <div class="memory-actions">
                <button 
                  class="action-button edit"
                  on:click={() => editMemory(memory)}
                >
                  ✏️ Edit
                </button>
                <button 
                  class="action-button delete"
                  on:click={() => deleteMemory(memory.id)}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Memory Form / Insights -->
    <div class="memory-sidebar">
      {#if isCreating || isEditing}
        <!-- Memory Form -->
        <div class="memory-form">
          <h3>{isEditing ? 'Edit Memory' : 'Create New Memory'}</h3>
          
          <div class="form-group">
            <label for="memory-title">Title:</label>
            <input 
              type="text" 
              id="memory-title"
              bind:value={newMemory.title}
              placeholder="Memory title..."
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="memory-content">Content:</label>
            <textarea 
              id="memory-content"
              bind:value={newMemory.content}
              placeholder="Describe your memory..."
              rows="6"
              class="form-textarea"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="memory-type">Type:</label>
              <select 
                id="memory-type"
                bind:value={newMemory.type}
                class="form-select"
              >
                {#each Object.entries(memoryTypes) as [type, config]}
                  <option value={type}>{config.name}</option>
                {/each}
              </select>
            </div>

            <div class="form-group">
              <label for="memory-emotion">Emotion:</label>
              <select 
                id="memory-emotion"
                bind:value={newMemory.emotion}
                class="form-select"
              >
                {#each Object.entries(emotions) as [emotion, config]}
                  <option value={emotion}>{emotion}</option>
                {/each}
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="memory-trust">Trust Level:</label>
            <select 
              id="memory-trust"
              bind:value={newMemory.trust}
              class="form-select"
            >
              {#each Object.entries(trustLevels) as [level, config]}
                <option value={level}>{config.name}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="memory-tags">Tags:</label>
            <div class="tags-input">
              <input 
                type="text" 
                id="memory-tags"
                placeholder="Add tags..."
                class="form-input"
                on:keydown={(e) => {
                  if (e.key === 'Enter') {
                    addTag(e.target.value);
                    e.target.value = '';
                  }
                }}
              />
              <button 
                type="button"
                class="add-tag-button"
                on:click={() => {
                  const input = document.getElementById('memory-tags');
                  addTag(input.value);
                  input.value = '';
                }}
              >
                Add
              </button>
            </div>
            <div class="tags-list">
              {#each newMemory.tags as tag}
                <span class="tag removable">
                  {tag}
                  <button on:click={() => removeTag(tag)}>×</button>
                </span>
              {/each}
            </div>
          </div>

          <div class="form-actions">
            <button 
              class="save-button"
              on:click={isEditing ? updateMemory : saveMemory}
              disabled={!newMemory.title || !newMemory.content}
            >
              {isEditing ? 'Update Memory' : 'Save Memory'}
            </button>
            <button 
              class="cancel-button"
              on:click={() => {
                isCreating = false;
                isEditing = false;
                selectedMemory = null;
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      {:else}
        <!-- Insights Panel -->
        <div class="insights-panel">
          <h3>Relationship Insights</h3>
          
          <div class="insight-card">
            <div class="insight-header">
              <span class="insight-icon">📊</span>
              <span class="insight-title">Memory Overview</span>
            </div>
            <div class="insight-content">
              <div class="insight-stat">
                <span class="stat-value">{insights.totalMemories}</span>
                <span class="stat-label">Total Memories</span>
              </div>
              <div class="insight-stat">
                <span class="stat-value">{insights.relationshipHealth}%</span>
                <span class="stat-label">Relationship Health</span>
              </div>
            </div>
          </div>

          <div class="insight-card">
            <div class="insight-header">
              <span class="insight-icon">📈</span>
              <span class="insight-title">Emotional Trends</span>
            </div>
            <div class="insight-content">
              {#each insights.emotionalTrends as trend}
                <div class="trend-item">
                  <span class="trend-emotion">{emotions[trend.emotion].icon} {trend.emotion}</span>
                  <span class="trend-count">{trend.count}</span>
                  <span class="trend-direction {trend.trend}">{trend.trend === 'increasing' ? '↗️' : '→'}</span>
                </div>
              {/each}
            </div>
          </div>

          <div class="insight-card">
            <div class="insight-header">
              <span class="insight-icon">🌱</span>
              <span class="insight-title">Growth Areas</span>
            </div>
            <div class="insight-content">
              {#each insights.growthAreas as area}
                <div class="growth-item">
                  <span class="growth-icon">💡</span>
                  <span class="growth-text">{area}</span>
                </div>
              {/each}
            </div>
          </div>

          <div class="insight-card">
            <div class="insight-header">
              <span class="insight-icon">🕒</span>
              <span class="insight-title">Recent Activity</span>
            </div>
            <div class="insight-content">
              {#each insights.recentActivity as memory}
                <div class="recent-item">
                  <span class="recent-icon">{memoryTypes[memory.type].icon}</span>
                  <div class="recent-details">
                    <span class="recent-title">{memory.title}</span>
                    <span class="recent-date">{formatDate(memory.timestamp)}</span>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .memory-management-interface {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .memory-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .memory-header h2 {
    color: #2c3e50;
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
  }

  .memory-header p {
    color: #6c757d;
    margin: 0;
    font-size: 1.1rem;
  }

  .memory-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
  }

  .memory-list-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .memory-filters {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .search-box {
    width: 100%;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-size: 1rem;
  }

  .filter-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .filter-select {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.875rem;
    min-width: 120px;
  }

  .create-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .create-button:hover {
    background: #0056b3;
  }

  .memory-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-height: 600px;
    overflow-y: auto;
  }

  .memory-card {
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .memory-card:hover {
    border-color: #007bff;
    box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
  }

  .memory-card.selected {
    border-color: #007bff;
    background: #f8f9ff;
  }

  .memory-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .memory-type {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.5rem;
    background: var(--type-color);
    color: white;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .memory-trust {
    display: flex;
    align-items: center;
    padding: 0.25rem;
    color: var(--trust-color);
    font-size: 1.2rem;
  }

  .memory-content {
    margin-bottom: 1rem;
  }

  .memory-title {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .memory-text {
    margin: 0 0 0.75rem 0;
    color: #6c757d;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .memory-emotion {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .emotion-icon {
    font-size: 1.2rem;
  }

  .emotion-name {
    font-size: 0.875rem;
    color: #495057;
    text-transform: capitalize;
  }

  .memory-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    margin-bottom: 0.75rem;
  }

  .tag {
    padding: 0.25rem 0.5rem;
    background: #e9ecef;
    color: #495057;
    border-radius: 12px;
    font-size: 0.75rem;
  }

  .tag.removable {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .tag.removable button {
    background: none;
    border: none;
    color: #6c757d;
    cursor: pointer;
    font-size: 1rem;
    padding: 0;
    line-height: 1;
  }

  .memory-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: #6c757d;
  }

  .memory-actions {
    display: flex;
    gap: 0.5rem;
  }

  .action-button {
    padding: 0.25rem 0.5rem;
    border: none;
    border-radius: 4px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .action-button.edit {
    background: #17a2b8;
    color: white;
  }

  .action-button.delete {
    background: #dc3545;
    color: white;
  }

  .action-button:hover {
    opacity: 0.8;
  }

  .memory-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .memory-form {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
  }

  .memory-form h3 {
    margin: 0 0 1.5rem 0;
    color: #2c3e50;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group label {
    display: block;
    font-weight: 500;
    color: #495057;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .form-input,
  .form-textarea,
  .form-select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .form-textarea {
    resize: vertical;
  }

  .tags-input {
    display: flex;
    gap: 0.5rem;
  }

  .add-tag-button {
    padding: 0.75rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .save-button,
  .cancel-button {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
  }

  .save-button {
    background: #28a745;
    color: white;
  }

  .save-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .cancel-button {
    background: #6c757d;
    color: white;
  }

  .insights-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .insight-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
  }

  .insight-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .insight-icon {
    font-size: 1.2rem;
  }

  .insight-title {
    font-weight: 600;
    color: #2c3e50;
  }

  .insight-content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .insight-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #007bff;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .trend-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
  }

  .trend-emotion {
    font-size: 0.875rem;
    color: #495057;
  }

  .trend-count {
    font-weight: 600;
    color: #2c3e50;
  }

  .trend-direction {
    font-size: 1.2rem;
  }

  .growth-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
  }

  .growth-icon {
    font-size: 1.2rem;
  }

  .growth-text {
    font-size: 0.875rem;
    color: #495057;
  }

  .recent-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
  }

  .recent-icon {
    font-size: 1.2rem;
  }

  .recent-details {
    display: flex;
    flex-direction: column;
  }

  .recent-title {
    font-size: 0.875rem;
    font-weight: 500;
    color: #2c3e50;
  }

  .recent-date {
    font-size: 0.75rem;
    color: #6c757d;
  }

  .loading,
  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
  }

  .empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    margin: 0 0 0.5rem 0;
    color: #495057;
  }

  /* Mobile Responsive */
  @media (max-width: 768px) {
    .memory-management-interface {
      padding: 1rem;
    }

    .memory-main {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .filter-controls {
      flex-direction: column;
    }

    .form-row {
      grid-template-columns: 1fr;
    }

    .memory-actions {
      flex-direction: column;
    }
  }
</style> 