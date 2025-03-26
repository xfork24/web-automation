<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto } from '$app/navigation';

	let { row } = $props();

	async function onNavShopClicked(shop_name: string) {
		try {
			const response = await fetch(`http://localhost:8000/api/v1/shop/${shop_name}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8',
				}
			});
			const body = await response.json();
			window.open(body.data.shop_link, '_blank');
		} catch (error) {
			console.error(`Error in load function: ${error}`);
		}
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button
				{...props}
				variant="ghost"
				size="icon"
				class="relative size-8 p-0"
			>
				<span class="sr-only">Open menu</span>
				<Ellipsis />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		<DropdownMenu.Group>
			<DropdownMenu.GroupHeading>Navigate to</DropdownMenu.GroupHeading>
			<DropdownMenu.Item onclick={() => onNavShopClicked(row.shop_name)}>
				Taobao Shop Page
			</DropdownMenu.Item>
		</DropdownMenu.Group>
		<DropdownMenu.Separator />
		<DropdownMenu.Group>
			<DropdownMenu.GroupHeading>Actions</DropdownMenu.GroupHeading>
			<DropdownMenu.Item>Resubmit Task</DropdownMenu.Item>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>