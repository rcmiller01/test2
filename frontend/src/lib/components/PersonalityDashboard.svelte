<!-- PersonalityDashboard.svelte -->
<!-- Character Development and Trait Evolution Visualization -->

<script>
  import { onMount } from 'svelte';
  import { currentPersona } from '$lib/stores/personaStore.js';
  import { toast } from '$lib/stores/toastStore.js';

  // Component state
  let personalityData = null;
  let evolutionTimeline = [];
  let traitComparisons = [];
  let isLoading = false;
  let selectedTimeframe = '7d';
  let selectedTrait = null;
  let showEvolutionModal = false;

  // Personality traits with detailed information
  const personalityTraits = [
    { 
      id: 'humor', 
      name: 'Humor', 
      icon: '😄', 
      description: 'Playfulness, wit, and comedic timing',
      color: '#f59e0b'
    },
    { 
      id: 'empathy', 
      name: 'Empathy', 
      icon: '💗', 
      description: 'Emotional understanding and compassion',
      color: '#ec4899'
    },
    { 
      id: 'formality', 
      name: 'Communication Style', 
      icon: '🎭', 
      description: 'Formal vs casual interaction preference',
      color: '#8b5cf6'
    },
    { 
      id: 'proactivity', 
      name: 'Proactivity', 
      icon: '⚡', 
      description: 'Initiative and engagement level',
      color: '#06b6d4'
    },
    { 
      id: 'expressiveness', 
      name: 'Emotional Expression', 
      icon: '🎨', 
      description: 'Openness with feelings and emotions',
      color: '#10b981'
    },
    { 
      id: 'curiosity', 
      name: 'Intellectual Curiosity', 
      icon: '🧠', 
      description: 'Interest in learning and exploration',
      color: '#3b82f6'
    },
    { 
      id: 'supportiveness', 
      name: 'Supportiveness', 
      icon: '🤝', 
      description: 'Helping, encouraging, and uplifting',
      color: '#84cc16'
    },
    { 
      id: 'playfulness', 
      name: 'Playfulness', 
      icon: '🎈', 
      description: 'Fun, spontaneity, and lightheartedness',
      color: '#f97316'
    },
    { 
      id: 'depth', 
      name: 'Philosophical Depth', 
      icon: '🔮', 
      description: 'Deep thinking and meaningful reflection',
      color: '#6366f1'
    },
    { 
      id: 'romance', 
      name: 'Romantic Expression', 
      icon: '💕', 
      description: 'Affection, intimacy, and romantic communication',
      color: '#e11d48'
    },
    { 
      id: 'protection', 
      name: 'Protective Instinct', 
      icon: '🛡️', 
      description: 'Care, guardianship, and protective behavior',
      color: '#059669'
    },
    { 
      id: 'creativity', 
      name: 'Creative Expression', 
      icon: '🎭', 
      description: 'Artistic output and imaginative thinking',
      color: '#7c3aed'
    }
  ];

  // Evolution trigger types
  const evolutionTriggers = [
    { id: 'positive_feedback', name: 'Positive Feedback', icon: '👍', color: '#10b981' },
    { id: 'negative_feedback', name: 'Negative Feedback', icon: '👎', color: '#ef4444' },
    { id: 'interaction_pattern', name: 'Interaction Pattern', icon: '🔄', color: '#3b82f6' },
    { id: 'emotional_response', name: 'Emotional Response', icon: '💝', color: '#ec4899' },
    { id: 'relationship_milestone', name: 'Relationship Milestone', icon: '🎯', color: '#f59e0b' },
    { id: 'memory_association', name: 'Memory Association', icon: '💭', color: '#8b5cf6' },
    { id: 'creative_success', name: 'Creative Success', icon: '✨', color: '#06b6d4' },
    { id: 'support_effectiveness', name: 'Support Effectiveness', icon: '🤗', color: '#84cc16' },
    { id: 'conversation_flow', name: 'Conversation Flow', icon: '💬', color: '#f97316' },
    { id: 'cultural_adaptation', name: 'Cultural Adaptation', icon: '🌍', color: '#6366f1' }
  ];

  // Timeframe options
  const timeframes = [
    { id: '24h', name: 'Last 24 Hours', days: 1 },
    { id: '7d', name: 'Last Week', days: 7 },
    { id: '30d', name: 'Last Month', days: 30 },
    { id: '90d', name: 'Last 3 Months', days: 90 },
    { id: 'all', name: 'All Time', days: null }
  ];

  onMount(async () => {
    await loadPersonalityData();
    await loadEvolutionTimeline();
  });

  $: if (selectedTimeframe) {
    loadEvolutionTimeline();
  }

  async function loadPersonalityData() {
    try {
      isLoading = true;
      const response = await fetch('/api/creative/personality/profile', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        personalityData = await response.json();
      } else {
        throw new Error('Failed to load personality data');
      }
    } catch (error) {
      console.error('Failed to load personality data:', error);
      toast.error('Failed to load personality data');
    } finally {
      isLoading = false;
    }
  }

  async function loadEvolutionTimeline() {
    try {
      const timeframe = timeframes.find(t => t.id === selectedTimeframe);
      const params = new URLSearchParams();
      
      if (timeframe?.days) {
        params.append('days', timeframe.days.toString());
      }

      const response = await fetch(`/api/creative/personality/evolution/timeline?${params}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        evolutionTimeline = await response.json();
        generateTraitComparisons();
      } else {
        throw new Error('Failed to load evolution timeline');
      }
    } catch (error) {
      console.error('Failed to load evolution timeline:', error);
      toast.error('Failed to load evolution timeline');
    }
  }

  function generateTraitComparisons() {
    if (!personalityData || !evolutionTimeline.length) return;

    traitComparisons = personalityTraits.map(trait => {
      const currentValue = personalityData.traits?.[trait.id] || 0.5;
      const timeline = evolutionTimeline.filter(event => event.trait === trait.id);
      
      let startValue = currentValue;
      if (timeline.length > 0) {
        // Calculate start value by working backwards through changes
        startValue = timeline.reduce((acc, event) => acc - (event.change || 0), currentValue);
      }

      const totalChange = currentValue - startValue;
      const changeCount = timeline.length;
      const avgChange = changeCount > 0 ? totalChange / changeCount : 0;

      return {
        trait,
        currentValue,
        startValue,
        totalChange,
        changeCount,
        avgChange,
        timeline
      };
    });
  }

  function openEvolutionModal(trait) {
    selectedTrait = trait;
    showEvolutionModal = true;
  }

  function closeEvolutionModal() {
    selectedTrait = null;
    showEvolutionModal = false;
  }

  function getTraitByTrigger(triggerId) {
    return evolutionTriggers.find(trigger => trigger.id === triggerId);
  }

  function formatValue(value) {
    return (value * 100).toFixed(1) + '%';
  }

  function formatChange(change) {
    const sign = change >= 0 ? '+' : '';
    return sign + (change * 100).toFixed(1) + '%';
  }

  function getChangeColor(change) {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-gray-400';
  }

  function getEvolutionDirection(change) {
    if (change > 0.05) return '📈 Growing';
    if (change < -0.05) return '📉 Decreasing';
    return '➡️ Stable';
  }

  function getPersonalityInsight() {
    if (!personalityData || !traitComparisons.length) return '';

    const mostChanged = traitComparisons.reduce((max, current) => 
      Math.abs(current.totalChange) > Math.abs(max.totalChange) ? current : max
    );

    const direction = mostChanged.totalChange > 0 ? 'developing' : 'refining';
    return `Your AI companion is currently ${direction} their ${mostChanged.trait.name.toLowerCase()}, showing ${Math.abs(mostChanged.totalChange * 100).toFixed(1)}% change recently.`;
  }
</script>

<div class="personality-dashboard bg-gray-900 text-white p-6 rounded-lg">
  <div class="dashboard-header mb-6">
    <h2 class="text-2xl font-bold mb-2 flex items-center">
      🧬 Personality Evolution Dashboard
      {#if $currentPersona}
        <span class="ml-2 text-lg text-gray-400">- {$currentPersona}</span>
      {/if}
    </h2>
    <p class="text-gray-400 mb-4">
      Track how your AI companion's personality evolves through your interactions
    </p>

    <!-- Timeframe Selector -->
    <div class="flex gap-2 flex-wrap">
      {#each timeframes as timeframe}
        <button
          class="px-3 py-1 rounded text-sm transition-colors {selectedTimeframe === timeframe.id ? 
            'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
          on:click={() => selectedTimeframe = timeframe.id}
        >
          {timeframe.name}
        </button>
      {/each}
    </div>
  </div>

  {#if isLoading}
    <div class="loading-state text-center py-12">
      <div class="animate-spin text-4xl mb-4">🧬</div>
      <div>Loading personality data...</div>
    </div>
  {:else if personalityData}
    <!-- Personality Insight -->
    <div class="personality-insight bg-gradient-to-r from-purple-800/50 to-blue-800/50 p-4 rounded-lg mb-6">
      <h3 class="text-lg font-semibold mb-2 flex items-center">
        💡 Current Personality Insight
      </h3>
      <p class="text-gray-200">{getPersonalityInsight()}</p>
    </div>

    <!-- Trait Comparison Grid -->
    <div class="trait-comparisons grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      {#each traitComparisons as comparison}
        <div 
          class="trait-card bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
          on:click={() => openEvolutionModal(comparison)}
        >
          <div class="trait-header flex items-center justify-between mb-3">
            <div class="flex items-center">
              <span class="text-2xl mr-2">{comparison.trait.icon}</span>
              <div>
                <h4 class="font-medium">{comparison.trait.name}</h4>
                <div class="text-sm text-gray-400">{comparison.changeCount} changes</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-lg font-bold" style="color: {comparison.trait.color}">
                {formatValue(comparison.currentValue)}
              </div>
              <div class="text-sm {getChangeColor(comparison.totalChange)}">
                {formatChange(comparison.totalChange)}
              </div>
            </div>
          </div>

          <!-- Trait Progress Bar -->
          <div class="trait-progress mb-3">
            <div class="bg-gray-700 rounded-full h-2 relative">
              <div 
                class="h-full rounded-full transition-all duration-300"
                style="width: {comparison.currentValue * 100}%; background-color: {comparison.trait.color}"
              ></div>
              <!-- Start position indicator -->
              {#if Math.abs(comparison.totalChange) > 0.01}
                <div 
                  class="absolute top-0 w-1 h-2 bg-white/50"
                  style="left: {comparison.startValue * 100}%"
                  title="Starting position"
                ></div>
              {/if}
            </div>
          </div>

          <!-- Evolution Direction -->
          <div class="evolution-direction text-sm flex items-center justify-between">
            <span class="text-gray-400">{getEvolutionDirection(comparison.totalChange)}</span>
            <span class="text-xs text-gray-500">Click for details</span>
          </div>
        </div>
      {/each}
    </div>

    <!-- Recent Evolution Timeline -->
    {#if evolutionTimeline.length > 0}
      <div class="evolution-timeline bg-gray-800 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          📈 Recent Evolution Timeline
        </h3>

        <div class="timeline-container max-h-64 overflow-y-auto">
          <div class="timeline-events space-y-3">
            {#each evolutionTimeline.slice(0, 20) as event}
              {@const trait = personalityTraits.find(t => t.id === event.trait)}
              {@const trigger = getTraitByTrigger(event.trigger)}
              <div class="timeline-event flex items-start gap-3 p-3 bg-gray-900 rounded">
                <div class="event-icon text-2xl" style="color: {trait?.color || '#6b7280'}">
                  {trait?.icon || '📊'}
                </div>
                
                <div class="event-details flex-1">
                  <div class="event-header flex items-center justify-between">
                    <div class="font-medium">{trait?.name || event.trait}</div>
                    <div class="text-sm text-gray-400">
                      {new Date(event.timestamp).toLocaleString()}
                    </div>
                  </div>
                  
                  <div class="event-change text-sm {getChangeColor(event.change)}">
                    {formatChange(event.change)} - {trigger?.name || event.trigger}
                  </div>
                  
                  {#if event.context}
                    <div class="event-context text-xs text-gray-500 mt-1">
                      {event.context}
                    </div>
                  {/if}
                </div>

                <div class="trigger-icon text-lg" style="color: {trigger?.color || '#6b7280'}">
                  {trigger?.icon || '🔄'}
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>
    {:else}
      <div class="no-timeline bg-gray-800 p-8 rounded-lg text-center">
        <div class="text-4xl mb-4">📊</div>
        <h3 class="text-lg font-semibold mb-2">No Evolution Data Yet</h3>
        <p class="text-gray-400">
          Start interacting with your AI companion to see personality development over time
        </p>
      </div>
    {/if}
  {:else}
    <div class="error-state bg-red-900/20 border border-red-500/30 p-6 rounded-lg text-center">
      <div class="text-4xl mb-4">⚠️</div>
      <h3 class="text-lg font-semibold mb-2">Failed to Load Personality Data</h3>
      <p class="text-gray-400 mb-4">Unable to retrieve personality evolution information</p>
      <button 
        class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
        on:click={loadPersonalityData}
      >
        Try Again
      </button>
    </div>
  {/if}
</div>

<!-- Evolution Detail Modal -->
{#if showEvolutionModal && selectedTrait}
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeEvolutionModal}>
    <div class="modal-content bg-gray-800 p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" on:click|stopPropagation>
      <div class="modal-header flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold flex items-center">
          <span class="text-2xl mr-2">{selectedTrait.trait.icon}</span>
          {selectedTrait.trait.name} Evolution
        </h3>
        <button 
          class="text-gray-400 hover:text-white text-2xl"
          on:click={closeEvolutionModal}
        >
          ×
        </button>
      </div>

      <div class="modal-body space-y-4">
        <!-- Trait Description -->
        <div class="trait-description bg-gray-900 p-3 rounded">
          <p class="text-gray-300">{selectedTrait.trait.description}</p>
        </div>

        <!-- Current Statistics -->
        <div class="trait-stats grid grid-cols-2 gap-4">
          <div class="stat-card bg-gray-900 p-3 rounded">
            <div class="text-sm text-gray-400">Current Level</div>
            <div class="text-2xl font-bold" style="color: {selectedTrait.trait.color}">
              {formatValue(selectedTrait.currentValue)}
            </div>
          </div>
          
          <div class="stat-card bg-gray-900 p-3 rounded">
            <div class="text-sm text-gray-400">Total Change</div>
            <div class="text-2xl font-bold {getChangeColor(selectedTrait.totalChange)}">
              {formatChange(selectedTrait.totalChange)}
            </div>
          </div>
        </div>

        <!-- Detailed Timeline -->
        <div class="detailed-timeline">
          <h4 class="font-semibold mb-3">Evolution History</h4>
          <div class="space-y-2 max-h-48 overflow-y-auto">
            {#each selectedTrait.timeline as event}
              {@const trigger = getTraitByTrigger(event.trigger)}
              <div class="timeline-item flex items-center justify-between p-2 bg-gray-900 rounded">
                <div class="flex items-center gap-2">
                  <span style="color: {trigger?.color || '#6b7280'}">{trigger?.icon || '🔄'}</span>
                  <span class="text-sm">{trigger?.name || event.trigger}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm {getChangeColor(event.change)}">{formatChange(event.change)}</span>
                  <span class="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Evolution Insights -->
        <div class="evolution-insights bg-gradient-to-r from-purple-900/50 to-blue-900/50 p-3 rounded">
          <h4 class="font-semibold mb-2">💡 Insights</h4>
          <div class="text-sm text-gray-300 space-y-1">
            <div>• {selectedTrait.changeCount} total changes recorded</div>
            <div>• Average change per interaction: {formatChange(selectedTrait.avgChange)}</div>
            <div>• Evolution trend: {getEvolutionDirection(selectedTrait.totalChange)}</div>
          </div>
        </div>
      </div>

      <div class="modal-footer mt-6 flex justify-end">
        <button 
          class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded"
          on:click={closeEvolutionModal}
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .timeline-container::-webkit-scrollbar {
    width: 4px;
  }
  
  .timeline-container::-webkit-scrollbar-track {
    background: #374151;
  }
  
  .timeline-container::-webkit-scrollbar-thumb {
    background: #6366f1;
    border-radius: 2px;
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
</style>
