<script>
	let { add_tasks_modal = $bindable(), add_task_date = $bindable(), header, children } = $props();

	let dialog = $state(); // HTMLDialogElement

	$effect(() => {
		if (add_tasks_modal) dialog.showModal();
	});
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
<dialog
	bind:this={dialog}
	onclose={() => {add_tasks_modal = false; add_task_date = null}}
	onclick={(e) => { if (e.target === dialog) dialog.close(); }}
>
	<div>
		{@render header?.()}
		{@render children?.()}
		<!-- <button autofocus onclick={() => dialog.close()}>Close</button> -->
		<!-- <button onclick={() => dialog.close()}>Close</button> -->
	</div>
	<!-- <button autofocus onclick={() => dialog.close()}>Close</button> -->
</dialog>

<style>
	dialog {
		max-width: 400px;
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