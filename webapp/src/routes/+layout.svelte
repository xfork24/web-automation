<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import AppSidebar from './(components)/app-sidebar.svelte';
	import '../app.css';

	let { children } = $props();
</script>

<Sidebar.Provider>
	<AppSidebar />
	{@render children?.()}
</Sidebar.Provider>