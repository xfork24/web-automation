<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import {
		Button
	} from '$lib/components/ui/button/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto, invalidateAll } from '$app/navigation';
	import type { ProductInfo } from '../../(components)/model';

	import * as Dialog from '$lib/components/ui/dialog/index.js';

	let { row, user } = $props();

	let open = $state(false);
	let dialog_title = $state('Are you sure?');
	let dialog_body = $state('');
	let handler = $state(async function(_: ProductInfo) {
	});

	function beforeCrawlProductDialog() {
		dialog_body = 'This action will add a product crawl task. The task will be scheduled later.';
		handler = createDetailCrawlTask;
	}

	function beforeCrawlProductInShopDialog() {
		dialog_body = 'This action will add a shop crawl task with target product. The task(s) will be scheduled later.';
		handler = createShopCrawlTask;
	}

	function beforeDeleteProductDialog() {
		dialog_body = 'This action will try to delete a product. You must fix all external constraints before this operation can be done.';
		handler = deleteProduct;
	}

	async function createDetailCrawlTask(row: ProductInfo) {
		try {
			const response = await fetch('http://localhost:8000/api/v1/detail_task', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				},
				body: JSON.stringify({
					'product_id': row.product_id,
					'product_link': row.product_link,
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

	async function createShopCrawlTask(row: ProductInfo) {
		try {
			const response = await fetch('http://localhost:8000/api/v1/shop_task', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				},
				body: JSON.stringify({
					'shop_name': row.shop_name,
					'target_product_ids': [row.product_id],
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

	async function deleteProduct(row: ProductInfo) {
		try {
			const response = await fetch(`http://localhost:8000/api/v1/product/${row.product_id}?update_id=${user.name}`, {
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
				<DropdownMenu.GroupHeading>Copy IDs</DropdownMenu.GroupHeading>
				<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.product_id)}>
					Copy Product ID
				</DropdownMenu.Item>
				<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.sku_id)}>
					Copy SKU ID
				</DropdownMenu.Item>
				<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.shop_name)}>
					Copy Shop Name
				</DropdownMenu.Item>
				<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.update_id)}>
					Copy Operator ID
				</DropdownMenu.Item>
			</DropdownMenu.Group>
			<DropdownMenu.Separator />
			<DropdownMenu.Group>
				<DropdownMenu.GroupHeading>Navigate to</DropdownMenu.GroupHeading>
				<DropdownMenu.Item onclick={() => window.open(row.product_link, '_blank')}>
					Taobao Product Page
				</DropdownMenu.Item>
				<DropdownMenu.Item onclick={() => window.open(row.shop_link, '_blank')}>
					Taobao Shop Page
				</DropdownMenu.Item>
			</DropdownMenu.Group>
			<DropdownMenu.Separator />
			<DropdownMenu.Group>
				<DropdownMenu.GroupHeading>Other Actions</DropdownMenu.GroupHeading>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeCrawlProductDialog()}>
						<span>Crawl Product</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeCrawlProductInShopDialog()}>
						<span>Crawl Product in Shop</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeDeleteProductDialog()}>
						<span>Delete Product</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<DropdownMenu.Item onclick={() => goto('/product/' + row.product_id + '/shelf')}>Product OnShelf
				</DropdownMenu.Item>
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