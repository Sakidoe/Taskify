<script lang="ts">
  import Task from "./task.svelte";
  import toggleOn from "./public/toggle_on.svg";
  import toggleOff from "./public/toggle_off.svg";

  let sidebarOpen = false;

  let tasks = [];

  let newTaskTitle = "";
  let newTaskTag = "";
  let newTaskPriority = "medium";
  let showCreateForm = false;
  const userId = "jon"; //hardcoded

  async function fetchTasks() {
    const res = await fetch(`http://localhost:8000/get_tasks/${userId}`, {
      credentials: "include"
    });
    const data = await res.json();
    if (data.tasks && typeof data.tasks === "object") {
      tasks = Object.entries(data.tasks).map(([title, t]: any, i) => ({
        id: i + 1,
        title,
        date: t.task_date,
        tag: t.task_tags,
        priority: t.task_priority,
        status: t.status ?? "task" // fallback to default
      }));
    }
  }

  async function deleteTask(title) {
    try {
      const res = await fetch('http://localhost:8000/delete_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id:    userId,
          task_title: title
        })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      if (data.success) {
        // Remove it locally
        tasks = tasks.filter(t => t.task_name !== title);
      } else {
        console.warn('Unexpected delete response:', data);
      }
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  }
  // async function createTask() {
  //   if (!newTaskTitle || !newTaskTag) return alert("Fill out all fields.");
  //   await fetch("http://localhost:8000/create_task", {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify({
  //       user_id: userId,
  //       task_name: newTaskTitle,
  //       task_description: "n/a",
  //       task_location: "n/a",
  //       task_color: "gray",
  //       task_label: "n/a",
  //       task_start_time: "00:00",
  //       task_end_time: "01:00",
  //       task_date: "unknown",
  //       task_tags: newTaskTag,
  //       task_priority: newTaskPriority,
  //       status: "task"
  //     }),
  //   });
  //   newTaskTitle = "";
  //   newTaskTag = "";
  //   newTaskPriority = "medium";
  //   showCreateForm = false;
  //   fetchTasks();
  // }

  async function updateStatus(taskId: number, newStatus: string) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    task.status = newStatus;

    await fetch("http://localhost:8000/update_task_status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, task_name: task.title, new_status: newStatus })
    });
  }

  // Derived groups
  $: taskGroup = tasks.filter(t => t.status === "task");
  $: inProgressGroup = tasks.filter(t => t.status === "in-progress");
  $: completedGroup = tasks.filter(t => t.status === "completed");

  fetchTasks();
  let colorblind = false;
  function toggleColorblind() {
    colorblind = !colorblind;
    if (colorblind) {
      document.documentElement.classList.add('colorblind');
    } else {
      document.documentElement.classList.remove('colorblind');
    }
  }

</script>


<main class="layout" class:colorblind={colorblind}>
  <div class:sidebar-open={sidebarOpen} class="sidebar">
    <div class="close-btn" on:click={() => sidebarOpen = false}>X</div>
    <h2>NAME</h2>
    <button class="nav-btn">dashboard</button>
    <button class="nav-btn">teams</button>
    <button class="nav-btn">calendar</button>
    <div class="logout-container">
      <div class="logout-icon"></div>
      <span>logout</span>
    </div>
    <img
      src={colorblind ? toggleOn : toggleOff}
      alt="Toggle colorblind mode"
      class="color-toggle"
      on:click={toggleColorblind}
    />
  </div>

  <div class:shifted={sidebarOpen} class="main-content">
    <header class="header">
      <div class="logo" on:click={() => sidebarOpen = true}></div>
      <p class="title-header">Dashboard</p>
    </header>

    <section class="board">
      <div class="column">
        <h2>task</h2>
        {#each tasks as task, index}
          <div class="task-card">
            <div class="close">
                <button 
                on:click={() => { 
                  deleteTask(task.title).then(() => fetchTasks()); 
                }} 
                class="closeTask"
              >
                X
              </button>
            </div>
            <div class="task-header">
              <span>{task.title}</span>
              <span class="task-date">{task.date}</span>
            </div>
            <div class="task-details">
              <div class="tag">{task.tag}</div>
              <div>priority: {task.priority}</div>

              <div class="checkbox-wrapper">
                <input 
                  type="checkbox" 
                  id="task-{index}" 
                  name="task-{index}" 
                  class="styled-checkbox"
                />
                <label for="task-{index}">{task.tag}</label>
              </div>
            </div>
          </div>
        {/each}

        <!-- <div class="task-card empty"></div> -->
        <div class="create-task">
          <button on:click={() => { showCreateForm = true }}>+</button>
          <p>Create a new task</p>
        </div>
        
        {#if showCreateForm}
          <Task
            on:close={() => showCreateForm = false}
            on:taskCreated={() => {
              showCreateForm = false; // Close the form
              fetchTasks(); // Refresh the tasks
            }}
          />
        {/if}

      </div>

      <div class="column">
        <h2>in-progress</h2>
        <div class="task-card empty"></div>
        <div class="task-card empty"></div>
      </div>

      <div class="column">
        <h2>completed</h2>
        <div class="task-card empty"></div>
        <div class="task-card empty"></div>
      </div>
    </section>
  </div>
</main>

<style>
  :root {
    /* Default color variables */
    --background-color: #dbe1d7; 
    --sidebar-color: #4a572a;
    --nav-btn-color: #6f7d4c;
    --logout-icon-color: #8a9a5b;
    --header-color: #3d4c1c;
    --task-card-color: #5b6d2f;
    --tag-color: #8c9c61;
    --in-progress-color: #88a595;
    --completed-color: #99b6db;
    --empty-task-in-progress: #84a89d;
    --empty-task-completed: #9bbfe8;
    --text-color: #f9f9f9;
    --button-text-color: #5b6d2f;
    --checkbox-border-color: white;
    --checkbox-checked-color: white;
    --checkbox-tick-color: #5b6d2f;
  }

  :root.colorblind {
    --background-color: #C9C9C9; 
    --sidebar-color: #1B4F72; 
    --nav-btn-color: #C9C9C9; 
    --logout-icon-color: #7f8c8d; 
    --header-color: #2c3e50;
    --task-card-color: #0072B2; 
    --tag-color: #bdc3c7; 
    --in-progress-color: #009E73;
    --completed-color: #56B4E9; 
    --empty-task-in-progress: #009E73; 
    --empty-task-completed: #56B4E9; 
    --text-color: #000000; 
    --button-text-color: #34495e;
    --checkbox-border-color: #000000; 
    --checkbox-checked-color: #000000; 
    --checkbox-tick-color: #ffffff; 
  }

  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');

  html, body {
    margin: 0;
    padding: 0;
    border: none;
    background-color: var(--background-color);
    height: 100%;
    width: 100%;
    overflow-x: hidden;
  }

  * {
    font-family: 'Playfair Display', serif;
    box-sizing: border-box;
  }

  .layout {
    display: flex;
    border: none;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: -320px;
    width: 320px;
    height: 100vh;
    background-color: var(--sidebar-color);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    transition: left 0.3s ease;
    z-index: 10;
    color: var(--text-color);
  }

  .sidebar-open {
    left: 0;
  }

  .color-toggle {
    position: absolute;
    bottom: 0;
    right: 1rem;
    width: 64px;
    height: 64px;
    cursor: pointer;
  }
  /* .colorblind {
    /* override your colors via variables or selectors here */
  /* } */

  .close-btn {
    align-self: flex-end;
    cursor: pointer;
    font-size: 1.2rem;
    color: white;
  }

  .nav-btn {
    background-color: var(--nav-btn-color);
    border: none;
    padding: 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-size: 1rem;
    color: var(--text-color);
  }

  .logout-container {
    margin-top: auto;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    color: var(--text-color);
  }

  .logout-icon {
    width: 24px;
    height: 24px;
    background-color: var(--logout-icon-color);
    border-radius: 4px;
  }

  .main-content {
    margin-left: 0;
    padding: 1rem;
    flex: 1;
    transition: margin-left 0.3s ease;
    width: 100%;
    background-color: var(--background-color);
  }

  .main-content.shifted {
    margin-left: 320px;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .logo {
    width: 40px;
    height: 40px;
    background-color: var(--header-color);
    cursor: pointer;
  }

  .title-header {
    text-align: center;
    width: 100%;
    font-size: 30px;
    background-color: white;
    padding: 0.5rem 2rem;
    border: 0.5px solid #556b2f;
    border-radius: 5px;
  }

  .board {
    display: flex;
    gap: 2rem;
  }

  .column {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .column h2 {
    text-align: center;
    padding: 0.5rem;
    border-radius: 6px;
    color: white;
  }

  .column:nth-child(1) h2 {
    background-color: var(--task-card-color);
  }

  .column:nth-child(2) h2 {
    background-color: var(--in-progress-color);
  }

  .column:nth-child(3) h2 {
    background-color: var(--completed-color);
  }

  .task-card {
    position: relative;
    background-color: var(--task-card-color);
    color: white;
    padding: 1rem;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .task-header {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
  }

  .task-details {
    font-size: 0.9rem;
  }

  .tag {
    background-color: var(--tag-color);
    display: inline-block;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    color: white;
  }

  /* Default empty style fallback */
  .task-card.empty {
    height: 100px;
    border-radius: 10px;
  }

  /* Specific column background styles */
  .column:nth-child(2) .task-card.empty {
    background-color: var(--empty-task-in-progress); /* same as in-progress header */
  }

  .column:nth-child(3) .task-card.empty {
    background-color: var(--empty-task-completed); /* same as completed header */
  }


  .create-task {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: var(--task-card-color);
    padding: 0.5rem;
    border-radius: 6px;
    color: white;
  }

  .create-task button {
    background-color: white;
    border: none;
    width: 24px;
    height: 24px;
    border-radius: 4px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    color: var(--button-text-color);
  }

  .checkbox-wrapper {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .styled-checkbox {
    appearance: none;
    width: 1.2rem;
    height: 1.2rem;
    border: 2px solid white;
    border-radius: 0.25rem;
    transition: all 0.2s ease;
    cursor: pointer;
    position: relative;
    background-color: transparent;
  }

  .styled-checkbox:checked {
    background-color: white;
    border-color: white;
  }

  .styled-checkbox:checked::after {
    content: '';
    position: absolute;
    left: 0.35rem;
    top: 0.05rem;
    width: 0.25rem;
    height: 0.6rem;
    border: solid #5b6d2f;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
  }

  .close {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    cursor: pointer;
  }

  .closeTask {
    background: none;
    border: none;
    font-size: 1rem;
    font-weight: bold;
    color: #f9f9f9;
    cursor: pointer;
  }
  html, body {
  margin: 0;
  padding: 0;
  background-color: var(--background-color); /* muted green-gray */
  height: 100%;
  width: 100%;
  overflow-x: hidden;
}

:global(body) {
  background-color: var(--background-color);
}

</style>
