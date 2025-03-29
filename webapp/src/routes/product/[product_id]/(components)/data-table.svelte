<script lang="ts">
	import {
		type ColumnDef,
		type ColumnFiltersState,
		type PaginationState,
		type RowSelectionState,
		type SortingState,
		type VisibilityState,
		getCoreRowModel,
		getFilteredRowModel,
		getPaginationRowModel,
		getSortedRowModel
	} from '@tanstack/table-core';
	import { createRawSnippet } from 'svelte';
	import DataTableSortButton from '../../../(components)/data-table-sort-button.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Table from '$lib/components/ui/table';
	import {
		FlexRender,
		createSvelteTable,
		renderComponent,
		renderSnippet
	} from '$lib/components/ui/data-table';
	import { parseUUID4, type ProductSale, timeConverter } from '../../../(components)/model';

	let { sales } = $props();

	let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 10 });
	let sorting = $state<SortingState>([]);
	let columnFilters = $state<ColumnFiltersState>([]);
	let rowSelection = $state<RowSelectionState>({});
	let columnVisibility = $state<VisibilityState>({});

	export const columns: ColumnDef<ProductSale>[] = [
		{
			id: 'Price',
			accessorKey: 'display_price',
			header: ({ column }) =>
				renderComponent(DataTableSortButton, {
					title: 'Price',
					onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
				}),
			cell: ({ row }) => {
				const amountCellSnippet = createRawSnippet<[string]>((getData) => {
					const display_price = getData();
					return {
						render: () => `<div>${display_price}</div>`
					};
				});
				const formatter = new Intl.NumberFormat('zh-CN', {
					style: 'currency',
					currency: row.original.price_unit
				});
				return renderSnippet(
					amountCellSnippet,
					formatter.format(Number.parseFloat(row.getValue('Price')) / 100)
				);
			}
		},
		{
			id: 'Sale/Year',
			accessorKey: 'display_sale',
			header: ({ column }) =>
				renderComponent(DataTableSortButton, {
					title: 'Sale/Year',
					onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
				})
		},
		{
			id: 'Revenue/Year',
			accessorKey: 'estimated_revenue',
			header: ({ column }) =>
				renderComponent(DataTableSortButton, {
					title: 'Revenue/Year',
					onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
				}),
			cell: ({ row }) => {
				const amountCellSnippet = createRawSnippet<[string]>((getData) => {
					const estimated_revenue = getData();
					return {
						render: () => `<div>${estimated_revenue}</div>`
					};
				});
				const formatter = new Intl.NumberFormat('zh-CN', {
					style: 'currency',
					currency: row.original.price_unit
				});

				return renderSnippet(
					amountCellSnippet,
					formatter.format(Number.parseFloat(row.getValue('Revenue/Year')) / 100)
				);
			}
		},
		{
			id: 'Create Time',
			accessorKey: 'create_ts',
			header: ({ column }) =>
				renderComponent(DataTableSortButton, {
					title: 'Create Time',
					onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
				}),
			cell: ({ row }) => {
				const amountCellSnippet = createRawSnippet<[number]>((getData) => {
					const create_ts = getData();
					const tm = timeConverter(create_ts);
					return {
						render: () => `<div><p>${tm[0]}</p><p>${tm[1]}</p></div>`
					};
				});
				return renderSnippet(amountCellSnippet, row.getValue('Create Time'));
			}
		},
		{
			id: 'Operator ID',
			accessorKey: 'update_id',
			header: 'Operator ID',
			cell: ({ row }) => {
				const amountCellSnippet = createRawSnippet<[string]>((getData) => {
					const operator_id = getData();
					return {
						render: () => `<div>${parseUUID4(operator_id)}</div>`
					};
				});
				return renderSnippet(amountCellSnippet, row.getValue('Operator ID'));
			}
		}
	];

	const table = createSvelteTable({
		get data() {
			return sales;
		},
		columns,
		state: {
			get pagination() {
				return pagination;
			},
			get sorting() {
				return sorting;
			},
			get columnVisibility() {
				return columnVisibility;
			},
			get rowSelection() {
				return rowSelection;
			},
			get columnFilters() {
				return columnFilters;
			}
		},
		getCoreRowModel: getCoreRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		onPaginationChange: (updater) => {
			if (typeof updater === 'function') {
				pagination = updater(pagination);
			} else {
				pagination = updater;
			}
		},
		onSortingChange: (updater) => {
			if (typeof updater === 'function') {
				sorting = updater(sorting);
			} else {
				sorting = updater;
			}
		},
		onColumnFiltersChange: (updater) => {
			if (typeof updater === 'function') {
				columnFilters = updater(columnFilters);
			} else {
				columnFilters = updater;
			}
		},
		onColumnVisibilityChange: (updater) => {
			if (typeof updater === 'function') {
				columnVisibility = updater(columnVisibility);
			} else {
				columnVisibility = updater;
			}
		},
		onRowSelectionChange: (updater) => {
			if (typeof updater === 'function') {
				rowSelection = updater(rowSelection);
			} else {
				rowSelection = updater;
			}
		}
	});
</script>

<div class="w-full">
	<div class="rounded-md border">
		<Table.Root>
			<Table.Header>
				{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
					<Table.Row>
						{#each headerGroup.headers as header (header.id)}
							<Table.Head class="text-center px-0.5 [&:has([role=checkbox])]:pl-3">
								{#if !header.isPlaceholder}
									<FlexRender
										content={header.column.columnDef.header}
										context={header.getContext()}
									/>
								{/if}
							</Table.Head>
						{/each}
					</Table.Row>
				{/each}
			</Table.Header>
			<Table.Body>
				{#each table.getRowModel().rows as row (row.id)}
					<Table.Row data-state={row.getIsSelected() && "selected"}>
						{#each row.getVisibleCells() as cell (cell.id)}
							<Table.Cell class="[&:has([role=checkbox])]:pl-3">
								<FlexRender
									content={cell.column.columnDef.cell}
									context={cell.getContext()}
								/>
							</Table.Cell>
						{/each}
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={columns.length} class="h-24 text-center">
							No results.
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
	<div class="flex items-center justify-end space-x-2 pt-4">
		<div class="text-muted-foreground flex-1 text-sm">
			{table.getFilteredSelectedRowModel().rows.length} of
			{table.getFilteredRowModel().rows.length} row(s) selected.
		</div>
		<div class="space-x-2">
			<Button
				variant="outline"
				size="sm"
				onclick={() => table.previousPage()}
				disabled={!table.getCanPreviousPage()}
			>
				Previous
			</Button>
			<Button
				variant="outline"
				size="sm"
				onclick={() => table.nextPage()}
				disabled={!table.getCanNextPage()}
			>
				Next
			</Button>
		</div>
	</div>
</div>