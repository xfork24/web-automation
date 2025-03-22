<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto } from '$app/navigation';

	let { row } = $props();
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
			<DropdownMenu.GroupHeading>Copy ID</DropdownMenu.GroupHeading>
			<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.product_id)}>
				Copy Product ID
			</DropdownMenu.Item>
			<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.sku_id)}>
				Copy SKU ID
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
			<DropdownMenu.GroupHeading>Actions</DropdownMenu.GroupHeading>
			<DropdownMenu.Item>Crawl Product</DropdownMenu.Item>
			<DropdownMenu.Item onclick={() => goto('/product/' + row.product_id + '/shelf')}>Product OnShelf</DropdownMenu.Item>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>