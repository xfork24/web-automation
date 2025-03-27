<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto } from '$app/navigation';
	import type { ShopInfo } from '../../(components)/model';
	import * as Dialog from '$lib/components/ui/dialog/index.js';

	let open = $state(false);

	let { row, user } = $props();

	async function createShopCrawlTask(row: ShopInfo) {
		try {
			const response = await fetch('http://localhost:8000/api/v1/shop_task', {
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
				<DropdownMenu.Item onclick={() => window.open(row.shop_link, '_blank')}>
					Taobao Shop Page
				</DropdownMenu.Item>
			</DropdownMenu.Group>
			<DropdownMenu.Separator />
			<DropdownMenu.Group>
				<DropdownMenu.GroupHeading>Actions</DropdownMenu.GroupHeading>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item>
						<span>Crawl Product</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<DropdownMenu.Item onclick={() => goto('/shop/' + row.shop_name)}>View Shop Products
				</DropdownMenu.Item>
			</DropdownMenu.Group>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Are you sure absolutely sure?</Dialog.Title>
			<Dialog.Description>
				This action will add a shop crawl task.<br>
				The task will be scheduled later.
			</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer>
			<Button type="reset" onclick={() => open = false}>Cancel</Button>
			<Button type="submit" class="bg-red-500 hover:bg-red-500" onclick={() => createShopCrawlTask(row)}>Continue
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>