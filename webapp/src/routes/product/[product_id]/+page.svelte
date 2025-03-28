<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import Tally_1 from 'lucide-svelte/icons/tally-1';
	import { RangeCalendar } from '$lib/components/ui/range-calendar';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import { getLocalTimeZone, today } from '@internationalized/date';
	import { timeConverter } from '../(components)/util';
	import type { ProductSale } from '../../(components)/model';

	let { data } = $props();

	const product_id = data.product_id;
	const product = data.product_info;

	let sales = $state(data.product_sales);

	let formatter = $state(new Intl.NumberFormat('zh-CN', {
		style: 'currency',
		currency: 'CNY'
	}));
	if (product != undefined) {
		formatter = new Intl.NumberFormat('zh-CN', {
			style: 'currency',
			currency: product.price_unit
		});
	}

	let end = today(getLocalTimeZone()).add({ days: 1 });
	let start = end.add({ days: -30 });
	let value = $state({
		start,
		end
	});

	function resetCalendar() {
		let end = today(getLocalTimeZone()).add({ days: 1 });
		let start = end.add({ days: -30 });
		value = {
			start,
			end
		};
	}

	async function onQueryProductSales() {
		try {
			const start_ts = value.start.toDate(getLocalTimeZone()).getTime() / 1000;
			const end_ts = value.end.toDate(getLocalTimeZone()).getTime() / 1000;
			const sale_response = await fetch(`http://localhost:8000/api/v1/product_sales?product_id=${product_id}&create_ts={"gte": ${start_ts}, "lt": ${end_ts}}&limit=1000&sort=create_ts&desc=true}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				}
			});
			const sale = await sale_response.json();
			sales = sale.data.filter((item: ProductSale) => {
				return item.display_sale != -1 && item.estimated_revenue != -1;
			});
		} catch (error) {
			console.error(`Error in load function: ${error}`);
		}
	}
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
						<Breadcrumb.Link href="/product">Products</Breadcrumb.Link>
					</Breadcrumb.Item>
					<Breadcrumb.Separator />
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/product/{data.product_id}">Product Details</Breadcrumb.Link>
					</Breadcrumb.Item>
				</Breadcrumb.List>
			</Breadcrumb.Root>
		</div>
	</header>
	<main>
		{#if data.product_info !== undefined }
			<div class="items-center justify-between px-4 text-4xl">Product Detail for Product: {product_id}</div>
			<div class="flex p-4">
				<div class="items-center justify-between w-1/5">
					<img src={product.product_cover} alt="product cover" />
				</div>
				<div class="flex flex-wrap items-center gap-4 w-4/5">
					<div class="grid grid-cols-3 gap-4 p-4">
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Product ID: </Label></div>
							{product.product_id}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>SKU ID: </Label></div>
							{product.sku_id}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Product Title: </Label></div>
							<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline"
								 href={product.product_link}
								 target="_blank">{product.product_title}</a>
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Shop: </Label></div>
							<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline"
								 href={product.shop_link} target="_blank">{product.shop_name}</a>
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Display Price: </Label></div>
							{formatter.format(Number.parseFloat(product.display_price) / 100)}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Product Sale: </Label></div>
							{product.display_sale}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Estimated Revenue: </Label></div>
							{formatter.format(Number.parseFloat(product.estimated_revenue) / 100)}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Create Time: </Label></div>
							{timeConverter(product.create_ts)}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Update Time: </Label></div>
							{timeConverter(product.update_ts)}
						</div>
						<div class="flex flex-nowrap">
							<div class="mr-2"><Label>Operator ID: </Label></div>
							{product.update_id}
						</div>
					</div>
				</div>
			</div>
			<div class="flex p-4">
				<div class="items-center justify-between w-1/4">
					<RangeCalendar bind:value class="rounded-md border" />
					<div class="flex justify-end gap-4 py-4">
						<Button type="reset" class="bg-red-500 hover:bg-red-500" onclick={() => resetCalendar()}>Reset</Button>
						<Button type="submit" onclick={() => onQueryProductSales()}>Apply</Button>
					</div>
				</div>
				<div class="flex flex-wrap gap-4 px-4 w-3/4">
					<Table.Root>
						<Table.Caption>Product sale information for product: {product_id}</Table.Caption>
						<Table.Header>
							<Table.Row>
								<Table.Head class="w-[100px]">Display Price</Table.Head>
								<Table.Head>Display Sale</Table.Head>
								<Table.Head>Estimated Revenue</Table.Head>
								<Table.Head>Create Time</Table.Head>
								<Table.Head class="text-right">Operator ID</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							<Table.Row>
								{#each sales as sale (sale)}
									<Table.Cell
										class="font-medium">{formatter.format(Number.parseFloat(sale.display_price) / 100)}</Table.Cell>
									<Table.Cell>{sale.display_sale}</Table.Cell>
									<Table.Cell>{formatter.format(Number.parseFloat(sale.estimated_revenue) / 100)}</Table.Cell>
									<Table.Cell>{timeConverter(sale.create_ts)}</Table.Cell>
									<Table.Cell class="text-right">{product.update_id}</Table.Cell>
								{/each}
							</Table.Row>
						</Table.Body>
					</Table.Root>
				</div>
			</div>
		{:else}
			<div class="items-center justify-between px-4 text-4xl">Please select a valid product from <a
				class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/product'>All Products</a> page
				first.
			</div>
		{/if}
	</main>
</Sidebar.Inset>