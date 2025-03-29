<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto, invalidateAll } from '$app/navigation';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import type { ShopSearchCrawlTask } from '../../../(components)/model';

	let { row, user } = $props();

	let open = $state(false);
	let dialog_title = $state('Are you sure?');
	let dialog_body = $state('');
	let handler = $state(async function(_: ShopSearchCrawlTask) {
	});

	function beforeCreateShopSearchDialog() {
		dialog_body = 'This action will add a shop search crawl task. The task will be scheduled later.';
		handler = createShopSearchCrawlTask;
	}

	function beforeDeleteShopSearchDialog() {
		dialog_body = 'This action will try to delete a shop search crawl task. You must fix all external constraints before this operation can be done.';
		handler = deleteShopSearchCrawlTask;
	}

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
			if (result.code == 0) {
				open = false;
				await invalidateAll();
				return;
			}
		} catch (error) {
			console.error(`Error in function: ${error}`);
		}
	}

	async function deleteShopSearchCrawlTask(row: ShopSearchCrawlTask) {
		try {
			const response = await fetch(`http://localhost:8000/api/v1/shop_search_task/${row.id}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				}
			});
			const result = await response.json();
			if (result.code == 0) {
				open = false;
				await invalidateAll();
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
					<DropdownMenu.Item onclick={() => beforeCreateShopSearchDialog()}>
						<span>Resubmit Task</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeDeleteShopSearchDialog()}>
						<span>Delete Task</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
			</DropdownMenu.Group>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>{dialog_title}</Dialog.Title>
			<Dialog.Description>
				{dialog_body}
			</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer>
			<Button type="reset" onclick={() => open = false}>Cancel</Button>
			<Button type="submit" class="bg-red-500 hover:bg-red-500" onclick={() => handler(row)}>Continue
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>