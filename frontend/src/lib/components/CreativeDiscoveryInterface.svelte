<!-- CreativeDiscoveryInterface.svelte -->
<!-- Dynamic Creative Model Integration and Interest Discovery -->

<script>
  import { onMount } from 'svelte';
  import { currentPersona } from '$lib/stores/personaStore.js';
  import { toast } from '$lib/stores/toastStore.js';

  // Component state
  let userProfile = null;
  let availableModels = {};
  let suggestedActivities = [];
  let collaborationHistory = null;
  let creativeInterests = [];
  let isLoading = false;
  let activeTab = 'discovery';
  
  // Model installation state
  let installingModels = new Set();
  let installationProgress = {};
  
  // Content creation state
  let contentCreationForm = {
    mediaType: '',
    prompt: '',
    style: '',
    isCreating: false
  };
  
  // Discovery state
  let discoveryInsights = {
    totalInterests: 0,
    confidenceScore: 0,
    recentActivity: []
  };

  const mediaTypeOptions = [
    { id: 'music', name: 'Music', icon: '🎵', description: 'Melodies, compositions, and soundscapes' },
    { id: 'visual_art', name: 'Visual Art', icon: '🎨', description: 'Paintings, drawings, and visual creations' },
    { id: 'photography', name: 'Photography', icon: '📸', description: 'Captured moments and artistic imagery' },
    { id: 'cooking', name: 'Cooking', icon: '👨‍🍳', description: 'Recipes, flavors, and culinary arts' },
    { id: 'crafts', name: 'Crafts', icon: '🧵', description: 'Handmade creations and DIY projects' },
    { id: 'digital_art', name: 'Digital Art', icon: '💻', description: 'Digital illustrations and concept art' },
    { id: 'poetry', name: 'Poetry', icon: '📝', description: 'Verses, rhymes, and lyrical expressions' },
    { id: 'dance', name: 'Dance', icon: '💃', description: 'Movement and choreographic expression' },
    { id: 'game_design', name: 'Game Design', icon: '🎮', description: 'Interactive experiences and gameplay' },
    { id: 'fashion', name: 'Fashion', icon: '👗', description: 'Style, design, and wearable art' }
  ];

  onMount(async () => {
    await loadUserProfile();
    await loadAvailableModels();
    await loadCreativeInterests();
    await loadSuggestedActivities();
  });

  async function loadUserProfile() {
    try {
      isLoading = true;
      const response = await fetch('/api/creative-discovery/user-profile/current-user');
      
      if (response.ok) {
        userProfile = await response.json();
        updateDiscoveryInsights();
      } else {
        console.warn('Could not load user profile');
      }
    } catch (error) {
      console.error('Failed to load user profile:', error);
    } finally {
      isLoading = false;
    }
  }

  async function loadAvailableModels() {
    try {
      const response = await fetch('/api/creative-discovery/available-models');
      
      if (response.ok) {
        const data = await response.json();
        availableModels = data.available_models || {};
      }
    } catch (error) {
      console.error('Failed to load available models:', error);
    }
  }

  async function loadCreativeInterests() {
    try {
      const response = await fetch('/api/creative-discovery/creative-interests/current-user');
      
      if (response.ok) {
        const data = await response.json();
        creativeInterests = data.creative_interests || [];
      }
    } catch (error) {
      console.error('Failed to load creative interests:', error);
    }
  }

  async function loadSuggestedActivities() {
    try {
      const response = await fetch('/api/creative-discovery/suggest-activities/current-user');
      
      if (response.ok) {
        const data = await response.json();
        suggestedActivities = data.suggestions || [];
      }
    } catch (error) {
      console.error('Failed to load suggested activities:', error);
    }
  }

  async function loadCollaborationHistory() {
    try {
      const response = await fetch('/api/creative-discovery/collaboration-history/current-user');
      
      if (response.ok) {
        collaborationHistory = await response.json();
      }
    } catch (error) {
      console.error('Failed to load collaboration history:', error);
    }
  }

  function updateDiscoveryInsights() {
    if (userProfile && userProfile.creative_interests) {
      discoveryInsights = {
        totalInterests: userProfile.creative_interests.length,
        confidenceScore: userProfile.creative_interests.length > 0 
          ? userProfile.creative_interests.reduce((sum, interest) => sum + interest.confidence_score, 0) / userProfile.creative_interests.length
          : 0,
        recentActivity: userProfile.creative_interests
          .sort((a, b) => new Date(b.last_mentioned) - new Date(a.last_mentioned))
          .slice(0, 3)
      };
    }
  }

  async function installModel(modelId, mediaType) {
    try {
      installingModels.add(modelId);
      installingModels = installingModels; // Trigger reactivity
      
      installationProgress[modelId] = { status: 'installing', progress: 0 };
      
      const response = await fetch('/api/creative-discovery/install-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'current-user',
          model_id: modelId
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Simulate installation progress
        for (let i = 0; i <= 100; i += 10) {
          installationProgress[modelId].progress = i;
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        installationProgress[modelId].status = 'completed';
        
        // Update model status
        if (availableModels[mediaType]) {
          const modelIndex = availableModels[mediaType].findIndex(m => m.model_id === modelId);
          if (modelIndex !== -1) {
            availableModels[mediaType][modelIndex].is_installed = true;
          }
        }
        
        toast.success(`${result.model_name || 'Model'} installed successfully!`);
        
        // Offer to create content
        await offerContentCreation(mediaType, modelId);
        
      } else {
        throw new Error('Installation failed');
      }
    } catch (error) {
      console.error('Model installation failed:', error);
      installationProgress[modelId] = { status: 'failed', progress: 0 };
      toast.error('Model installation failed');
    } finally {
      installingModels.delete(modelId);
      installingModels = installingModels; // Trigger reactivity
    }
  }

  async function offerContentCreation(mediaType, modelId) {
    const mediaTypeInfo = mediaTypeOptions.find(option => option.id === mediaType);
    
    if (mediaTypeInfo) {
      const shouldCreate = confirm(
        `${mediaTypeInfo.name} model is now ready! Would you like to create something together?`
      );
      
      if (shouldCreate) {
        contentCreationForm.mediaType = mediaType;
        activeTab = 'create';
      }
    }
  }

  async function createPersonalizedContent() {
    try {
      contentCreationForm.isCreating = true;
      
      const response = await fetch('/api/creative-discovery/create-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'current-user',
          media_type: contentCreationForm.mediaType,
          prompt: contentCreationForm.prompt
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        toast.success('Creative content generated successfully!');
        
        // Reset form
        contentCreationForm = {
          mediaType: '',
          prompt: '',
          style: '',
          isCreating: false
        };
        
        // Show created content
        showCreatedContent(result.generated_content);
        
      } else {
        throw new Error('Content creation failed');
      }
    } catch (error) {
      console.error('Content creation failed:', error);
      toast.error('Failed to create content');
    } finally {
      contentCreationForm.isCreating = false;
    }
  }

  function showCreatedContent(content) {
    // This would open a modal or navigate to show the created content
    alert(`Created: ${content.description}\nType: ${content.type}\nFile: ${content.file_path}`);
  }

  async function analyzeCurrentConversation() {
    try {
      const conversationText = "I love playing piano and recently started learning jazz improvisation";
      
      const response = await fetch('/api/creative-discovery/analyze-conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'current-user',
          conversation_text: conversationText,
          context: { source: 'manual_analysis' }
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success('Conversation analyzed for creative interests!');
        
        // Refresh interests
        await loadCreativeInterests();
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error) {
      console.error('Conversation analysis failed:', error);
      toast.error('Failed to analyze conversation');
    }
  }

  function getMediaTypeInfo(mediaType) {
    return mediaTypeOptions.find(option => option.id === mediaType) || { 
      name: mediaType, 
      icon: '🎨', 
      description: 'Creative expression' 
    };
  }

  function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    if (confidence >= 0.4) return 'text-orange-400';
    return 'text-red-400';
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }

  function getSkillLevelColor(skillLevel) {
    const colors = {
      'beginner': 'text-blue-400',
      'intermediate': 'text-green-400',
      'advanced': 'text-purple-400',
      'professional': 'text-yellow-400'
    };
    return colors[skillLevel] || 'text-gray-400';
  }
</script>

<div class="creative-discovery bg-gray-900 text-white p-6 rounded-lg">
  <div class="discovery-header mb-6">
    <h2 class="text-2xl font-bold mb-2 flex items-center">
      🎨 Creative Discovery & Collaboration
      {#if $currentPersona}
        <span class="ml-2 text-lg text-gray-400">- with {$currentPersona}</span>
      {/if}
    </h2>
    <p class="text-gray-400">
      Discover your creative interests and collaborate with AI models tailored to your artistic preferences
    </p>
  </div>

  <!-- Tab Navigation -->
  <div class="tab-navigation mb-6">
    <div class="flex space-x-4 border-b border-gray-700">
      <button 
        class="px-4 py-2 border-b-2 transition-colors {activeTab === 'discovery' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}"
        on:click={() => activeTab = 'discovery'}
      >
        🔍 Discovery
      </button>
      <button 
        class="px-4 py-2 border-b-2 transition-colors {activeTab === 'models' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}"
        on:click={() => activeTab = 'models'}
      >
        🤖 AI Models
      </button>
      <button 
        class="px-4 py-2 border-b-2 transition-colors {activeTab === 'create' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}"
        on:click={() => activeTab = 'create'}
      >
        ✨ Create
      </button>
      <button 
        class="px-4 py-2 border-b-2 transition-colors {activeTab === 'history' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}"
        on:click={() => { activeTab = 'history'; loadCollaborationHistory(); }}
      >
        📚 History
      </button>
    </div>
  </div>

  {#if isLoading}
    <div class="loading-state text-center py-12">
      <div class="animate-spin text-4xl mb-4">🎨</div>
      <div>Loading creative profile...</div>
    </div>
  {:else}
    <!-- Discovery Tab -->
    {#if activeTab === 'discovery'}
      <div class="discovery-content space-y-6">
        <!-- Discovery Insights -->
        <div class="insights-panel bg-gray-800 p-6 rounded-lg">
          <h3 class="text-xl font-semibold mb-4 flex items-center">
            📊 Your Creative Profile
          </h3>
          
          <div class="insights-grid grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="insight-card bg-gray-700 p-4 rounded-lg text-center">
              <div class="text-2xl font-bold text-blue-400">{discoveryInsights.totalInterests}</div>
              <div class="text-sm text-gray-400">Creative Interests</div>
            </div>
            <div class="insight-card bg-gray-700 p-4 rounded-lg text-center">
              <div class="text-2xl font-bold text-green-400">{(discoveryInsights.confidenceScore * 100).toFixed(0)}%</div>
              <div class="text-sm text-gray-400">Avg Confidence</div>
            </div>
            <div class="insight-card bg-gray-700 p-4 rounded-lg text-center">
              <div class="text-2xl font-bold text-purple-400">{discoveryInsights.recentActivity.length}</div>
              <div class="text-sm text-gray-400">Recent Activity</div>
            </div>
          </div>

          <button 
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium"
            on:click={analyzeCurrentConversation}
          >
            🔍 Analyze Current Interests
          </button>
        </div>

        <!-- Discovered Interests -->
        {#if creativeInterests.length > 0}
          <div class="interests-panel bg-gray-800 p-6 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">🎭 Discovered Creative Interests</h3>
            
            <div class="interests-grid space-y-4">
              {#each creativeInterests as interest}
                {@const mediaInfo = getMediaTypeInfo(interest.media_type)}
                <div class="interest-card bg-gray-700 p-4 rounded-lg">
                  <div class="flex items-start justify-between">
                    <div class="flex items-center">
                      <span class="text-2xl mr-3">{mediaInfo.icon}</span>
                      <div>
                        <h4 class="font-semibold">{mediaInfo.name}</h4>
                        <p class="text-sm text-gray-400">{interest.specific_interests.join(', ')}</p>
                      </div>
                    </div>
                    
                    <div class="text-right">
                      <div class="text-sm {getConfidenceColor(interest.confidence_score)}">
                        {(interest.confidence_score * 100).toFixed(0)}% confidence
                      </div>
                      <div class="text-xs text-gray-500">
                        {interest.frequency_mentioned} mentions
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-3 flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                      <span class="text-xs {getSkillLevelColor(interest.skill_level)} font-medium">
                        {interest.skill_level.toUpperCase()}
                      </span>
                      <span class="text-xs text-gray-500">
                        Last: {formatDate(interest.last_mentioned)}
                      </span>
                    </div>
                    
                    <div class="emotional-connection">
                      <div class="text-xs text-gray-400">Emotional Connection</div>
                      <div class="w-16 h-2 bg-gray-600 rounded-full overflow-hidden">
                        <div 
                          class="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                          style="width: {interest.emotional_connection * 100}%"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Suggested Activities -->
        {#if suggestedActivities.length > 0}
          <div class="activities-panel bg-gray-800 p-6 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">💡 Suggested Creative Activities</h3>
            
            <div class="activities-grid grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each suggestedActivities as activity}
                {@const mediaInfo = getMediaTypeInfo(activity.media_type)}
                <div class="activity-card bg-gray-700 p-4 rounded-lg">
                  <div class="flex items-start">
                    <span class="text-xl mr-3">{mediaInfo.icon}</span>
                    <div class="flex-1">
                      <h4 class="font-semibold mb-2">{activity.activity}</h4>
                      <p class="text-sm text-gray-400 mb-3">{activity.description}</p>
                      
                      <div class="flex justify-between items-center">
                        <span class="text-xs text-blue-400">
                          {activity.media_type.replace('_', ' ')}
                        </span>
                        
                        <button 
                          class="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm"
                          on:click={() => {
                            contentCreationForm.mediaType = activity.media_type;
                            activeTab = 'create';
                          }}
                        >
                          Try Now
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {/if}

    <!-- AI Models Tab -->
    {#if activeTab === 'models'}
      <div class="models-content space-y-6">
        <div class="models-header">
          <h3 class="text-xl font-semibold mb-4">🤖 Available AI Creative Models</h3>
          <p class="text-gray-400 mb-6">
            Install specialized AI models for different creative mediums based on your interests
          </p>
        </div>

        {#each Object.entries(availableModels) as [mediaType, models]}
          {@const mediaInfo = getMediaTypeInfo(mediaType)}
          <div class="media-type-section bg-gray-800 p-6 rounded-lg">
            <h4 class="text-lg font-semibold mb-4 flex items-center">
              <span class="text-xl mr-2">{mediaInfo.icon}</span>
              {mediaInfo.name}
              <span class="ml-2 text-sm text-gray-400">({models.length} models available)</span>
            </h4>
            
            <div class="models-grid grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each models as model}
                <div class="model-card bg-gray-700 p-4 rounded-lg">
                  <div class="flex justify-between items-start mb-3">
                    <div>
                      <h5 class="font-medium">{model.name}</h5>
                      <p class="text-sm text-gray-400 capitalize">{model.quality_level} quality</p>
                    </div>
                    
                    <div class="text-right">
                      {#if model.cost_per_use > 0}
                        <div class="text-sm text-yellow-400">${model.cost_per_use}/use</div>
                      {:else}
                        <div class="text-sm text-green-400">Free</div>
                      {/if}
                    </div>
                  </div>
                  
                  <div class="capabilities mb-3">
                    <div class="text-xs text-gray-500 mb-1">Capabilities:</div>
                    <div class="flex flex-wrap gap-1">
                      {#each model.capabilities as capability}
                        <span class="px-2 py-1 bg-gray-600 rounded-full text-xs">
                          {capability.replace('_', ' ')}
                        </span>
                      {/each}
                    </div>
                  </div>
                  
                  <div class="model-actions">
                    {#if model.is_installed}
                      <button class="w-full px-3 py-2 bg-green-600 rounded text-sm" disabled>
                        ✅ Installed
                      </button>
                    {:else if installingModels.has(model.model_id)}
                      <div class="installation-progress">
                        <div class="text-xs text-blue-400 mb-1">Installing...</div>
                        <div class="w-full h-2 bg-gray-600 rounded-full overflow-hidden">
                          <div 
                            class="h-full bg-blue-500 transition-all duration-300"
                            style="width: {installationProgress[model.model_id]?.progress || 0}%"
                          ></div>
                        </div>
                      </div>
                    {:else}
                      <button 
                        class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                        on:click={() => installModel(model.model_id, mediaType)}
                      >
                        📥 Install Model
                      </button>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {/if}

    <!-- Create Tab -->
    {#if activeTab === 'create'}
      <div class="create-content space-y-6">
        <div class="create-header">
          <h3 class="text-xl font-semibold mb-4">✨ Create Personalized Content</h3>
          <p class="text-gray-400 mb-6">
            Generate creative content tailored to your discovered preferences and style
          </p>
        </div>

        <div class="creation-form bg-gray-800 p-6 rounded-lg">
          <div class="form-grid space-y-4">
            <!-- Media Type Selection -->
            <div>
              <label class="block text-sm font-medium mb-2">Creative Medium</label>
              <select 
                bind:value={contentCreationForm.mediaType}
                class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg"
              >
                <option value="">Select a creative medium...</option>
                {#each mediaTypeOptions as option}
                  <option value={option.id}>{option.icon} {option.name}</option>
                {/each}
              </select>
            </div>

            <!-- Creative Prompt -->
            <div>
              <label class="block text-sm font-medium mb-2">Creative Prompt</label>
              <textarea 
                bind:value={contentCreationForm.prompt}
                placeholder="Describe what you'd like to create, or leave blank for a surprise based on your interests..."
                class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg h-24"
              ></textarea>
            </div>

            <!-- Create Button -->
            <div class="create-actions">
              <button 
                class="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium flex items-center justify-center disabled:opacity-50"
                disabled={!contentCreationForm.mediaType || contentCreationForm.isCreating}
                on:click={createPersonalizedContent}
              >
                {#if contentCreationForm.isCreating}
                  <div class="animate-spin text-lg mr-2">⏳</div>
                  Creating...
                {:else}
                  ✨ Create Together
                {/if}
              </button>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- History Tab -->
    {#if activeTab === 'history'}
      <div class="history-content space-y-6">
        <div class="history-header">
          <h3 class="text-xl font-semibold mb-4">📚 Creative Collaboration History</h3>
          <p class="text-gray-400 mb-6">
            Review your creative journey and collaborative projects
          </p>
        </div>

        {#if collaborationHistory}
          <div class="history-stats bg-gray-800 p-6 rounded-lg">
            <div class="stats-grid grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-blue-400">{collaborationHistory.total_collaborations}</div>
                <div class="text-sm text-gray-400">Total Collaborations</div>
              </div>
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-green-400">{Object.keys(collaborationHistory.collaborations_by_type).length}</div>
                <div class="text-sm text-gray-400">Creative Mediums</div>
              </div>
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-purple-400">{collaborationHistory.recent_creations.length}</div>
                <div class="text-sm text-gray-400">Recent Works</div>
              </div>
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-yellow-400">{collaborationHistory.favorite_styles.length}</div>
                <div class="text-sm text-gray-400">Favorite Styles</div>
              </div>
            </div>
          </div>

          <!-- Recent Creations -->
          {#if collaborationHistory.recent_creations.length > 0}
            <div class="recent-creations bg-gray-800 p-6 rounded-lg">
              <h4 class="text-lg font-semibold mb-4">🎨 Recent Creations</h4>
              
              <div class="creations-grid space-y-4">
                {#each collaborationHistory.recent_creations as creation}
                  {@const mediaInfo = getMediaTypeInfo(creation.type)}
                  <div class="creation-card bg-gray-700 p-4 rounded-lg flex items-center justify-between">
                    <div class="flex items-center">
                      <span class="text-xl mr-3">{mediaInfo.icon}</span>
                      <div>
                        <h5 class="font-medium">{creation.title}</h5>
                        <p class="text-sm text-gray-400">{formatDate(creation.created_at)}</p>
                      </div>
                    </div>
                    
                    <div class="flex items-center">
                      <div class="rating mr-3">
                        <span class="text-yellow-400">⭐</span>
                        <span class="text-sm">{creation.user_satisfaction}/5</span>
                      </div>
                      <button class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                        View
                      </button>
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {:else}
          <div class="no-history bg-gray-800 p-8 rounded-lg text-center">
            <div class="text-4xl mb-4">🎨</div>
            <h4 class="text-lg font-semibold mb-2">No Collaboration History Yet</h4>
            <p class="text-gray-400 mb-4">
              Start creating with AI models to build your creative collaboration history
            </p>
            <button 
              class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium"
              on:click={() => activeTab = 'create'}
            >
              Create Your First Piece
            </button>
          </div>
        {/if}
      </div>
    {/if}
  {/if}
</div>

<style>
  .tab-navigation button:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  .insight-card, .interest-card, .activity-card, .model-card, .creation-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .insight-card:hover, .interest-card:hover, .activity-card:hover, .model-card:hover, .creation-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  
  .installation-progress {
    animation: pulse 1.5s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
</style>
