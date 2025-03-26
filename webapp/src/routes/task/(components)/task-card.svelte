<script lang="ts">
	import BellRing from '@lucide/svelte/icons/bell-ring';
	import Check from '@lucide/svelte/icons/check';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Card from '$lib/components/ui/card/index.js';

	let { data } = $props();

</script>

<a href={data.link}>
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-nowrap">{data.title}</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4">
			<div>
				{#each Object.entries(data) as [status, count]}
					{#if status !== 'key' && status !== 'title' && status !== 'link'}
						<div class="flex items-center justify-between space-x-4">
							<span class="text-xl font-medium leading-none float-left">
								{status}
							</span>
							<span class="text-muted-foreground text-xl float-right">
								{count}
							</span>
						</div>
					{/if}
				{/each}
			</div>
		</Card.Content>
	</Card.Root>
</a>