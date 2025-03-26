<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import Tally_1 from 'lucide-svelte/icons/tally-1';
	import TaskCard from './(components)/task-card.svelte';
	import { type TaskStatus } from './+page.server';

	let { data } = $props();
	let tasks: TaskStatus[] = data.content!;
</script>

<Sidebar.Inset>
	<header class="flex h-16 shrink-0 items-center gap-2">
		<div class="flex items-center gap-2 px-4">
			<Sidebar.Trigger />
			<Breadcrumb.Root>
				<Breadcrumb.List>
					<Breadcrumb.Separator>
						<Tally_1 />
					</Breadcrumb.Separator>
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/">Home</Breadcrumb.Link>
					</Breadcrumb.Item>
					<Breadcrumb.Separator />
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/task">Tasks</Breadcrumb.Link>
					</Breadcrumb.Item>
				</Breadcrumb.List>
			</Breadcrumb.Root>
		</div>
	</header>
	<main>
		<div class="items-center justify-between px-4">
			<div class="text-4xl">All Tasks Overview</div>
			<div class="flex flex-wrap items-center gap-4 p-2">
				{#each tasks as data (data.key)}
					<TaskCard {data} />
				{/each}
			</div>
		</div>
	</main>
</Sidebar.Inset>