<script lang="ts">
   // Teams data
  let teams: Record<string, any> = {};
  export let user;
  export let full_user;
  let currentUser: { id?: string, email?: string } = {id: user};
  let isLoading: boolean = false;
  let teamError: string | null = null;
  let createTeamError: string | null = null;
  let selectedTeam: string | null = null;
  let tasks: any[] = [];
  let taskError: string | null = null;
  let currentScreen = "teams";


// Task management
  let newTask = {
    name: "",
    description: "",
    team: "",
    assignees: [] as string[],
    priority: "Medium",
    dueDate: "",
    location: ""
  };
  let newAssignee = "";
  let newTeamName = "";
  let showTaskModal = false;


  // Team functions
  async function fetchTeams() {
    if (!currentUser.id) return;
    
    try {
      isLoading = true;
      const response = await fetch(`http://localhost:8000/get_teams/${currentUser.id}`);
      const data = await response.json();
      teams = data.teams || {};
    } catch (err) {
      teamError = "Failed to load teams";
    } finally {
      isLoading = false;
    }
  }

  async function createTeam() {
    if (!newTeamName.trim()) {
      createTeamError = "Please enter a team name";
      return;
    }
    if (!currentUser.id) {
      createTeamError = "You must be logged in to create a team";
      return;
    }

    createTeamError = null;
    isLoading = true;

    try {
      const response = await fetch("http://localhost:8000/create_team_task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUser.id,
          task_name: `Initial task for ${newTeamName}`,
          task_description: "Starter task created with the team",
          task_team: newTeamName,
          task_assignees: [currentUser.id],
          task_priority: "Medium",
          task_due_date: null
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        createTeamError = data.error || "Failed to create team";
        return;
      }

      newTeamName = "";
      await fetchTeams();
    } catch (err) {
      createTeamError = "Network error creating team";
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  // Task functions
  async function viewTeamTasks(teamName: string) {
    selectedTeam = teamName;
    isLoading = true;
    taskError = null;

    try {
      const response = await fetch(`http://localhost:8000/get_tasks/${currentUser.id}`);
      const data = await response.json();
      tasks = data.tasks || [];
    } catch (err) {
      taskError = "Failed to load tasks.";
      tasks = [];
    } finally {
      isLoading = false;
    }
  }

  function addAssignee() {
    if (newAssignee.trim() && !newTask.assignees.includes(newAssignee)) {
      newTask.assignees = [...newTask.assignees, newAssignee.trim()];
      newAssignee = "";
    }
  }

  async function createTeamTask() {
    if (!newTask.name.trim()) {
      createTeamError = "Please enter a task name";
      return;
    }

    try {
      isLoading = true;
      const response = await fetch("http://localhost:8000/create_team_task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUser.id,
          task_name: newTask.name,
          task_description: newTask.description,
          task_team: newTask.team,
          task_assignees: newTask.assignees,
          task_priority: newTask.priority,
          task_due_date: newTask.dueDate || null,
          task_location: newTask.location
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || "Failed to create task");
      }

      closeTaskModal();
      await fetchTeams();
    } catch (err) {
      createTeamError = err.message;
    } finally {
      isLoading = false;
    }
  }

  function getUniqueMembers(teamTasks) {
    const members = new Set();
    Object.values(teamTasks).forEach(task => {
      (task.task_assignees || []).forEach(member => members.add(member));
    });
    return Array.from(members);
  }

  function formatDate(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  }

  function openTaskModal() {
    newTask.team = Object.keys(teams)[0] || "";
    showTaskModal = true;
  }

  function closeTaskModal() {
    showTaskModal = false;
    newTask = {
      name: "",
      description: "",
      team: "",
      assignees: [],
      priority: "Medium",
      dueDate: "",
      location: ""
    };
  }
</script>

{#if currentScreen === 'teams'}
    <div class="teams-dashboard">
      <header class="teams-header">
        <h1>Team Dashboard</h1>
        <button on:click={full_user = null} class="logout-button">Logout</button>
      </header>

      <div class="teams-content">
        <div class="teams-list">
          {#if isLoading && Object.keys(teams).length === 0}
            <div class="loading">Loading teams...</div>
          {:else if Object.keys(teams).length === 0}
            <div class="no-teams">You don't have any teams yet</div>
          {:else}
            {#each Object.entries(teams) as [teamName, teamTasks]}
              <div class="team-card">
                <div class="team-header">
                  <h3>{teamName}</h3>
                  <div class="team-actions">
                    <button on:click={() => viewTeamTasks(teamName)}>View All</button>
                  </div>
                </div>
                
                <div class="team-stats">
                  <span>Members: {getUniqueMembers(teamTasks).length}</span>
                  <span>Tasks: {Object.keys(teamTasks).length}</span>
                </div>
                
                <div class="task-list">
                  {#each Object.entries(teamTasks).slice(0, 3) as [taskId, task]}
                    <div class="task-item priority-{task.task_priority.toLowerCase()}">
                      <div class="task-header">
                        <h4>{task.task_name}</h4>
                        <span class="priority">{task.task_priority}</span>
                      </div>
                      {#if task.task_description}
                        <p class="task-description">{task.task_description}</p>
                      {/if}
                      {#if task.task_due_date}
                        <div class="task-due">
                          Due: {formatDate(task.task_due_date)}
                        </div>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          {/if}
        </div>

        <div class="teams-actions">
          <button on:click={openTaskModal} class="create-task-button">
            <span>Create New Task</span>
            <span class="plus-icon">+</span>
          </button>
          
          <div class="create-team">
            <h2>Create New Team</h2>
            <input 
              type="text" 
              bind:value={newTeamName}
              placeholder="Enter team name"
              class="team-input"
            >
            {#if createTeamError}
              <div class="error-message">{createTeamError}</div>
            {/if}
            <button on:click={createTeam} class="create-button" disabled={isLoading}>
              {#if isLoading}Creating...{:else}Create Team{/if}
            </button>
          </div>
        </div>
      </div>

      <!-- Task Modal -->
      {#if showTaskModal}
        <div class="modal-overlay" on:click|self={closeTaskModal}>
          <div class="task-modal">
            <button class="close-modal" on:click={closeTaskModal}>×</button>
            <h2>Create New Task</h2>
            
            <form on:submit|preventDefault={createTeamTask}>
              <div class="form-group">
                <label for="task-name">Task Name</label>
                <input
                  type="text"
                  id="task-name"
                  bind:value={newTask.name}
                  placeholder="Enter task name here"
                  required
                />
              </div>

              <div class="form-group">
                <label for="task-description">Description</label>
                <textarea
                  id="task-description"
                  bind:value={newTask.description}
                  placeholder="Enter any comments or task description"
                  rows="3"
                ></textarea>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Team</label>
                  <select bind:value={newTask.team}>
                    {#each Object.keys(teams) as team}
                      <option value={team}>{team}</option>
                    {/each}
                  </select>
                </div>

                <div class="form-group">
                  <label>Assign To</label>
                  <div class="assignee-list">
                    {#each newTask.assignees as assignee, i}
                      <div class="assignee-tag">
                        <span>{assignee}</span>
                        <button type="button" on:click={() => newTask.assignees.splice(i, 1)}>
                          ×
                        </button>
                      </div>
                    {/each}
                    <input
                      type="text"
                      bind:value={newAssignee}
                      placeholder="Add assignee"
                      on:keydown={(e) => e.key === 'Enter' && addAssignee()}
                    />
                  </div>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Priority</label>
                  <select bind:value={newTask.priority}>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Due Date</label>
                  <input
                    type="datetime-local"
                    bind:value={newTask.dueDate}
                  />
                </div>
              </div>

              <div class="form-group">
                <label>Location (Optional)</label>
                <input
                  type="text"
                  bind:value={newTask.location}
                  placeholder="Add location"
                />
              </div>

              <div class="form-actions">
                <button type="button" class="cancel-button" on:click={closeTaskModal}>
                  Cancel
                </button>
                <button type="submit" class="submit-button" disabled={isLoading}>
                  {#if isLoading}Creating...{:else}Create Task{/if}
                </button>
              </div>
            </form>
          </div>
        </div>
      {/if}
    </div>
  {/if}
  
  <style>
  .create-task-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #687D31;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .task-modal {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    padding: 2rem;
    position: relative;
  }
</style>