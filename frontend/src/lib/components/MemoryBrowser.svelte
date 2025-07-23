<!-- MemoryBrowser.svelte -->
<!-- Memory Retrieval UI Component -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';
  import { memoryAPI } from '$lib/apis/persona.js';

  const dispatch = createEventDispatcher();

  // Component state
  let memories = [];
  let filteredMemories = [];
  let isLoading = false;
  let error = null;
  let searchQuery = '';
  let selectedFilters = {
    mood: 'all',
    persona: 'all',
    type: 'all',
    dateRange: 'all'
  };
  let sortBy = 'timestamp';
  let sortOrder = 'desc';
  let currentPage = 1;
  let itemsPerPage = 20;
  let totalPages = 1;

  // Memory statistics
  let memoryStats = {
    total: 0,
    byMood: {},
    byPersona: {},
    byType: {},
    recentActivity: []
  };

  // UI state
  let showFilters = false;
  let selectedMemory = null;
  let showMemoryDetail = false;
  let isExporting = false;

  // Available filter options
  const moodOptions = [
    { value: 'all', label: 'All Moods' },
    { value: 'love', label: 'Love' },
    { value: 'passion', label: 'Passion' },
    { value: 'tenderness', label: 'Tenderness' },
    { value: 'longing', label: 'Longing' },
    { value: 'excitement', label: 'Excitement' },
    { value: 'calm', label: 'Calm' },
    { value: 'sadness', label: 'Sadness' },
    { value: 'anger', label: 'Anger' }
  ];

  const personaOptions = [
    { value: 'all', label: 'All Personas' },
    { value: 'mia', label: 'Mia' },
    { value: 'solene', label: 'Solene' },
    { value: 'lyra', label: 'Lyra' },
    { value: 'doc', label: 'Doc' }
  ];

  const typeOptions = [
    { value: 'all', label: 'All Types' },
    { value: 'conversation', label: 'Conversation' },
    { value: 'emotional', label: 'Emotional' },
    { value: 'ritual', label: 'Ritual' },
    { value: 'touch', label: 'Touch' },
    { value: 'scene', label: 'Scene' },
    { value: 'symbolic', label: 'Symbolic' },
    { value: 'milestone', label: 'Milestone' }
  ];

  const dateRangeOptions = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'year', label: 'This Year' }
  ];

  // Initialize component
  onMount(async () => {
    await loadMemories();
    await loadMemoryStats();
  });

  // Load memories from API
  async function loadMemories() {
    isLoading = true;
    error = null;

    try {
      const response = await memoryAPI.getMemories({
        persona: selectedFilters.persona !== 'all' ? selectedFilters.persona : undefined,
        mood: selectedFilters.mood !== 'all' ? selectedFilters.mood : undefined,
        memory_type: selectedFilters.type !== 'all' ? selectedFilters.type : undefined,
        date_range: selectedFilters.dateRange !== 'all' ? selectedFilters.dateRange : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        page: currentPage,
        limit: itemsPerPage
      });

      if (response.success) {
        memories = response.memories || [];
        totalPages = response.total_pages || 1;
        applySearchFilter();
      } else {
        error = response.error || 'Failed to load memories';
      }
    } catch (err) {
      error = 'Network error while loading memories';
      console.error('Memory loading error:', err);
    } finally {
      isLoading = false;
    }
  }

  // Load memory statistics
  async function loadMemoryStats() {
    try {
      const response = await memoryAPI.getMemoryStats();
      if (response.success) {
        memoryStats = response.stats || memoryStats;
      }
    } catch (err) {
      console.error('Memory stats loading error:', err);
    }
  }

  // Apply search filter
  function applySearchFilter() {
    if (!searchQuery.trim()) {
      filteredMemories = memories;
      return;
    }

    const query = searchQuery.toLowerCase();
    filteredMemories = memories.filter(memory => {
      return (
        memory.content?.toLowerCase().includes(query) ||
        memory.mood?.toLowerCase().includes(query) ||
        memory.persona?.toLowerCase().includes(query) ||
        memory.memory_type?.toLowerCase().includes(query) ||
        memory.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    });
  }

  // Handle search input
  function handleSearch() {
    applySearchFilter();
    currentPage = 1;
  }

  // Handle filter changes
  function handleFilterChange() {
    currentPage = 1;
    loadMemories();
  }

  // Handle sort changes
  function handleSortChange() {
    loadMemories();
  }

  // Handle pagination
  function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
      loadMemories();
    }
  }

  // View memory detail
  function viewMemoryDetail(memory) {
    selectedMemory = memory;
    showMemoryDetail = true;
  }

  // Close memory detail
  function closeMemoryDetail() {
    showMemoryDetail = false;
    selectedMemory = null;
  }

  // Export memories
  async function exportMemories() {
    isExporting = true;
    try {
      const response = await memoryAPI.exportMemories({
        format: 'json',
        filters: selectedFilters
      });

      if (response.success) {
        // Create download link
        const blob = new Blob([JSON.stringify(response.data, null, 2)], {
          type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `memories_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      error = 'Failed to export memories';
      console.error('Export error:', err);
    } finally {
      isExporting = false;
    }
  }

  // Delete memory
  async function deleteMemory(memoryId) {
    if (!confirm('Are you sure you want to delete this memory?')) {
      return;
    }

    try {
      const response = await memoryAPI.deleteMemory(memoryId);
      if (response.success) {
        await loadMemories();
        await loadMemoryStats();
      } else {
        error = response.error || 'Failed to delete memory';
      }
    } catch (err) {
      error = 'Network error while deleting memory';
      console.error('Delete error:', err);
    }
  }

  // Format timestamp
  function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
  }

  // Get mood color
  function getMoodColor(mood) {
    const colors = {
      love: '#FF6B9D',
      passion: '#FF4757',
      tenderness: '#FFB3D1',
      longing: '#5F27CD',
      excitement: '#FF9F43',
      calm: '#54A0FF',
      sadness: '#747D8C',
      anger: '#FF3838'
    };
    return colors[mood] || '#6C757D';
  }

  // Get persona icon
  function getPersonaIcon(persona) {
    const icons = {
      mia: '💕',
      solene: '🌹',
      lyra: '✨',
      doc: '💻'
    };
    return icons[persona] || '👤';
  }

  // Reactive statements
  $: if (searchQuery !== undefined) {
    handleSearch();
  }

  $: if (selectedFilters !== undefined) {
    handleFilterChange();
  }

  $: if (sortBy !== undefined || sortOrder !== undefined) {
    handleSortChange();
  }
</script>

<div class="memory-browser">
  <!-- Header -->
  <div class="memory-header">
    <div class="header-left">
      <h2 class="memory-title">Memory Browser</h2>
      <div class="memory-stats">
        <span class="stat-item">
          <span class="stat-label">Total:</span>
          <span class="stat-value">{memoryStats.total}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">Current Persona:</span>
          <span class="stat-value">{$currentPersonaConfig?.name || 'None'}</span>
        </span>
      </div>
    </div>
    
    <div class="header-right">
      <button 
        class="btn btn-secondary" 
        on:click={() => showFilters = !showFilters}
      >
        {showFilters ? 'Hide' : 'Show'} Filters
      </button>
      <button 
        class="btn btn-primary" 
        on:click={exportMemories}
        disabled={isExporting}
      >
        {isExporting ? 'Exporting...' : 'Export'}
      </button>
    </div>
  </div>

  <!-- Search Bar -->
  <div class="search-bar">
    <div class="search-input-wrapper">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search memories..."
        class="search-input"
      />
      <span class="search-icon">🔍</span>
    </div>
  </div>

  <!-- Filters -->
  {#if showFilters}
    <div class="filters-panel">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">Mood</label>
          <select bind:value={selectedFilters.mood} class="filter-select">
            {#each moodOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Persona</label>
          <select bind:value={selectedFilters.persona} class="filter-select">
            {#each personaOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Type</label>
          <select bind:value={selectedFilters.type} class="filter-select">
            {#each typeOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Date Range</label>
          <select bind:value={selectedFilters.dateRange} class="filter-select">
            {#each dateRangeOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">Sort By</label>
          <select bind:value={sortBy} class="filter-select">
            <option value="timestamp">Date</option>
            <option value="mood">Mood</option>
            <option value="persona">Persona</option>
            <option value="type">Type</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Order</label>
          <select bind:value={sortOrder} class="filter-select">
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
        </div>
      </div>
    </div>
  {/if}

  <!-- Error Display -->
  {#if error}
    <div class="error-message">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{error}</span>
      <button class="error-close" on:click={() => error = null}>×</button>
    </div>
  {/if}

  <!-- Loading State -->
  {#if isLoading}
    <div class="loading-state">
      <div class="loading-spinner"></div>
      <span class="loading-text">Loading memories...</span>
    </div>
  {:else}
    <!-- Memory List -->
    <div class="memory-list">
      {#if filteredMemories.length === 0}
        <div class="empty-state">
          <span class="empty-icon">🧠</span>
          <h3 class="empty-title">No memories found</h3>
          <p class="empty-description">
            Try adjusting your search or filters to find memories.
          </p>
        </div>
      {:else}
        {#each filteredMemories as memory (memory.id)}
          <div class="memory-card" on:click={() => viewMemoryDetail(memory)}>
            <div class="memory-header">
              <div class="memory-meta">
                <span class="memory-persona">
                  {getPersonaIcon(memory.persona)} {memory.persona}
                </span>
                <span class="memory-type">{memory.memory_type}</span>
                <span class="memory-date">{formatTimestamp(memory.timestamp)}</span>
              </div>
              
              <div class="memory-actions">
                <button 
                  class="btn-icon"
                  on:click|stopPropagation={() => deleteMemory(memory.id)}
                  title="Delete memory"
                >
                  🗑️
                </button>
              </div>
            </div>
            
            <div class="memory-content">
              <p class="memory-text">{memory.content}</p>
            </div>
            
            <div class="memory-footer">
              <div class="memory-mood">
                <span 
                  class="mood-indicator"
                  style="background-color: {getMoodColor(memory.mood)}"
                ></span>
                <span class="mood-text">{memory.mood}</span>
              </div>
              
              {#if memory.tags && memory.tags.length > 0}
                <div class="memory-tags">
                  {#each memory.tags as tag}
                    <span class="memory-tag">{tag}</span>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/each}
      {/if}
    </div>

    <!-- Pagination -->
    {#if totalPages > 1}
      <div class="pagination">
        <button 
          class="btn-page"
          disabled={currentPage === 1}
          on:click={() => goToPage(currentPage - 1)}
        >
          ← Previous
        </button>
        
        <div class="page-numbers">
          {#each Array(totalPages) as _, i}
            {#if i + 1 === currentPage || i + 1 === 1 || i + 1 === totalPages || (i + 1 >= currentPage - 1 && i + 1 <= currentPage + 1)}
              <button 
                class="btn-page {i + 1 === currentPage ? 'active' : ''}"
                on:click={() => goToPage(i + 1)}
              >
                {i + 1}
              </button>
            {:else if i + 1 === currentPage - 2 || i + 1 === currentPage + 2}
              <span class="page-ellipsis">...</span>
            {/if}
          {/each}
        </div>
        
        <button 
          class="btn-page"
          disabled={currentPage === totalPages}
          on:click={() => goToPage(currentPage + 1)}
        >
          Next →
        </button>
      </div>
    {/if}
  {/if}
</div>

<!-- Memory Detail Modal -->
{#if showMemoryDetail && selectedMemory}
  <div class="modal-overlay" on:click={closeMemoryDetail}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3 class="modal-title">Memory Detail</h3>
        <button class="modal-close" on:click={closeMemoryDetail}>×</button>
      </div>
      
      <div class="modal-body">
        <div class="memory-detail-meta">
          <div class="detail-item">
            <span class="detail-label">Persona:</span>
            <span class="detail-value">
              {getPersonaIcon(selectedMemory.persona)} {selectedMemory.persona}
            </span>
          </div>
          
          <div class="detail-item">
            <span class="detail-label">Type:</span>
            <span class="detail-value">{selectedMemory.memory_type}</span>
          </div>
          
          <div class="detail-item">
            <span class="detail-label">Mood:</span>
            <span class="detail-value">
              <span 
                class="mood-indicator"
                style="background-color: {getMoodColor(selectedMemory.mood)}"
              ></span>
              {selectedMemory.mood}
            </span>
          </div>
          
          <div class="detail-item">
            <span class="detail-label">Date:</span>
            <span class="detail-value">{formatTimestamp(selectedMemory.timestamp)}</span>
          </div>
        </div>
        
        <div class="memory-detail-content">
          <h4 class="detail-section-title">Content</h4>
          <p class="detail-text">{selectedMemory.content}</p>
        </div>
        
        {#if selectedMemory.tags && selectedMemory.tags.length > 0}
          <div class="memory-detail-tags">
            <h4 class="detail-section-title">Tags</h4>
            <div class="detail-tags">
              {#each selectedMemory.tags as tag}
                <span class="detail-tag">{tag}</span>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if selectedMemory.emotional_weight}
          <div class="memory-detail-emotion">
            <h4 class="detail-section-title">Emotional Weight</h4>
            <div class="emotion-weight">
              <div class="weight-bar">
                <div 
                  class="weight-fill"
                  style="width: {selectedMemory.emotional_weight * 100}%"
                ></div>
              </div>
              <span class="weight-value">{Math.round(selectedMemory.emotional_weight * 100)}%</span>
            </div>
          </div>
        {/if}
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={closeMemoryDetail}>
          Close
        </button>
        <button 
          class="btn btn-danger" 
          on:click={() => {
            deleteMemory(selectedMemory.id);
            closeMemoryDetail();
          }}
        >
          Delete Memory
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .memory-browser {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }

  .memory-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
  }

  .memory-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: #2D3748;
    margin: 0 0 0.5rem 0;
  }

  .memory-stats {
    display: flex;
    gap: 1rem;
  }

  .stat-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #718096;
  }

  .stat-value {
    font-weight: 600;
    color: #2D3748;
  }

  .header-right {
    display: flex;
    gap: 0.5rem;
  }

  .search-bar {
    margin-bottom: 1rem;
  }

  .search-input-wrapper {
    position: relative;
    max-width: 400px;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-size: 1rem;
    background: white;
  }

  .search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: #A0AEC0;
  }

  .filters-panel {
    background: #F7FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .filter-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .filter-row:last-child {
    margin-bottom: 0;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .filter-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #4A5568;
  }

  .filter-select {
    padding: 0.5rem;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    background: white;
    font-size: 0.875rem;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #FED7D7;
    border: 1px solid #FEB2B2;
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 1rem;
  }

  .error-icon {
    font-size: 1.2rem;
  }

  .error-text {
    color: #C53030;
    font-size: 0.875rem;
  }

  .error-close {
    background: none;
    border: none;
    color: #C53030;
    font-size: 1.2rem;
    cursor: pointer;
    margin-left: auto;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    gap: 1rem;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #E2E8F0;
    border-top: 4px solid #4299E1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .loading-text {
    color: #718096;
    font-size: 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .memory-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .memory-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .memory-card:hover {
    border-color: #4299E1;
    box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
  }

  .memory-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }

  .memory-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: #718096;
  }

  .memory-persona {
    font-weight: 500;
    color: #4A5568;
  }

  .memory-actions {
    display: flex;
    gap: 0.25rem;
  }

  .btn-icon {
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .btn-icon:hover {
    background: #F7FAFC;
  }

  .memory-content {
    margin-bottom: 0.75rem;
  }

  .memory-text {
    color: #2D3748;
    line-height: 1.5;
    margin: 0;
  }

  .memory-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .memory-mood {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .mood-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }

  .mood-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: #4A5568;
  }

  .memory-tags {
    display: flex;
    gap: 0.25rem;
  }

  .memory-tag {
    background: #EDF2F7;
    color: #4A5568;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    text-align: center;
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .empty-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #4A5568;
    margin: 0 0 0.5rem 0;
  }

  .empty-description {
    color: #718096;
    margin: 0;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
  }

  .btn-page {
    padding: 0.5rem 1rem;
    border: 1px solid #E2E8F0;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-page:hover:not(:disabled) {
    border-color: #4299E1;
    background: #EBF8FF;
  }

  .btn-page.active {
    background: #4299E1;
    color: white;
    border-color: #4299E1;
  }

  .btn-page:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .page-numbers {
    display: flex;
    gap: 0.25rem;
  }

  .page-ellipsis {
    padding: 0.5rem;
    color: #718096;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #E2E8F0;
  }

  .modal-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #718096;
  }

  .modal-body {
    padding: 1rem;
  }

  .memory-detail-meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .detail-label {
    font-size: 0.875rem;
    color: #718096;
  }

  .detail-value {
    font-weight: 500;
    color: #2D3748;
  }

  .detail-section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #2D3748;
    margin: 0 0 0.5rem 0;
  }

  .detail-text {
    color: #2D3748;
    line-height: 1.6;
    margin: 0 0 1rem 0;
  }

  .detail-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .detail-tag {
    background: #EDF2F7;
    color: #4A5568;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .emotion-weight {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .weight-bar {
    flex: 1;
    height: 8px;
    background: #E2E8F0;
    border-radius: 4px;
    overflow: hidden;
  }

  .weight-fill {
    height: 100%;
    background: #4299E1;
    transition: width 0.3s ease;
  }

  .weight-value {
    font-weight: 600;
    color: #2D3748;
    min-width: 40px;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 1rem;
    border-top: 1px solid #E2E8F0;
  }

  .btn {
    padding: 0.5rem 1rem;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }

  .btn-primary {
    background: #4299E1;
    color: white;
    border-color: #4299E1;
  }

  .btn-primary:hover {
    background: #3182CE;
  }

  .btn-secondary {
    background: white;
    color: #4A5568;
  }

  .btn-secondary:hover {
    background: #F7FAFC;
  }

  .btn-danger {
    background: #F56565;
    color: white;
    border-color: #F56565;
  }

  .btn-danger:hover {
    background: #E53E3E;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .memory-header {
      flex-direction: column;
      gap: 1rem;
    }

    .header-right {
      align-self: stretch;
    }

    .filter-row {
      flex-direction: column;
      gap: 0.5rem;
    }

    .memory-meta {
      flex-direction: column;
      gap: 0.25rem;
    }

    .memory-footer {
      flex-direction: column;
      gap: 0.5rem;
      align-items: flex-start;
    }

    .pagination {
      flex-direction: column;
      gap: 0.5rem;
    }

    .page-numbers {
      order: -1;
    }
  }
</style> 