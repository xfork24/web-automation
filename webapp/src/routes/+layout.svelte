<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import AppSidebar from './(components)/app-sidebar.svelte';
	import '../app.css';

	let { children } = $props();
</script>

<Sidebar.Provider>

	<AppSidebar />

	<Sidebar.Inset>
		<header class="flex h-12 items-center justify-between px-4">
			<Sidebar.Trigger />
		</header>
		<main>
				{@render children?.()}
		</main>
	</Sidebar.Inset>

</Sidebar.Provider>