<script lang="ts">
  import { onMount } from 'svelte';
  import Calendar from './calendar.svelte';
  import taskifyLogo from './assets/Taskify.svg';
  import Teams from './Teams.svelte';


  let user: { name: any; picture: any; } | null = null;

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
  let currentScreen: 'welcome' | 'login' | 'signup' | 'teams' = 'welcome';
  
</script>

{#if user}
  <button on:click={logout}>Logout</button>
  <!-- <button on:click={log_user}>Log User</button> -->
{:else}
  <button on:click={login}>Login with Google</button>
{/if}


<main>
    {#if user}
      <Calendar user={user.name} profile_picture={user.picture}/>
    {/if}



  <!-- Welcome Screen(keep this for now) -->
  {#if currentScreen === 'welcome'}
    <div class="welcome-container">
      <div class="welcome-content">
        <h1>Welcome</h1>
        <div class="auth-options">
          <button on:click={() => currentScreen = 'login'}>Log in</button>
          <span>or</span>
          <button on:click={() => currentScreen = 'signup'}>Create an Account</button>
        </div>
      </div>
    </div>
    {/if}
</main>
