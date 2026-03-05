<script lang="ts">
      import { onMount } from 'svelte';
      import Calendar from './calendar.svelte';
    import Teams from './Teams.svelte';
    import Dashboard from './dashboard.svelte';


  let user: { name: any; picture: any; } | null = $state(null);

  onMount(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/me", {
    credentials: "include" 
      });
      if (res.ok) {
        user = await res.json();
      }
    } catch (e) {
      console.error("Failed to fetch user", e);
    }
  });

  const login = () => window.location.href = "http://localhost:8000/login";
  const logout = () => window.location.href = "http://localhost:8000/logout";
  const log_user = () => console.log(user);

  // Screen state
  let currentScreen: 'welcome' | 'login' | 'signup' | 'teams' | 'calendar' | 'dashboard' = $state('welcome');
  
</script>

<!-- {#if user}
  <button on:click={logout}>Logout</button>
  <button on:click={log_user}>Log User</button>
{:else}
  <button on:click={login}>Login with Google</button>
{/if} -->


<main>
    {#if user && currentScreen == 'calendar'}
        <Calendar user={user.name} profile_picture={user.picture}/>
    {:else if user && currentScreen == 'teams'}
        <Teams user={user.name} bind:full_user={user}/>
    {:else if user}
        <Dashboard userId={user.name} bind:currentScreen={currentScreen} bind:full_user={user}/>
    {/if}




  <!-- Welcome Screen(keep this for now) -->
  {#if !user}
    <div class="welcome-container">
      <div class="welcome-content">
        <h1>Welcome</h1>
        <div class="auth-options">
          <button on:click={login}>Log in</button>
          <span>or</span>
          <button on:click={() => currentScreen = 'signup'}>Create an Account</button>
        </div>
      </div>
    </div>
    {/if}
</main>