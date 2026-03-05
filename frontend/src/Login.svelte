<script lang="ts">

//not needed anymore with using google OAuth
  export let onLogin: (user: { id: string; email: string }) => void;

  let email = "";
  let password = "";
  let rememberMe = false;
  let loginError: string | null = null;
  let isLoading = false;

  async function handleLogin() {
    if (!email || !password) {
      loginError = "Please enter both email and password";
      return;
    }

    try {
      isLoading = true;
      const user = { id: `user_${Date.now()}`, email };
      // Optionally call your real login endpoint here.
      // await fetch(...);
      onLogin(user);
    } catch {
      loginError = "Login failed";
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="login-form">
  <h2>Welcome Back</h2>
  <form on:submit|preventDefault={handleLogin}>
    <input type="email" placeholder="Email" bind:value={email} required />
    <input type="password" placeholder="Password" bind:value={password} required />
    <label><input type="checkbox" bind:checked={rememberMe} /> Remember me</label>
    {#if loginError}<div class="error">{loginError}</div>{/if}
    <button type="submit" disabled={isLoading}>
      {isLoading ? 'Loading...' : 'Log in'}
    </button>
  </form>
</div>
