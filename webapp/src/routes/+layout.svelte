<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import AppSidebar from './(components)/app-sidebar.svelte';
	import type { LayoutProps } from './$types';
	import '../app.css';

	let { data, children }: LayoutProps = $props();
</script>

<Sidebar.Provider>
	<AppSidebar {data} />
	{@render children?.() }
</Sidebar.Provider>