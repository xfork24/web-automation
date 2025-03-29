<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import Tally_1 from 'lucide-svelte/icons/tally-1';
	import DataTable from './(components)/data-table.svelte';

	let { data } = $props();

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
						<Breadcrumb.Link href="/shop">Shops</Breadcrumb.Link>
					</Breadcrumb.Item>
					<Breadcrumb.Separator />
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/shop/{data.shop_name}">Shop Details</Breadcrumb.Link>
					</Breadcrumb.Item>
				</Breadcrumb.List>
			</Breadcrumb.Root>
		</div>
	</header>
	<main>
		{#if data.shop_info !== undefined }
			<div class="items-center justify-between px-4 text-4xl">Included Products for Shop: {data.shop_name}</div>
			<div>
				<DataTable {data} />
			</div>
		{:else}
			<div class="items-center justify-between px-4 text-4xl">Please select a valid shop from <a
				class="italic font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/shop'>All Shops</a> page
				first.
			</div>
		{/if}
	</main>
</Sidebar.Inset>