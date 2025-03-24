<script lang="ts">
	import { ChevronDown, Link } from 'lucide-svelte/icons';
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
	import DataTableCheckbox from '../../../(components)/data-table-checkbox.svelte';
	import DataTableSortButton from '../../../(components)/data-table-sort-button.svelte';
	import DataTableActions from './data-table-actions.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import * as Table from '$lib/components/ui/table';
	import {
		FlexRender,
		createSvelteTable,
		renderComponent,
		renderSnippet
	} from '$lib/components/ui/data-table';
	import * as Select from '$lib/components/ui/select/index.js';
	import { type ShopCrawlTask } from '../+page.server';

	let { data } = $props();

	let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 10 });
	let sorting = $state<SortingState>([]);
	let columnFilters = $state<ColumnFiltersState>([]);
	let rowSelection = $state<RowSelectionState>({});
	let columnVisibility = $state<VisibilityState>({});

	function timeConverter(ts: number) {
		let a = new Date(ts * 1000);
		return `${a.getFullYear()}/${String(a.getMonth()).padStart(2, '0')}/${String(a.getDate()).padStart(2, '0')} ${String(a.getHours()).padStart(2, '0')}:${String(a.getMinutes()).padStart(2, '0')}:${String(a.getSeconds()).padStart(2, '0')}`;
	}

	export const columns: ColumnDef<ShopCrawlTask>[] = [
		{
			id: 'select',
			header: ({ table }) =>
				renderComponent(DataTableCheckbox, {
					checked: table.getIsAllPageRowsSelected(),
					indeterminate:
						table.getIsSomePageRowsSelected() &&
						!table.getIsAllPageRowsSelected(),
					onCheckedChange: (value) => table.toggleAllPageRowsSelected(!!value),
					'aria-label': 'Select all'
				}),
			cell: ({ row }) =>
				renderComponent(DataTableCheckbox, {
					checked: row.getIsSelected(),
					onCheckedChange: (value) => row.toggleSelected(!!value),
					'aria-label': 'Select row'
				}),
			enableSorting: false,
			enableHiding: false
		},
		{
			id: 'ID',
			accessorKey: 'id',
			header: 'ID',
			cell: ({ row }) => {
				const statusSnippet = createRawSnippet<[number]>((getData) => {
					const id = getData();
					return {
						render: () => `<span>${id}</span>`
					};
				});
				return renderSnippet(statusSnippet, row.getValue('ID'));
			}
		},
		{
			id: 'Shop',
			accessorKey: 'shop_name',
			header: 'Shop',
			cell: ({ row }) => {
				const statusSnippet = createRawSnippet<[string]>((getData) => {
					const shop_name = getData();
					return {
						render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/shop/${shop_name}'>${shop_name}</a>`
					};
				});
				return renderSnippet(statusSnippet, row.getValue('Shop'));
			}
		},
		{
			id: 'Target Product IDs',
			accessorKey: 'target_product_ids',
			header: 'Target Product IDs',
			cell: ({ row }) => {
				const statusSnippet = createRawSnippet<[string]>((getData) => {
					const target_product_ids = JSON.parse(getData());
					let snippet = ``;
					target_product_ids.forEach((product_id: string) => snippet += `<a class='font-medium text-blue-600 dark:text-blue-500 hover:underline' href='/product/${product_id}'>${product_id}</a>`);
					return {
						render: () => `<div>${snippet}</div>`
					};
				});
				return renderSnippet(statusSnippet, row.getValue('Target Product IDs'));
			}
		},
		{
			id: 'Status',
			accessorKey: 'status',
			header: 'Status',
			cell: ({ row }) => {
				const statusSnippet = createRawSnippet<[number]>((getData) => {
					const status = getData();
					return {
						render: () => `<div>${status}</div>`
					};
				});
				return renderSnippet(statusSnippet, row.getValue('Status'));
			}
		},
		{
			id: 'Attempts',
			accessorKey: 'try_count',
			header: ({ column }) =>
				renderComponent(DataTableSortButton, {
					title: 'Attempts',
					onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
				}),
			cell: ({ row }) => {
				const statusSnippet = createRawSnippet<[number]>((getData) => {
					const try_count = getData();
					return {
						render: () => `<div>${try_count}</div>`
					};
				});
				return renderSnippet(statusSnippet, row.getValue('Attempts'));
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
					return {
						render: () => `<div>${timeConverter(create_ts)}</div>`
					};
				});
				return renderSnippet(amountCellSnippet, row.getValue('Create Time'));
			}
		},
		{
			id: 'Update Time',
			accessorKey: 'update_ts',
			header: ({ column }) =>
				renderComponent(DataTableSortButton, {
					title: 'Update Time',
					onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
				}),
			cell: ({ row }) => {
				const amountCellSnippet = createRawSnippet<[number]>((getData) => {
					const create_ts = getData();
					return {
						render: () => `<div>${timeConverter(create_ts)}</div>`
					};
				});
				return renderSnippet(amountCellSnippet, row.getValue('Update Time'));
			}
		},
		{
			id: 'Operator ID',
			accessorKey: 'update_id',
			header: 'Operator ID'
		},
		{
			id: 'actions',
			enableHiding: false,
			cell: ({ row }) =>
				renderComponent(DataTableActions, { row: row.original })
		}
	];

	const table = createSvelteTable({
		get data() {
			return data.content;
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

	const filter_fields = [
		{ value: 'id', label: 'ID' },
		{ value: 'shop', label: 'Shop' },
		{ value: 'target_product_ids', label: 'Target Product IDs' },
		{ value: 'status', label: 'Status' },
	];

	let value = $state('id');

	const triggerContent = $derived(
		filter_fields.find((f) => f.value === value)?.label ?? 'ID'
	);
</script>

<div class="w-full">
	<div class="flex items-center py-4">
		<div class="max-w-xs mr-4">
			<Select.Root type="single" name="favoriteFruit" bind:value>
				<Select.Trigger class="w-[180px]">
					{triggerContent}
				</Select.Trigger>
				<Select.Content>
					<Select.Group>
						{#each filter_fields as filter (filter.value)}
							<Select.Item value={filter.value} label={filter.label}
							>{filter.label}</Select.Item
							>
						{/each}
					</Select.Group>
				</Select.Content>
			</Select.Root>
		</div>
		<Input
			placeholder="Filter {triggerContent}..."
			value={(table.getColumn(triggerContent)?.getFilterValue() as string) ?? ""}
			oninput={(e) =>
        table.getColumn(triggerContent)?.setFilterValue(e.currentTarget.value)}
			onchange={(e) => {
        table.getColumn(triggerContent)?.setFilterValue(e.currentTarget.value);
      }}
			class="max-w-xs mr-4"
		/>
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				{#snippet child({ props })}
					<Button {...props} variant="outline" class="ml-auto">
						Visible Columns
						<ChevronDown class="ml-2 size-4" />
					</Button>
				{/snippet}
			</DropdownMenu.Trigger>
			<DropdownMenu.Content align="end">
				{#each table
					.getAllColumns()
					.filter((col) => col.getCanHide()) as column (column)}
					<DropdownMenu.CheckboxItem
						bind:checked={
              () => column.getIsVisible(), (v) => column.toggleVisibility(!!v)
            }
					>
						{column.id}
					</DropdownMenu.CheckboxItem>
				{/each}
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</div>
	<div class="rounded-md border">
		<Table.Root>
			<Table.Header>
				{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
					<Table.Row>
						{#each headerGroup.headers as header (header.id)}
							<Table.Head class="[&:has([role=checkbox])]:pl-3">
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