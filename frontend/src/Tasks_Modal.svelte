<script>
	let { show_tasks_modal = $bindable(), openTaskTitle = $bindable(), add_tasks_modal = $bindable(), header, children } = $props();


	let dialog = $state(); // HTMLDialogElement

	$effect(() => {
		if (show_tasks_modal) dialog.showModal();
	});
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
<dialog
	bind:this={dialog}
	onclose={() => {show_tasks_modal = false; openTaskTitle = null; add_tasks_modal = false;}}
	onclick={(e) => { if (e.target === dialog) dialog.close(); }}
>
	<div>
		{@render header?.()}
		<!-- <hr /> -->
		{@render children?.()}
		<!-- <hr /> -->
		<!-- svelte-ignore a11y_autofocus -->
		<!-- <button autofocus onclick={() => dialog.close()}>Close</button> -->
	</div>
</dialog>

<style>
	dialog {
		max-width: 32em;
		border-radius: 0.2em;
		border: none;
		padding: 0;
	}
	dialog::backdrop {
		background: rgba(0, 0, 0, 0.3);
	}
	dialog > div {
		padding: 1em;
	}
	dialog[open] {
		animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	@keyframes zoom {
		from {
			transform: scale(0.95);
		}
		to {
			transform: scale(1);
		}
	}
	dialog[open]::backdrop {
		animation: fade 0.2s ease-out;
	}
	@keyframes fade {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	button {
		display: block;
	}
</style>