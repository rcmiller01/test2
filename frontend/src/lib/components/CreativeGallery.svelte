<!-- CreativeGallery.svelte -->
<!-- Display Generated Creative Content Gallery -->

<script>
  import { onMount } from 'svelte';
  import { currentPersona } from '$lib/stores/personaStore.js';
  import { toast } from '$lib/stores/toastStore.js';

  // Component state
  let creativeContent = [];
  let isLoading = false;
  let selectedContent = null;
  let showContentModal = false;
  let filterType = 'all';
  let filterStyle = 'all';
  let filterTimeframe = '30d';
  let searchQuery = '';
  let sortBy = 'newest';

  // Content types for filtering
  const contentTypes = [
    { id: 'all', name: 'All Content', icon: '📚' },
    { id: 'story', name: 'Stories', icon: '📖' },
    { id: 'poem', name: 'Poems', icon: '🎭' },
    { id: 'dream', name: 'Dreams', icon: '🌙' },
    { id: 'interactive', name: 'Interactive', icon: '🎮' },
    { id: 'memory', name: 'Memories', icon: '💭' },
    { id: 'comfort', name: 'Comfort', icon: '🤗' },
    { id: 'celebration', name: 'Celebration', icon: '🎉' },
    { id: 'prompt', name: 'Prompts', icon: '💡' },
    { id: 'symbolic', name: 'Symbolic', icon: '🎨' },
    { id: 'collaborative', name: 'Collaborative', icon: '🤝' }
  ];

  // Style filters
  const styleFilters = [
    { id: 'all', name: 'All Styles' },
    { id: 'whimsical', name: 'Whimsical' },
    { id: 'contemplative', name: 'Contemplative' },
    { id: 'romantic', name: 'Romantic' },
    { id: 'adventurous', name: 'Adventurous' },
    { id: 'mystical', name: 'Mystical' },
    { id: 'comforting', name: 'Comforting' },
    { id: 'nostalgic', name: 'Nostalgic' },
    { id: 'inspirational', name: 'Inspirational' },
    { id: 'surreal', name: 'Surreal' },
    { id: 'intimate', name: 'Intimate' }
  ];

  // Timeframe filters
  const timeframeFilters = [
    { id: '24h', name: 'Last 24 Hours', days: 1 },
    { id: '7d', name: 'Last Week', days: 7 },
    { id: '30d', name: 'Last Month', days: 30 },
    { id: '90d', name: 'Last 3 Months', days: 90 },
    { id: 'all', name: 'All Time', days: null }
  ];

  // Sort options
  const sortOptions = [
    { id: 'newest', name: 'Newest First' },
    { id: 'oldest', name: 'Oldest First' },
    { id: 'liked', name: 'Most Liked' },
    { id: 'type', name: 'Content Type' },
    { id: 'style', name: 'Style' }
  ];

  onMount(async () => {
    await loadCreativeContent();
  });

  // Reactive filtering and sorting
  $: filteredContent = creativeContent
    .filter(content => {
      // Type filter
      if (filterType !== 'all' && content.type !== filterType) return false;
      
      // Style filter
      if (filterStyle !== 'all' && content.style !== filterStyle) return false;
      
      // Search filter
      if (searchQuery && !content.title?.toLowerCase().includes(searchQuery.toLowerCase()) && 
          !content.content?.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      
      // Timeframe filter
      if (filterTimeframe !== 'all') {
        const timeframe = timeframeFilters.find(t => t.id === filterTimeframe);
        if (timeframe?.days) {
          const contentDate = new Date(content.created_at);
          const cutoffDate = new Date(Date.now() - (timeframe.days * 24 * 60 * 60 * 1000));
          if (contentDate < cutoffDate) return false;
        }
      }
      
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'liked':
          return (b.likes || 0) - (a.likes || 0);
        case 'type':
          return a.type.localeCompare(b.type);
        case 'style':
          return a.style.localeCompare(b.style);
        default:
          return 0;
      }
    });

  async function loadCreativeContent() {
    try {
      isLoading = true;
      const response = await fetch('/api/creative/content/gallery', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        creativeContent = await response.json();
      } else {
        throw new Error('Failed to load creative content');
      }
    } catch (error) {
      console.error('Failed to load creative content:', error);
      toast.error('Failed to load creative gallery');
    } finally {
      isLoading = false;
    }
  }

  async function likeContent(contentId) {
    try {
      const response = await fetch(`/api/creative/content/${contentId}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        // Update local state
        creativeContent = creativeContent.map(content => 
          content.id === contentId 
            ? { ...content, likes: (content.likes || 0) + 1, user_liked: true }
            : content
        );
        
        if (selectedContent && selectedContent.id === contentId) {
          selectedContent.likes = (selectedContent.likes || 0) + 1;
          selectedContent.user_liked = true;
        }
      } else {
        throw new Error('Failed to like content');
      }
    } catch (error) {
      console.error('Failed to like content:', error);
      toast.error('Failed to like content');
    }
  }

  async function saveContent(contentId) {
    try {
      const response = await fetch(`/api/creative/content/${contentId}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        // Update local state
        creativeContent = creativeContent.map(content => 
          content.id === contentId 
            ? { ...content, user_saved: true }
            : content
        );
        
        if (selectedContent && selectedContent.id === contentId) {
          selectedContent.user_saved = true;
        }
        
        toast.success('Content saved to your collection');
      } else {
        throw new Error('Failed to save content');
      }
    } catch (error) {
      console.error('Failed to save content:', error);
      toast.error('Failed to save content');
    }
  }

  async function shareContent(contentId) {
    try {
      if (navigator.share) {
        await navigator.share({
          title: selectedContent?.title || 'Creative Content',
          text: selectedContent?.content?.substring(0, 100) + '...',
          url: window.location.href
        });
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(selectedContent?.content || '');
        toast.success('Content copied to clipboard');
      }
    } catch (error) {
      console.error('Failed to share content:', error);
      toast.error('Failed to share content');
    }
  }

  async function regenerateContent(contentId) {
    try {
      const response = await fetch(`/api/creative/content/${contentId}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const newContent = await response.json();
        // Add new content to gallery
        creativeContent.unshift(newContent);
        creativeContent = creativeContent; // Trigger reactivity
        toast.success('Content regenerated successfully');
      } else {
        throw new Error('Failed to regenerate content');
      }
    } catch (error) {
      console.error('Failed to regenerate content:', error);
      toast.error('Failed to regenerate content');
    }
  }

  function openContentModal(content) {
    selectedContent = content;
    showContentModal = true;
  }

  function closeContentModal() {
    selectedContent = null;
    showContentModal = false;
  }

  function getContentTypeInfo(typeId) {
    return contentTypes.find(type => type.id === typeId) || contentTypes[0];
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }

  function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString();
  }

  function truncateContent(content, maxLength = 150) {
    if (!content) return '';
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  }

  function getTimeAgo(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    const diffInWeeks = Math.floor(diffInDays / 7);
    if (diffInWeeks < 4) return `${diffInWeeks}w ago`;
    
    return formatDate(dateString);
  }
</script>

<div class="creative-gallery bg-gray-900 text-white p-6 rounded-lg">
  <div class="gallery-header mb-6">
    <h2 class="text-2xl font-bold mb-2 flex items-center">
      🎨 Creative Gallery
      {#if $currentPersona}
        <span class="ml-2 text-lg text-gray-400">- {$currentPersona}</span>
      {/if}
    </h2>
    <p class="text-gray-400 mb-4">
      Browse and manage all your collaboratively created content
    </p>

    <!-- Search and Filters -->
    <div class="filters-section space-y-4">
      <!-- Search Bar -->
      <div class="search-bar">
        <input 
          type="text" 
          bind:value={searchQuery}
          placeholder="Search content..." 
          class="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
        />
      </div>

      <!-- Filter Controls -->
      <div class="filter-controls grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Content Type Filter -->
        <div>
          <label class="block text-sm font-medium mb-2">Content Type</label>
          <select bind:value={filterType} class="w-full p-2 bg-gray-800 border border-gray-700 rounded">
            {#each contentTypes as type}
              <option value={type.id}>{type.icon} {type.name}</option>
            {/each}
          </select>
        </div>

        <!-- Style Filter -->
        <div>
          <label class="block text-sm font-medium mb-2">Style</label>
          <select bind:value={filterStyle} class="w-full p-2 bg-gray-800 border border-gray-700 rounded">
            {#each styleFilters as style}
              <option value={style.id}>{style.name}</option>
            {/each}
          </select>
        </div>

        <!-- Timeframe Filter -->
        <div>
          <label class="block text-sm font-medium mb-2">Timeframe</label>
          <select bind:value={filterTimeframe} class="w-full p-2 bg-gray-800 border border-gray-700 rounded">
            {#each timeframeFilters as timeframe}
              <option value={timeframe.id}>{timeframe.name}</option>
            {/each}
          </select>
        </div>

        <!-- Sort Options -->
        <div>
          <label class="block text-sm font-medium mb-2">Sort By</label>
          <select bind:value={sortBy} class="w-full p-2 bg-gray-800 border border-gray-700 rounded">
            {#each sortOptions as option}
              <option value={option.id}>{option.name}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- Results Summary -->
      <div class="results-summary flex items-center justify-between text-sm text-gray-400">
        <span>
          Showing {filteredContent.length} of {creativeContent.length} items
        </span>
        <button 
          class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          on:click={loadCreativeContent}
        >
          🔄 Refresh
        </button>
      </div>
    </div>
  </div>

  {#if isLoading}
    <div class="loading-state text-center py-12">
      <div class="animate-spin text-4xl mb-4">🎨</div>
      <div>Loading creative gallery...</div>
    </div>
  {:else if filteredContent.length === 0}
    <div class="no-content bg-gray-800 p-8 rounded-lg text-center">
      <div class="text-4xl mb-4">📚</div>
      <h3 class="text-lg font-semibold mb-2">
        {creativeContent.length === 0 ? 'No Creative Content Yet' : 'No Content Matches Your Filters'}
      </h3>
      <p class="text-gray-400 mb-4">
        {creativeContent.length === 0 
          ? 'Start creating content with your AI companion to build your gallery'
          : 'Try adjusting your filters to see more content'}
      </p>
      {#if creativeContent.length === 0}
        <button class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium">
          Create Your First Content
        </button>
      {:else}
        <button 
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium"
          on:click={() => {
            filterType = 'all';
            filterStyle = 'all';
            filterTimeframe = 'all';
            searchQuery = '';
          }}
        >
          Clear All Filters
        </button>
      {/if}
    </div>
  {:else}
    <!-- Content Grid -->
    <div class="content-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each filteredContent as content}
        {@const typeInfo = getContentTypeInfo(content.type)}
        <div 
          class="content-card bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
          on:click={() => openContentModal(content)}
        >
          <!-- Content Header -->
          <div class="content-header p-4 pb-2">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center">
                <span class="text-xl mr-2">{typeInfo.icon}</span>
                <div>
                  <h3 class="font-medium">{content.title || typeInfo.name}</h3>
                  <div class="text-sm text-gray-400">{content.style} • {getTimeAgo(content.created_at)}</div>
                </div>
              </div>
              
              <div class="flex items-center gap-1 text-sm text-gray-400">
                {#if content.likes > 0}
                  <span class="flex items-center">
                    <span class="mr-1">👍</span>
                    {content.likes}
                  </span>
                {/if}
                {#if content.user_saved}
                  <span class="text-yellow-400">⭐</span>
                {/if}
              </div>
            </div>
          </div>

          <!-- Content Preview -->
          <div class="content-preview p-4 pt-0">
            <div class="text-sm text-gray-300 line-clamp-4 leading-relaxed">
              {truncateContent(content.content)}
            </div>
          </div>

          <!-- Content Footer -->
          <div class="content-footer p-4 pt-2 border-t border-gray-700">
            <div class="flex items-center justify-between">
              <div class="text-xs text-gray-500">
                {content.word_count || 0} words
              </div>
              
              <div class="flex gap-2">
                <button 
                  class="p-1 hover:bg-gray-700 rounded text-sm {content.user_liked ? 'text-green-400' : 'text-gray-400'}"
                  on:click|stopPropagation={() => !content.user_liked && likeContent(content.id)}
                  title="Like"
                >
                  👍
                </button>
                
                <button 
                  class="p-1 hover:bg-gray-700 rounded text-sm {content.user_saved ? 'text-yellow-400' : 'text-gray-400'}"
                  on:click|stopPropagation={() => !content.user_saved && saveContent(content.id)}
                  title="Save"
                >
                  ⭐
                </button>
                
                <button 
                  class="p-1 hover:bg-gray-700 rounded text-sm text-gray-400"
                  on:click|stopPropagation={() => shareContent(content.id)}
                  title="Share"
                >
                  📤
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Load More Button (if applicable) -->
    {#if filteredContent.length >= 20}
      <div class="load-more text-center mt-6">
        <button class="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded font-medium">
          Load More Content
        </button>
      </div>
    {/if}
  {/if}
</div>

<!-- Content Detail Modal -->
{#if showContentModal && selectedContent}
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeContentModal}>
    <div class="modal-content bg-gray-800 p-6 rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" on:click|stopPropagation>
      <div class="modal-header flex items-center justify-between mb-4">
        <div>
          <h3 class="text-xl font-bold flex items-center">
            <span class="text-2xl mr-2">{getContentTypeInfo(selectedContent.type).icon}</span>
            {selectedContent.title || getContentTypeInfo(selectedContent.type).name}
          </h3>
          <div class="text-sm text-gray-400 flex items-center gap-4">
            <span>{selectedContent.style} style</span>
            <span>•</span>
            <span>{selectedContent.theme} theme</span>
            <span>•</span>
            <span>Created {formatDateTime(selectedContent.created_at)}</span>
          </div>
        </div>
        
        <button 
          class="text-gray-400 hover:text-white text-2xl"
          on:click={closeContentModal}
        >
          ×
        </button>
      </div>

      <div class="modal-body space-y-6">
        <!-- Content Actions -->
        <div class="content-actions flex gap-2 flex-wrap">
          <button 
            class="px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center"
            class:opacity-50={selectedContent.user_liked}
            on:click={() => !selectedContent.user_liked && likeContent(selectedContent.id)}
            disabled={selectedContent.user_liked}
          >
            👍 {selectedContent.user_liked ? 'Liked' : 'Like'} ({selectedContent.likes || 0})
          </button>
          
          <button 
            class="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm flex items-center"
            class:opacity-50={selectedContent.user_saved}
            on:click={() => !selectedContent.user_saved && saveContent(selectedContent.id)}
            disabled={selectedContent.user_saved}
          >
            ⭐ {selectedContent.user_saved ? 'Saved' : 'Save'}
          </button>
          
          <button 
            class="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center"
            on:click={() => shareContent(selectedContent.id)}
          >
            📤 Share
          </button>
          
          <button 
            class="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm flex items-center"
            on:click={() => regenerateContent(selectedContent.id)}
          >
            🔄 Regenerate
          </button>
        </div>

        <!-- Content Display -->
        <div class="content-display bg-gray-900 p-6 rounded-lg">
          <div class="prose prose-invert max-w-none">
            <div class="whitespace-pre-wrap leading-relaxed text-gray-200">
              {selectedContent.content}
            </div>
          </div>

          <!-- Interactive Elements -->
          {#if selectedContent.choices && selectedContent.choices.length > 0}
            <div class="interactive-choices mt-6">
              <h4 class="font-medium mb-3">Choose what happens next:</h4>
              <div class="space-y-2">
                {#each selectedContent.choices as choice, index}
                  <button class="block w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded border border-gray-600">
                    {index + 1}. {choice}
                  </button>
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <!-- Content Metadata -->
        <div class="content-metadata bg-gray-900 p-4 rounded-lg">
          <h4 class="font-medium mb-3">Content Details</h4>
          <div class="metadata-grid grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div class="text-gray-400">Type</div>
              <div>{getContentTypeInfo(selectedContent.type).name}</div>
            </div>
            <div>
              <div class="text-gray-400">Style</div>
              <div class="capitalize">{selectedContent.style}</div>
            </div>
            <div>
              <div class="text-gray-400">Theme</div>
              <div class="capitalize">{selectedContent.theme}</div>
            </div>
            <div>
              <div class="text-gray-400">Word Count</div>
              <div>{selectedContent.word_count || 0}</div>
            </div>
          </div>

          {#if selectedContent.generation_context}
            <div class="generation-context mt-4">
              <div class="text-gray-400 text-sm">Generation Context</div>
              <div class="text-xs text-gray-500">{selectedContent.generation_context}</div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .line-clamp-4 {
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .modal-content::-webkit-scrollbar {
    width: 4px;
  }
  
  .modal-content::-webkit-scrollbar-track {
    background: #374151;
  }
  
  .modal-content::-webkit-scrollbar-thumb {
    background: #6366f1;
    border-radius: 2px;
  }

  .prose {
    line-height: 1.7;
  }
</style>
