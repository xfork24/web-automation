<script lang="ts">
  import { ChevronDown } from '@lucide/svelte/icons';
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
  import DataTableCheckbox from '../../(components)/data-table-checkbox.svelte';
  import DataTableSortButton from '../../(components)/data-table-sort-button.svelte';
  import DataTableActions from './data-table-actions.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Select from '$lib/components/ui/select';
  import * as Tooltip from "$lib/components/ui/tooltip";
  import * as Table from '$lib/components/ui/table';
  import {
    FlexRender,
    createSvelteTable,
    renderComponent,
    renderSnippet
  } from '$lib/components/ui/data-table';
  import { FunnelX, RotateCcw } from "@lucide/svelte/icons";
  import type { OperationHistory } from '../../(components)/model';
  import { parseUUID4, timeConverter } from '../../(components)/model';
  import { invalidateAll } from "$app/navigation";
  import { toast } from "svelte-sonner";

  let {data} = $props();

  let pagination = $state<PaginationState>({pageIndex: 0, pageSize: 10});
  let sorting = $state<SortingState>([]);
  let columnFilters = $state<ColumnFiltersState>([]);
  let rowSelection = $state<RowSelectionState>({});
  let columnVisibility = $state<VisibilityState>({'Operator Role': false});

  export const columns: ColumnDef<OperationHistory>[] = [
    {
      id: 'select',
      header: ({table}) =>
        renderComponent(DataTableCheckbox, {
          checked: table.getIsAllPageRowsSelected(),
          indeterminate:
            table.getIsSomePageRowsSelected() &&
            !table.getIsAllPageRowsSelected(),
          onCheckedChange: (value) => table.toggleAllPageRowsSelected(!!value),
          'aria-label': 'Select all'
        }),
      cell: ({row}) =>
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
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[number]>((getData) => {
          const operation_id = getData();
          return {
            render: () => `<span>${operation_id}</span>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('ID'));
      }
    },
    {
      id: 'Primary Key',
      accessorKey: 'pk',
      header: 'Primary Key',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          let pk = getData();
          let link = '';
          if (row.original.table_name == 'product_info') {
            link = `/product/${pk}`;
          } else if (row.original.table_name == 'shop_info') {
            link = `/shop/${pk}`;
          } else if (row.original.table_name == 'product_sale') {
            link = `/product/${pk.split(',')[0]}`;
          } else if (row.original.table_name == 'hot_product') {
            link = `/product/${pk.split(',')[0]}`;
          } else if (row.original.table_name == 'search_crawl_task') {
            link = `/task/search?id=${pk}`;
          } else if (row.original.table_name == 'shop_crawl_task') {
            link = `/task/shop?id=${pk}`;
          } else if (row.original.table_name == 'detail_crawl_task') {
            link = `/task/detail?id=${pk}`;
          } else if (row.original.table_name == 'shop_search_crawl_task') {
            link = `/task/shop_search?id=${pk}`;
          } else if (row.original.table_name == 'llm_analyze_task') {
            link = `/task/llm?id=${pk}`;
          }
          pk = parseUUID4(pk);
          if (pk.search(',') != -1) {
            const parts = pk.split(',');
            return {
              render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href=${link}><p>${parts[0]}</p><p>${parts[1]}</p></a>`
            };
          } else {
            return {
              render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href=${link}>${pk}</a>`
            };
          }
        });
        return renderSnippet(statusSnippet, row.getValue('Primary Key'));
      }
    },
    {
      id: 'Table',
      accessorKey: 'table_name',
      header: 'Table',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const table_name = getData();
          return {
            render: () => `<span>${table_name}</span>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Table'));
      }
    },
    {
      id: 'Operation',
      accessorKey: 'operation',
      header: 'Operation',
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[number]>((getData) => {
          const operation = getData();
          let ops = '';
          if (operation === 1) {
            ops = 'CREATE';
          } else if (operation === 2) {
            ops = 'UPDATE';
          } else if (operation === 3) {
            ops = "DELETE";
          }
          return {
            render: () => `<div>${ops}</div>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Operation'));
      }
    },
    {
      id: 'Operation Time',
      accessorKey: 'operation_ts',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Operation Time',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[number]>((getData) => {
          const operation_ts = getData();
          const tm = timeConverter(operation_ts);
          return {
            render: () => `<div><p>${tm[0]}</p><p>${tm[1]}</p></div>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Operation Time'));
      }
    },
    {
      id: 'Create Time',
      accessorKey: 'create_ts',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Create Time',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
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
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const update_id = getData();
          return {
            render: () => `<div>${parseUUID4(update_id)}</div>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Operator ID'));
      }
    },
    {
      id: 'Operator Role',
      accessorKey: 'update_role',
      header: 'Operator Role',
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const update_role = getData();
          return {
            render: () => `<div>${update_role}</div>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Operator Role'));
      }
    },
    {
      id: 'actions',
      enableHiding: false,
      cell: ({row}) =>
        renderComponent(DataTableActions, {row: row.original, user: data.user})
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
    {value: 'primary_key', label: 'Primary Key'},
    {value: 'table', label: 'Table'},
    {value: 'update_id', label: 'Operator ID'}
  ];

  let value = $state('primary_key');

  const triggerContent = $derived(
    filter_fields.find((f) => f.value === value)?.label ?? 'Primary Key'
  );

  function clearAllTableFilters() {
    table.getAllColumns().forEach(column => {
      column.setFilterValue('');
    });
  }

  export const refreshData = async () => {
    await invalidateAll();
    toast("Operation Successful");
  };
</script>

<div class="w-full">
  <div class="flex items-center py-4">
    <div class="max-w-xs mr-4">
      <Select.Root bind:value name="favoriteFruit" type="single">
        <Select.Trigger class="w-[150px]">
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
      class="max-w-xs mr-4"
      onchange={(e) => {
        table.getColumn(triggerContent)?.setFilterValue(e.currentTarget.value);
      }}
      oninput={(e) =>
        table.getColumn(triggerContent)?.setFilterValue(e.currentTarget.value)}
      placeholder="Filter {triggerContent}..."
      value={(table.getColumn(triggerContent)?.getFilterValue() as string) ?? ""}
    />
    <Tooltip.Provider>
      <Tooltip.Root>
        <Tooltip.Trigger>
          <Button class="max-w-xs mr-4" onclick={ () => clearAllTableFilters()} variant="destructive">
            <FunnelX/>
          </Button>
        </Tooltip.Trigger>
        <Tooltip.Content>
          <p>Clear all filters</p>
        </Tooltip.Content>
      </Tooltip.Root>
    </Tooltip.Provider>

    <Tooltip.Provider>
      <Tooltip.Root>
        <Tooltip.Trigger>
          <Button class="max-w-xs mr-4" onclick={ () => refreshData()} variant="destructive">
            <RotateCcw/>
          </Button>
        </Tooltip.Trigger>
        <Tooltip.Content>
          <p>Refresh data</p>
        </Tooltip.Content>
      </Tooltip.Root>
    </Tooltip.Provider>
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({props})}
          <Button {...props} variant="outline" class="ml-auto">
            Visible Columns
            <ChevronDown class="ml-2 size-4"/>
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
              <Table.Cell class="text-center px-0.5 [&:has([role=checkbox])]:pl-3">
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
        disabled={!table.getCanPreviousPage()}
        onclick={() => table.previousPage()}
        size="sm"
        variant="outline"
      >
        Previous
      </Button>
      <Button
        disabled={!table.getCanNextPage()}
        onclick={() => table.nextPage()}
        size="sm"
        variant="outline"
      >
        Next
      </Button>
    </div>
  </div>
</div>