<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto } from '$app/navigation';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import type { ShopSearchCrawlTask } from '../../../(components)/model';

	let { row, user } = $props();

	let open = $state(false);

	async function createShopSearchCrawlTask(row: ShopSearchCrawlTask) {
		try {
			const response = await fetch('http://localhost:8000/api/v1/shop_search_task', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				},
				body: JSON.stringify({
					'shop_name': row.shop_name,
					'update_id': user.name
				})
			});
			const result = await response.json();
			console.log(result);
			if (result.code == 0) {
				open = false;
				return;
			}
		} catch (error) {
			console.error(`Error in function: ${error}`);
		}
	}

	async function onNavShopClicked(shop_name: string) {
		try {
			const response = await fetch(`http://localhost:8000/api/v1/shop/${shop_name}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				}
			});
			const body = await response.json();
			window.open(body.data.shop_link, '_blank');
		} catch (error) {
			console.error(`Error in load function: ${error}`);
		}
	}
</script>

<Dialog.Root bind:open>
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
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item>
						<span>Resubmit Task</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
			</DropdownMenu.Group>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Are you sure absolutely sure?</Dialog.Title>
			<Dialog.Description>
				This action will add a shop search crawl task.<br>
				The task will be scheduled later.
			</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer>
			<Button type="reset" onclick={() => open = false}>Cancel</Button>
			<Button type="submit" class="bg-red-500 hover:bg-red-500" onclick={() => createShopSearchCrawlTask(row)}>Continue
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>