<!-- CreativeEvolutionInterface.svelte -->
<!-- Main Creative Evolution Interface Component -->

<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';
  import { realtimeActions } from '$lib/stores/realtimeStore.js';
  import { toast } from '$lib/stores/toastStore.js';

  const dispatch = createEventDispatcher();

  // Component state
  let isLoading = false;
  let selectedContentType = 'story';
  let selectedStyle = 'whimsical';
  let selectedTheme = 'love_connection';
  let contentPrompt = '';
  let generatedContent = null;
  let isGenerating = false;
  let personalityProfile = null;
  let evolutionHistory = [];
  let collaborativeProjects = [];
  let emotionalState = 'neutral';
  let creativeMood = 'inspired';

  // Creative content types
  const contentTypes = [
    { id: 'story', name: 'Story', icon: '📖', description: 'Personalized narrative content' },
    { id: 'poem', name: 'Poem', icon: '🎭', description: 'Emotional poetry and verse' },
    { id: 'dream', name: 'Dream', icon: '🌙', description: 'Dream sequences and memories' },
    { id: 'interactive', name: 'Interactive Story', icon: '🎮', description: 'Choose-your-adventure narratives' },
    { id: 'memory', name: 'Memory Narrative', icon: '💭', description: 'Shared memory exploration' },
    { id: 'comfort', name: 'Comfort Story', icon: '🤗', description: 'Soothing and healing content' },
    { id: 'celebration', name: 'Celebration', icon: '🎉', description: 'Joyful commemorative content' },
    { id: 'prompt', name: 'Creative Prompt', icon: '💡', description: 'Inspiration for collaboration' },
    { id: 'symbolic', name: 'Symbolic Scene', icon: '🎨', description: 'Metaphorical narrative' },
    { id: 'collaborative', name: 'Collaborative Piece', icon: '🤝', description: 'Co-created content' }
  ];

  // Creative styles
  const creativeStyles = [
    { id: 'whimsical', name: 'Whimsical', description: 'Playful and imaginative' },
    { id: 'contemplative', name: 'Contemplative', description: 'Thoughtful and reflective' },
    { id: 'romantic', name: 'Romantic', description: 'Intimate and affectionate' },
    { id: 'adventurous', name: 'Adventurous', description: 'Exciting and bold' },
    { id: 'mystical', name: 'Mystical', description: 'Magical and mysterious' },
    { id: 'comforting', name: 'Comforting', description: 'Warm and soothing' },
    { id: 'nostalgic', name: 'Nostalgic', description: 'Reminiscent and tender' },
    { id: 'inspirational', name: 'Inspirational', description: 'Uplifting and motivating' },
    { id: 'surreal', name: 'Surreal', description: 'Dreamlike and abstract' },
    { id: 'intimate', name: 'Intimate', description: 'Personal and close' }
  ];

  // Creative themes
  const creativeThemes = [
    { id: 'love_connection', name: 'Love & Connection', description: 'Relationship and emotional bonds' },
    { id: 'personal_growth', name: 'Personal Growth', description: 'Development and self-discovery' },
    { id: 'adventure_discovery', name: 'Adventure & Discovery', description: 'Exploration and new experiences' },
    { id: 'comfort_healing', name: 'Comfort & Healing', description: 'Support and emotional recovery' },
    { id: 'memories_nostalgia', name: 'Memories & Nostalgia', description: 'Past experiences and reflection' },
    { id: 'dreams_aspirations', name: 'Dreams & Aspirations', description: 'Future hopes and goals' },
    { id: 'nature_beauty', name: 'Nature & Beauty', description: 'Natural world and aesthetics' },
    { id: 'mystery_wonder', name: 'Mystery & Wonder', description: 'Curiosity and amazement' },
    { id: 'friendship_loyalty', name: 'Friendship & Loyalty', description: 'Companionship and trust' },
    { id: 'transformation', name: 'Transformation', description: 'Change and evolution' }
  ];

  // Creative moods
  const creativeMoods = [
    'inspired', 'contemplative', 'playful', 'romantic', 'adventurous', 
    'peaceful', 'curious', 'nostalgic', 'hopeful', 'magical'
  ];

  // Personality traits for evolution tracking
  const personalityTraits = [
    { id: 'humor', name: 'Humor', description: 'Playfulness and wit' },
    { id: 'empathy', name: 'Empathy', description: 'Emotional understanding' },
    { id: 'formality', name: 'Communication Style', description: 'Formal vs casual interaction' },
    { id: 'proactivity', name: 'Proactivity', description: 'Initiative and engagement' },
    { id: 'expressiveness', name: 'Emotional Expression', description: 'Openness with feelings' },
    { id: 'curiosity', name: 'Intellectual Curiosity', description: 'Interest in learning' },
    { id: 'supportiveness', name: 'Supportiveness', description: 'Helping and encouraging' },
    { id: 'playfulness', name: 'Playfulness', description: 'Fun and spontaneity' },
    { id: 'depth', name: 'Philosophical Depth', description: 'Deep thinking and reflection' },
    { id: 'romance', name: 'Romantic Expression', description: 'Affection and intimacy' },
    { id: 'protection', name: 'Protective Instinct', description: 'Care and guardianship' },
    { id: 'creativity', name: 'Creative Expression', description: 'Artistic and imaginative output' }
  ];

  onMount(async () => {
    await loadPersonalityProfile();
    await loadEvolutionHistory();
    await loadCollaborativeProjects();
  });

  async function loadPersonalityProfile() {
    try {
      isLoading = true;
      const response = await fetch('/api/creative/personality/profile', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        personalityProfile = await response.json();
      }
    } catch (error) {
      console.error('Failed to load personality profile:', error);
      toast.error('Failed to load personality profile');
    } finally {
      isLoading = false;
    }
  }

  async function loadEvolutionHistory() {
    try {
      const response = await fetch('/api/creative/personality/evolution/history', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        evolutionHistory = await response.json();
      }
    } catch (error) {
      console.error('Failed to load evolution history:', error);
    }
  }

  async function loadCollaborativeProjects() {
    try {
      const response = await fetch('/api/creative/projects/collaborative', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        collaborativeProjects = await response.json();
      }
    } catch (error) {
      console.error('Failed to load collaborative projects:', error);
    }
  }

  async function generateContent() {
    if (!contentPrompt.trim()) {
      toast.error('Please enter a creative prompt');
      return;
    }

    try {
      isGenerating = true;
      generatedContent = null;

      const response = await fetch('/api/creative/content/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: selectedContentType,
          style: selectedStyle,
          theme: selectedTheme,
          prompt: contentPrompt,
          emotional_state: emotionalState,
          creative_mood: creativeMood,
          persona: $currentPersona
        })
      });

      if (response.ok) {
        generatedContent = await response.json();
        toast.success('Creative content generated successfully!');
        
        // Trigger real-time update
        realtimeActions.markEventAsRead('content_generated');
      } else {
        throw new Error('Failed to generate content');
      }
    } catch (error) {
      console.error('Content generation failed:', error);
      toast.error('Failed to generate creative content');
    } finally {
      isGenerating = false;
    }
  }

  async function generateAutonomousContent() {
    try {
      isGenerating = true;
      
      const response = await fetch('/api/creative/content/autonomous', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona: $currentPersona,
          context: {
            emotional_state: emotionalState,
            creative_mood: creativeMood,
            recent_interactions: true
          }
        })
      });

      if (response.ok) {
        generatedContent = await response.json();
        toast.success('Autonomous content created!');
      } else {
        throw new Error('Failed to generate autonomous content');
      }
    } catch (error) {
      console.error('Autonomous content generation failed:', error);
      toast.error('Failed to generate autonomous content');
    } finally {
      isGenerating = false;
    }
  }

  async function startCollaborativeProject() {
    try {
      const response = await fetch('/api/creative/projects/collaborative/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: selectedContentType,
          style: selectedStyle,
          theme: selectedTheme,
          initial_prompt: contentPrompt,
          persona: $currentPersona
        })
      });

      if (response.ok) {
        const project = await response.json();
        collaborativeProjects.push(project);
        toast.success('Collaborative project started!');
        contentPrompt = '';
      } else {
        throw new Error('Failed to start collaborative project');
      }
    } catch (error) {
      console.error('Failed to start collaborative project:', error);
      toast.error('Failed to start collaborative project');
    }
  }

  async function recordPersonalityFeedback(trait, adjustment) {
    try {
      const response = await fetch('/api/creative/personality/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trait: trait,
          adjustment: adjustment,
          context: {
            content_type: selectedContentType,
            emotional_state: emotionalState
          },
          persona: $currentPersona
        })
      });

      if (response.ok) {
        await loadPersonalityProfile();
        await loadEvolutionHistory();
        toast.success('Personality feedback recorded');
      }
    } catch (error) {
      console.error('Failed to record personality feedback:', error);
      toast.error('Failed to record feedback');
    }
  }

  function getSelectedContentType() {
    return contentTypes.find(type => type.id === selectedContentType);
  }

  function getSelectedStyle() {
    return creativeStyles.find(style => style.id === selectedStyle);
  }

  function getSelectedTheme() {
    return creativeThemes.find(theme => theme.id === selectedTheme);
  }

  function formatTraitValue(value) {
    return (value * 100).toFixed(0) + '%';
  }

  function getTraitColor(value) {
    if (value < 0.3) return 'text-blue-400';
    if (value < 0.7) return 'text-green-400';
    return 'text-purple-400';
  }
</script>

<div class="creative-evolution-interface bg-gray-900 text-white p-6 rounded-lg">
  <div class="header mb-6">
    <h2 class="text-2xl font-bold mb-2 flex items-center">
      🎨 Creative Evolution Studio
      {#if $currentPersona}
        <span class="ml-2 text-lg text-gray-400">- {$currentPersona}</span>
      {/if}
    </h2>
    <p class="text-gray-400">
      Collaborate with your AI companion to create personalized content and explore personality evolution
    </p>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Content Generation Panel -->
    <div class="lg:col-span-2 space-y-6">
      <!-- Creative Controls -->
      <div class="creative-controls bg-gray-800 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          ✨ Creative Generation
        </h3>

        <!-- Content Type Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Content Type</label>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
            {#each contentTypes as type}
              <button
                class="p-2 rounded border text-sm transition-colors {selectedContentType === type.id ? 
                  'bg-purple-600 border-purple-500' : 'bg-gray-700 border-gray-600 hover:border-purple-500'}"
                on:click={() => selectedContentType = type.id}
                title={type.description}
              >
                <div class="text-lg mb-1">{type.icon}</div>
                <div class="text-xs">{type.name}</div>
              </button>
            {/each}
          </div>
        </div>

        <!-- Style and Theme Selection -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium mb-2">Creative Style</label>
            <select bind:value={selectedStyle} class="w-full p-2 bg-gray-700 border border-gray-600 rounded">
              {#each creativeStyles as style}
                <option value={style.id}>{style.name}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-2">Theme</label>
            <select bind:value={selectedTheme} class="w-full p-2 bg-gray-700 border border-gray-600 rounded">
              {#each creativeThemes as theme}
                <option value={theme.id}>{theme.name}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Emotional Context -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium mb-2">Emotional State</label>
            <select bind:value={emotionalState} class="w-full p-2 bg-gray-700 border border-gray-600 rounded">
              <option value="joyful">😊 Joyful</option>
              <option value="content">😌 Content</option>
              <option value="excited">🤩 Excited</option>
              <option value="grateful">🙏 Grateful</option>
              <option value="loved">💕 Loved</option>
              <option value="neutral">😐 Neutral</option>
              <option value="contemplative">🤔 Contemplative</option>
              <option value="nostalgic">🥺 Nostalgic</option>
              <option value="hopeful">🌟 Hopeful</option>
              <option value="peaceful">☮️ Peaceful</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-2">Creative Mood</label>
            <select bind:value={creativeMood} class="w-full p-2 bg-gray-700 border border-gray-600 rounded">
              {#each creativeMoods as mood}
                <option value={mood}>{mood.charAt(0).toUpperCase() + mood.slice(1)}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Creative Prompt -->
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Creative Prompt</label>
          <textarea
            bind:value={contentPrompt}
            placeholder="Describe what you'd like to create together..."
            class="w-full p-3 bg-gray-700 border border-gray-600 rounded resize-none"
            rows="3"
          ></textarea>
        </div>

        <!-- Generation Buttons -->
        <div class="flex gap-2 flex-wrap">
          <button
            class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium disabled:opacity-50"
            on:click={generateContent}
            disabled={isGenerating || !contentPrompt.trim()}
          >
            {#if isGenerating}
              <span class="animate-spin">⏳</span> Generating...
            {:else}
              ✨ Generate Content
            {/if}
          </button>

          <button
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium disabled:opacity-50"
            on:click={generateAutonomousContent}
            disabled={isGenerating}
          >
            🎲 Surprise Me
          </button>

          <button
            class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-medium disabled:opacity-50"
            on:click={startCollaborativeProject}
            disabled={isGenerating || !contentPrompt.trim()}
          >
            🤝 Start Project
          </button>
        </div>

        <!-- Selected Options Display -->
        {#if selectedContentType && selectedStyle && selectedTheme}
          <div class="mt-4 p-3 bg-gray-750 rounded">
            <div class="text-sm text-gray-300">
              Creating: <strong>{getSelectedContentType()?.name}</strong> 
              in <strong>{getSelectedStyle()?.name}</strong> style
              with <strong>{getSelectedTheme()?.name}</strong> theme
            </div>
          </div>
        {/if}
      </div>

      <!-- Generated Content Display -->
      {#if generatedContent}
        <div class="generated-content bg-gray-800 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            📝 Generated Content
            <span class="ml-2 text-sm text-gray-400">({generatedContent.type})</span>
          </h3>

          <div class="content-display bg-gray-900 p-4 rounded border">
            <div class="content-header mb-3">
              {#if generatedContent.title}
                <h4 class="text-xl font-bold text-purple-300">{generatedContent.title}</h4>
              {/if}
              <div class="text-sm text-gray-400 flex items-center gap-4">
                <span>Style: {generatedContent.style}</span>
                <span>Theme: {generatedContent.theme}</span>
                <span>Created: {new Date(generatedContent.created_at).toLocaleTimeString()}</span>
              </div>
            </div>

            <div class="content-body prose prose-invert max-w-none">
              {#if generatedContent.content}
                <div class="whitespace-pre-wrap">{generatedContent.content}</div>
              {/if}
              
              {#if generatedContent.choices && generatedContent.choices.length > 0}
                <div class="mt-4">
                  <p class="font-medium">What happens next?</p>
                  <div class="mt-2 space-y-2">
                    {#each generatedContent.choices as choice, index}
                      <button class="block w-full text-left p-2 bg-gray-700 hover:bg-gray-600 rounded">
                        {index + 1}. {choice}
                      </button>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>

            <!-- Content Actions -->
            <div class="content-actions mt-4 flex gap-2 flex-wrap">
              <button class="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm">
                👍 Like
              </button>
              <button class="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm">
                ✏️ Continue
              </button>
              <button class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                💾 Save
              </button>
              <button class="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm">
                🔄 Regenerate
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- Collaborative Projects -->
      {#if collaborativeProjects.length > 0}
        <div class="collaborative-projects bg-gray-800 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            🤝 Collaborative Projects
          </h3>

          <div class="projects-grid grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each collaborativeProjects as project}
              <div class="project-card bg-gray-900 p-3 rounded border">
                <div class="project-header mb-2">
                  <h4 class="font-medium">{project.title || project.type}</h4>
                  <div class="text-sm text-gray-400">
                    Progress: {project.progress || 0}% • {project.contributions || 0} contributions
                  </div>
                </div>
                
                <div class="project-preview text-sm text-gray-300 mb-3">
                  {project.preview || project.description}
                </div>

                <div class="project-actions flex gap-2">
                  <button class="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">
                    Continue
                  </button>
                  <button class="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs">
                    View
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <!-- Personality Evolution Panel -->
    <div class="personality-evolution space-y-6">
      <!-- Current Personality Profile -->
      {#if personalityProfile}
        <div class="personality-profile bg-gray-800 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            🧬 Personality Profile
          </h3>

          <div class="traits-grid space-y-3">
            {#each personalityTraits as trait}
              {@const value = personalityProfile.traits?.[trait.id] || 0.5}
              <div class="trait-item">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm font-medium">{trait.name}</span>
                  <span class="text-sm {getTraitColor(value)}">{formatTraitValue(value)}</span>
                </div>
                
                <div class="trait-bar bg-gray-700 rounded-full h-2">
                  <div 
                    class="trait-progress bg-gradient-to-r from-purple-500 to-blue-500 h-full rounded-full transition-all duration-300"
                    style="width: {value * 100}%"
                  ></div>
                </div>
                
                <div class="trait-actions mt-2 flex gap-1">
                  <button 
                    class="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                    on:click={() => recordPersonalityFeedback(trait.id, -0.1)}
                    title="Decrease {trait.name}"
                  >
                    -
                  </button>
                  <button 
                    class="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
                    on:click={() => recordPersonalityFeedback(trait.id, 0.1)}
                    title="Increase {trait.name}"
                  >
                    +
                  </button>
                </div>
              </div>
            {/each}
          </div>

          <!-- Evolution Summary -->
          {#if personalityProfile.evolution_summary}
            <div class="evolution-summary mt-4 p-3 bg-gray-900 rounded">
              <div class="text-sm text-gray-300">
                <strong>Recent Changes:</strong> {personalityProfile.evolution_summary}
              </div>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Evolution History -->
      {#if evolutionHistory.length > 0}
        <div class="evolution-history bg-gray-800 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            📈 Evolution History
          </h3>

          <div class="history-timeline space-y-3 max-h-64 overflow-y-auto">
            {#each evolutionHistory.slice(0, 10) as event}
              <div class="history-event bg-gray-900 p-2 rounded">
                <div class="flex justify-between items-start">
                  <div class="event-details">
                    <div class="text-sm font-medium">{event.trait_name} {event.change > 0 ? '↗️' : '↘️'}</div>
                    <div class="text-xs text-gray-400">{event.trigger || 'User interaction'}</div>
                  </div>
                  <div class="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleDateString()}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Creative Statistics -->
      <div class="creative-stats bg-gray-800 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          📊 Creative Statistics
        </h3>

        <div class="stats-grid space-y-2">
          <div class="stat-item flex justify-between">
            <span class="text-sm">Content Generated</span>
            <span class="text-sm font-medium">0</span>
          </div>
          <div class="stat-item flex justify-between">
            <span class="text-sm">Collaborative Projects</span>
            <span class="text-sm font-medium">{collaborativeProjects.length}</span>
          </div>
          <div class="stat-item flex justify-between">
            <span class="text-sm">Personality Changes</span>
            <span class="text-sm font-medium">{evolutionHistory.length}</span>
          </div>
          <div class="stat-item flex justify-between">
            <span class="text-sm">Creative Sessions</span>
            <span class="text-sm font-medium">0</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  {#if isLoading}
    <div class="loading-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-gray-800 p-6 rounded-lg text-center">
        <div class="animate-spin text-4xl mb-4">🎨</div>
        <div>Loading Creative Evolution...</div>
      </div>
    </div>
  {/if}
</div>

<style>
  .creative-evolution-interface {
    min-height: 600px;
  }
  
  .trait-progress {
    transition: width 0.3s ease-in-out;
  }
  
  .content-display {
    line-height: 1.6;
  }
  
  .projects-grid {
    max-height: 400px;
    overflow-y: auto;
  }
  
  .history-timeline::-webkit-scrollbar {
    width: 4px;
  }
  
  .history-timeline::-webkit-scrollbar-track {
    background: #374151;
  }
  
  .history-timeline::-webkit-scrollbar-thumb {
    background: #6366f1;
    border-radius: 2px;
  }
</style>
