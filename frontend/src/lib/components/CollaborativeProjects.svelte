<!-- CollaborativeProjects.svelte -->
<!-- Multi-part Creative Project Management Interface -->

<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { currentPersona } from '$lib/stores/personaStore.js';
  import { toast } from '$lib/stores/toastStore.js';

  const dispatch = createEventDispatcher();

  // Component state
  let projects = [];
  let selectedProject = null;
  let isLoading = false;
  let showCreateModal = false;
  let showProjectModal = false;
  let newProjectData = {
    title: '',
    type: 'story',
    style: 'whimsical',
    theme: 'love_connection',
    description: '',
    collaboration_style: 'alternating'
  };

  // Project types and configurations
  const projectTypes = [
    { id: 'story', name: 'Collaborative Story', icon: '📖', description: 'Build a narrative together over time' },
    { id: 'poetry', name: 'Poetry Collection', icon: '🎭', description: 'Create poems and verses collaboratively' },
    { id: 'interactive', name: 'Interactive Adventure', icon: '🎮', description: 'Choose-your-adventure narrative' },
    { id: 'memory_book', name: 'Memory Book', icon: '📚', description: 'Collection of shared memories and experiences' },
    { id: 'dream_journal', name: 'Dream Journal', icon: '🌙', description: 'Explore dreams and subconscious together' },
    { id: 'creative_journal', name: 'Creative Journal', icon: '✍️', description: 'Mixed creative content and reflections' }
  ];

  const collaborationStyles = [
    { id: 'alternating', name: 'Alternating', description: 'Take turns adding content' },
    { id: 'simultaneous', name: 'Simultaneous', description: 'Work on different aspects together' },
    { id: 'guided', name: 'AI Guided', description: 'AI provides structure and prompts' },
    { id: 'user_led', name: 'User Led', description: 'User drives with AI support' },
    { id: 'equal', name: 'Equal Partnership', description: 'Equal creative input from both' }
  ];

  const projectStatuses = [
    { id: 'active', name: 'Active', color: '#10b981', icon: '🟢' },
    { id: 'paused', name: 'Paused', color: '#f59e0b', icon: '🟡' },
    { id: 'completed', name: 'Completed', color: '#3b82f6', icon: '🔵' },
    { id: 'archived', name: 'Archived', color: '#6b7280', icon: '⚫' }
  ];

  onMount(async () => {
    await loadProjects();
  });

  async function loadProjects() {
    try {
      isLoading = true;
      const response = await fetch('/api/creative/projects/collaborative', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        projects = await response.json();
      } else {
        throw new Error('Failed to load projects');
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load collaborative projects');
    } finally {
      isLoading = false;
    }
  }

  async function createProject() {
    if (!newProjectData.title.trim()) {
      toast.error('Please enter a project title');
      return;
    }

    try {
      const response = await fetch('/api/creative/projects/collaborative/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newProjectData,
          persona: $currentPersona
        })
      });

      if (response.ok) {
        const project = await response.json();
        projects.push(project);
        projects = projects; // Trigger reactivity
        
        // Reset form
        newProjectData = {
          title: '',
          type: 'story',
          style: 'whimsical',
          theme: 'love_connection',
          description: '',
          collaboration_style: 'alternating'
        };
        
        showCreateModal = false;
        toast.success('Collaborative project created!');
      } else {
        throw new Error('Failed to create project');
      }
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create collaborative project');
    }
  }

  async function addContribution(projectId, content, contributionType = 'content') {
    try {
      const response = await fetch(`/api/creative/projects/collaborative/${projectId}/contribute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          type: contributionType,
          persona: $currentPersona
        })
      });

      if (response.ok) {
        await loadProjects();
        if (selectedProject && selectedProject.id === projectId) {
          await loadProjectDetails(projectId);
        }
        toast.success('Contribution added!');
      } else {
        throw new Error('Failed to add contribution');
      }
    } catch (error) {
      console.error('Failed to add contribution:', error);
      toast.error('Failed to add contribution');
    }
  }

  async function loadProjectDetails(projectId) {
    try {
      const response = await fetch(`/api/creative/projects/collaborative/${projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        selectedProject = await response.json();
      } else {
        throw new Error('Failed to load project details');
      }
    } catch (error) {
      console.error('Failed to load project details:', error);
      toast.error('Failed to load project details');
    }
  }

  async function updateProjectStatus(projectId, status) {
    try {
      const response = await fetch(`/api/creative/projects/collaborative/${projectId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        await loadProjects();
        if (selectedProject && selectedProject.id === projectId) {
          selectedProject.status = status;
        }
        toast.success('Project status updated');
      } else {
        throw new Error('Failed to update project status');
      }
    } catch (error) {
      console.error('Failed to update project status:', error);
      toast.error('Failed to update project status');
    }
  }

  async function requestAIContribution(projectId) {
    try {
      const response = await fetch(`/api/creative/projects/collaborative/${projectId}/ai-contribute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona: $currentPersona
        })
      });

      if (response.ok) {
        await loadProjects();
        if (selectedProject && selectedProject.id === projectId) {
          await loadProjectDetails(projectId);
        }
        toast.success('AI contribution added!');
      } else {
        throw new Error('Failed to get AI contribution');
      }
    } catch (error) {
      console.error('Failed to get AI contribution:', error);
      toast.error('Failed to get AI contribution');
    }
  }

  function openProjectModal(project) {
    selectedProject = project;
    loadProjectDetails(project.id);
    showProjectModal = true;
  }

  function closeProjectModal() {
    selectedProject = null;
    showProjectModal = false;
  }

  function openCreateModal() {
    showCreateModal = true;
  }

  function closeCreateModal() {
    showCreateModal = false;
  }

  function getProjectType(typeId) {
    return projectTypes.find(type => type.id === typeId);
  }

  function getProjectStatus(statusId) {
    return projectStatuses.find(status => status.id === statusId);
  }

  function getCollaborationStyle(styleId) {
    return collaborationStyles.find(style => style.id === styleId);
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }

  function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString();
  }

  function calculateProgress(project) {
    const targetContributions = project.target_contributions || 10;
    const currentContributions = project.contributions?.length || 0;
    return Math.min((currentContributions / targetContributions) * 100, 100);
  }

  function getContributionAuthor(contribution) {
    return contribution.author === 'user' ? 'You' : $currentPersona || 'AI';
  }

  // Reactive statement for filtering projects
  $: activeProjects = projects.filter(p => p.status === 'active');
  $: pausedProjects = projects.filter(p => p.status === 'paused');
  $: completedProjects = projects.filter(p => p.status === 'completed');
</script>

<div class="collaborative-projects bg-gray-900 text-white p-6 rounded-lg">
  <div class="projects-header mb-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold flex items-center">
        🤝 Collaborative Projects
        {#if $currentPersona}
          <span class="ml-2 text-lg text-gray-400">- {$currentPersona}</span>
        {/if}
      </h2>
      
      <button 
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium flex items-center"
        on:click={openCreateModal}
      >
        ➕ New Project
      </button>
    </div>

    <p class="text-gray-400">
      Work together with your AI companion on ongoing creative projects
    </p>
  </div>

  {#if isLoading}
    <div class="loading-state text-center py-12">
      <div class="animate-spin text-4xl mb-4">🤝</div>
      <div>Loading collaborative projects...</div>
    </div>
  {:else if projects.length === 0}
    <div class="no-projects bg-gray-800 p-8 rounded-lg text-center">
      <div class="text-4xl mb-4">🎨</div>
      <h3 class="text-lg font-semibold mb-2">No Collaborative Projects Yet</h3>
      <p class="text-gray-400 mb-4">
        Start a creative project to work on together with your AI companion
      </p>
      <button 
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium"
        on:click={openCreateModal}
      >
        Create Your First Project
      </button>
    </div>
  {:else}
    <!-- Project Categories -->
    <div class="project-categories space-y-6">
      <!-- Active Projects -->
      {#if activeProjects.length > 0}
        <div class="active-projects">
          <h3 class="text-lg font-semibold mb-3 flex items-center">
            🟢 Active Projects ({activeProjects.length})
          </h3>
          
          <div class="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each activeProjects as project}
              <div 
                class="project-card bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
                on:click={() => openProjectModal(project)}
              >
                <div class="project-header mb-3">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium flex items-center">
                      <span class="text-xl mr-2">{getProjectType(project.type)?.icon}</span>
                      {project.title}
                    </h4>
                    <span class="text-xs text-green-400">●</span>
                  </div>
                  
                  <div class="text-sm text-gray-400">
                    {getProjectType(project.type)?.name} • {getCollaborationStyle(project.collaboration_style)?.name}
                  </div>
                </div>

                <div class="project-preview text-sm text-gray-300 mb-3 line-clamp-2">
                  {project.description || project.preview || 'No description available'}
                </div>

                <!-- Progress Bar -->
                <div class="project-progress mb-3">
                  <div class="flex justify-between items-center mb-1">
                    <span class="text-xs text-gray-400">Progress</span>
                    <span class="text-xs text-gray-400">{calculateProgress(project).toFixed(0)}%</span>
                  </div>
                  <div class="bg-gray-700 rounded-full h-2">
                    <div 
                      class="bg-purple-500 h-full rounded-full transition-all duration-300"
                      style="width: {calculateProgress(project)}%"
                    ></div>
                  </div>
                </div>

                <div class="project-stats flex justify-between text-xs text-gray-400">
                  <span>{project.contributions?.length || 0} contributions</span>
                  <span>Updated {formatDate(project.updated_at)}</span>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Paused Projects -->
      {#if pausedProjects.length > 0}
        <div class="paused-projects">
          <h3 class="text-lg font-semibold mb-3 flex items-center">
            🟡 Paused Projects ({pausedProjects.length})
          </h3>
          
          <div class="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each pausedProjects as project}
              <div 
                class="project-card bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer opacity-75"
                on:click={() => openProjectModal(project)}
              >
                <div class="project-header mb-3">
                  <h4 class="font-medium flex items-center">
                    <span class="text-xl mr-2">{getProjectType(project.type)?.icon}</span>
                    {project.title}
                    <span class="ml-2 text-xs text-yellow-400">⏸️</span>
                  </h4>
                  <div class="text-sm text-gray-400">
                    {project.contributions?.length || 0} contributions • Paused {formatDate(project.updated_at)}
                  </div>
                </div>

                <div class="project-preview text-sm text-gray-300 mb-3">
                  {project.description || project.preview || 'No description available'}
                </div>

                <button 
                  class="w-full px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm"
                  on:click|stopPropagation={() => updateProjectStatus(project.id, 'active')}
                >
                  Resume Project
                </button>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Completed Projects -->
      {#if completedProjects.length > 0}
        <div class="completed-projects">
          <h3 class="text-lg font-semibold mb-3 flex items-center">
            🔵 Completed Projects ({completedProjects.length})
          </h3>
          
          <div class="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each completedProjects.slice(0, 6) as project}
              <div 
                class="project-card bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
                on:click={() => openProjectModal(project)}
              >
                <div class="project-header mb-3">
                  <h4 class="font-medium flex items-center">
                    <span class="text-xl mr-2">{getProjectType(project.type)?.icon}</span>
                    {project.title}
                    <span class="ml-2 text-xs text-blue-400">✅</span>
                  </h4>
                  <div class="text-sm text-gray-400">
                    {project.contributions?.length || 0} contributions • Completed {formatDate(project.completed_at)}
                  </div>
                </div>

                <div class="project-preview text-sm text-gray-300">
                  {project.description || project.preview || 'No description available'}
                </div>
              </div>
            {/each}
          </div>

          {#if completedProjects.length > 6}
            <div class="text-center mt-4">
              <span class="text-sm text-gray-400">
                And {completedProjects.length - 6} more completed projects...
              </span>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<!-- Create Project Modal -->
{#if showCreateModal}
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeCreateModal}>
    <div class="modal-content bg-gray-800 p-6 rounded-lg max-w-lg w-full mx-4" on:click|stopPropagation>
      <div class="modal-header flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold">Create New Collaborative Project</h3>
        <button 
          class="text-gray-400 hover:text-white text-2xl"
          on:click={closeCreateModal}
        >
          ×
        </button>
      </div>

      <div class="modal-body space-y-4">
        <!-- Project Title -->
        <div>
          <label class="block text-sm font-medium mb-2">Project Title</label>
          <input 
            type="text" 
            bind:value={newProjectData.title}
            placeholder="Enter a creative title..."
            class="w-full p-3 bg-gray-700 border border-gray-600 rounded"
          />
        </div>

        <!-- Project Type -->
        <div>
          <label class="block text-sm font-medium mb-2">Project Type</label>
          <div class="grid grid-cols-2 gap-2">
            {#each projectTypes as type}
              <button
                class="p-2 rounded border text-sm transition-colors {newProjectData.type === type.id ? 
                  'bg-purple-600 border-purple-500' : 'bg-gray-700 border-gray-600 hover:border-purple-500'}"
                on:click={() => newProjectData.type = type.id}
                title={type.description}
              >
                <div class="text-lg mb-1">{type.icon}</div>
                <div class="text-xs">{type.name}</div>
              </button>
            {/each}
          </div>
        </div>

        <!-- Collaboration Style -->
        <div>
          <label class="block text-sm font-medium mb-2">Collaboration Style</label>
          <select bind:value={newProjectData.collaboration_style} class="w-full p-2 bg-gray-700 border border-gray-600 rounded">
            {#each collaborationStyles as style}
              <option value={style.id}>{style.name} - {style.description}</option>
            {/each}
          </select>
        </div>

        <!-- Project Description -->
        <div>
          <label class="block text-sm font-medium mb-2">Description (Optional)</label>
          <textarea
            bind:value={newProjectData.description}
            placeholder="Describe your creative vision..."
            class="w-full p-3 bg-gray-700 border border-gray-600 rounded resize-none"
            rows="3"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer mt-6 flex justify-end gap-2">
        <button 
          class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded"
          on:click={closeCreateModal}
        >
          Cancel
        </button>
        <button 
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium"
          on:click={createProject}
          disabled={!newProjectData.title.trim()}
        >
          Create Project
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Project Detail Modal -->
{#if showProjectModal && selectedProject}
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeProjectModal}>
    <div class="modal-content bg-gray-800 p-6 rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" on:click|stopPropagation>
      <div class="modal-header flex items-center justify-between mb-4">
        <div>
          <h3 class="text-xl font-bold flex items-center">
            <span class="text-2xl mr-2">{getProjectType(selectedProject.type)?.icon}</span>
            {selectedProject.title}
          </h3>
          <div class="text-sm text-gray-400 flex items-center gap-4">
            <span>{getProjectType(selectedProject.type)?.name}</span>
            <span>•</span>
            <span class="flex items-center">
              {getProjectStatus(selectedProject.status)?.icon}
              {getProjectStatus(selectedProject.status)?.name}
            </span>
            <span>•</span>
            <span>{selectedProject.contributions?.length || 0} contributions</span>
          </div>
        </div>
        
        <button 
          class="text-gray-400 hover:text-white text-2xl"
          on:click={closeProjectModal}
        >
          ×
        </button>
      </div>

      <div class="modal-body space-y-6">
        <!-- Project Actions -->
        <div class="project-actions flex gap-2 flex-wrap">
          {#if selectedProject.status === 'active'}
            <button 
              class="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
              on:click={() => requestAIContribution(selectedProject.id)}
            >
              🤖 Request AI Contribution
            </button>
            <button 
              class="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm"
              on:click={() => updateProjectStatus(selectedProject.id, 'paused')}
            >
              ⏸️ Pause Project
            </button>
          {:else if selectedProject.status === 'paused'}
            <button 
              class="px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm"
              on:click={() => updateProjectStatus(selectedProject.id, 'active')}
            >
              ▶️ Resume Project
            </button>
          {/if}

          {#if selectedProject.status === 'active'}
            <button 
              class="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm"
              on:click={() => updateProjectStatus(selectedProject.id, 'completed')}
            >
              ✅ Mark Complete
            </button>
          {/if}
        </div>

        <!-- Project Progress -->
        <div class="project-progress bg-gray-900 p-4 rounded">
          <div class="flex justify-between items-center mb-2">
            <h4 class="font-medium">Project Progress</h4>
            <span class="text-sm text-gray-400">{calculateProgress(selectedProject).toFixed(0)}%</span>
          </div>
          <div class="bg-gray-700 rounded-full h-3">
            <div 
              class="bg-purple-500 h-full rounded-full transition-all duration-300"
              style="width: {calculateProgress(selectedProject)}%"
            ></div>
          </div>
          <div class="text-xs text-gray-400 mt-1">
            {selectedProject.contributions?.length || 0} of {selectedProject.target_contributions || 10} contributions
          </div>
        </div>

        <!-- Contributions Timeline -->
        {#if selectedProject.contributions && selectedProject.contributions.length > 0}
          <div class="contributions-timeline">
            <h4 class="font-medium mb-3">Contribution Timeline</h4>
            <div class="timeline space-y-4 max-h-96 overflow-y-auto">
              {#each selectedProject.contributions as contribution}
                <div class="contribution bg-gray-900 p-4 rounded">
                  <div class="contribution-header flex justify-between items-start mb-2">
                    <div class="flex items-center gap-2">
                      <div class="author-avatar w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center text-sm font-bold">
                        {contribution.author === 'user' ? 'U' : 'A'}
                      </div>
                      <div>
                        <div class="font-medium">{getContributionAuthor(contribution)}</div>
                        <div class="text-xs text-gray-400">{formatDateTime(contribution.created_at)}</div>
                      </div>
                    </div>
                    <div class="text-xs text-gray-500">#{contribution.sequence || 0}</div>
                  </div>
                  
                  <div class="contribution-content text-sm text-gray-300 whitespace-pre-wrap">
                    {contribution.content}
                  </div>

                  {#if contribution.type && contribution.type !== 'content'}
                    <div class="contribution-type text-xs text-purple-400 mt-2">
                      Type: {contribution.type}
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          </div>

          <!-- Add Contribution Form -->
          {#if selectedProject.status === 'active'}
            <div class="add-contribution bg-gray-900 p-4 rounded">
              <h4 class="font-medium mb-3">Add Your Contribution</h4>
              <form on:submit|preventDefault={(e) => {
                const content = e.target.content.value;
                if (content.trim()) {
                  addContribution(selectedProject.id, content);
                  e.target.content.value = '';
                }
              }}>
                <textarea
                  name="content"
                  placeholder="Write your contribution to the project..."
                  class="w-full p-3 bg-gray-700 border border-gray-600 rounded resize-none mb-3"
                  rows="4"
                ></textarea>
                <div class="flex justify-end">
                  <button 
                    type="submit"
                    class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium"
                  >
                    Add Contribution
                  </button>
                </div>
              </form>
            </div>
          {/if}
        {:else}
          <div class="no-contributions bg-gray-900 p-6 rounded text-center">
            <div class="text-2xl mb-2">📝</div>
            <h4 class="font-medium mb-2">No Contributions Yet</h4>
            <p class="text-sm text-gray-400 mb-4">
              Start adding content to begin your collaborative project
            </p>
            
            {#if selectedProject.status === 'active'}
              <button 
                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded"
                on:click={() => requestAIContribution(selectedProject.id)}
              >
                Get AI Started
              </button>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .timeline::-webkit-scrollbar {
    width: 4px;
  }
  
  .timeline::-webkit-scrollbar-track {
    background: #374151;
  }
  
  .timeline::-webkit-scrollbar-thumb {
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
