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
    getSortedRowModel, type Row
  } from '@tanstack/table-core';
  import { createRawSnippet } from 'svelte';
  import DataTableCheckbox from '../../../(components)/data-table-checkbox.svelte';
  import DataTableSortButton from '../../../(components)/data-table-sort-button.svelte';
  import DataTableActions from './data-table-actions.svelte';
  import NewTaskDialog from './new-task-dialog.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Toaster } from "$lib/components/ui/sonner/index.js";
  import { toast } from "svelte-sonner";
  import * as Dialog from '$lib/components/ui/dialog/index.js';
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Table from '$lib/components/ui/table';
  import * as Select from '$lib/components/ui/select/index.js';
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";
  import {
    FlexRender,
    createSvelteTable,
    renderComponent,
    renderSnippet
  } from '$lib/components/ui/data-table';
  import {
    assert, parseTaskReason,
    parseUUID4,
    type SearchCrawlTask, statusToString,
    task_status_badge_class,
    timeConverter
  } from '../../../(components)/model';
  import { FunnelX, Copy, Archive, RotateCcw, Trash2 } from "@lucide/svelte/icons";
  import { invalidateAll } from '$app/navigation';

  let {data} = $props();

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: Row<SearchCrawlTask>[]) {
  });

  function beforeCreateSelectSearchDialog() {
    dialog_body = 'This action will resubmit select search crawl task(s). The task(s) will be scheduled later.';
    handler = createSelectSearchCrawlTask;
  }

  function beforeArchiveSelectSearchDialog() {
    dialog_body = 'This action will try to archive select search crawl task(s). Archived tasks will no longer be scheduled.';
    handler = archiveSelectSearchCrawlTask;
  }

  function beforeDeleteSelectSearchDialog() {
    dialog_body = 'This action will try to delete select search crawl task(s). You must fix all external constraints before this operation can be done.';
    handler = deleteSelectSearchCrawlTask;
  }

  async function createSelectSearchCrawlTask(rows: Row<SearchCrawlTask>[]) {
    try {
      for (const row of rows) {
        const response = await fetch('http://localhost:8000/api/v1/search_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'search_key': row.original.search_key,
            'num_of_pages': row.original.num_of_pages,
            'target_product_ids': row.original.target_product_ids,
            'update_id': data.user.name
          })
        });
        const result = await response.json();
        assert(result.code == 0, `create search_crawl_task failed for search ${row.original.search_key}`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function archiveSelectSearchCrawlTask(rows: Row<SearchCrawlTask>[]) {
    try {
      for (const row of rows) {
        const response = await fetch(`http://localhost:8000/api/v1/search_task/${row.original.id}/archive?update_id=${data.user.name}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          }
        });
        const result = await response.json();
        assert(result.code == 0, `archive search_crawl_task failed for search ${row.original.search_key}`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function deleteSelectSearchCrawlTask(rows: Row<SearchCrawlTask>[]) {
    try {
      for (const row of rows) {
        const response = await fetch(`http://localhost:8000/api/v1/search_task/${row.original.id}?update_id=${data.user.name}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          }
        });
        const result = await response.json();
        assert(result.code == 0, `delete search_crawl_task failed for search ${row.original.search_key}`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  let pagination = $state<PaginationState>({pageIndex: 0, pageSize: 10});
  let sorting = $state<SortingState>([]);
  let columnFilters = $state<ColumnFiltersState>([]);
  let rowSelection = $state<RowSelectionState>({});
  let columnVisibility = $state<VisibilityState>({
    'Operator ID': false,
    'Product IDs': false,
    'Operator Role': false,
    'Target Product IDs': false
  });

  export const columns: ColumnDef<SearchCrawlTask>[] = [
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
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const id = getData();
          return {
            render: () => `<span>${parseUUID4(id)}</span>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('ID'));
      }
    },
    {
      id: 'Search Key',
      accessorKey: 'search_key',
      header: 'Search Key',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const search_key = getData();
          return {
            render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href='https://s.taobao.com/search?page=1&q=${search_key}' target="_blank">${search_key}</a>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Search Key'));
      }
    },
    {
      id: 'Number of Pages',
      accessorKey: 'num_of_pages',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Number of Pages',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[number]>((getData) => {
          const num_of_pages = getData();
          return {
            render: () => `<div class="text-center">${num_of_pages}</div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Number of Pages'));
      }
    },
    {
      id: 'Target Product IDs',
      accessorKey: 'target_product_ids',
      header: 'Target Product IDs',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string[]]>((getData) => {
          const target_product_ids = getData();
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
      id: 'Product IDs',
      accessorKey: 'target_product_ids_str',
      header: 'Product IDs',
    },
    {
      id: 'Status',
      accessorKey: 'status_str',
      header: 'Status',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[number]>((getData) => {
          const status = getData();
          const badge_class = task_status_badge_class[row.original.status];
          return {
            render: () => `<div><span class="${badge_class}">${status}</span></div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Status'));
      }
    },
    {
      id: 'Reason',
      accessorKey: 'reason',
      header: 'Reason'
    },
    {
      id: 'Attempts',
      accessorKey: 'try_count',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Attempts',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[number]>((getData) => {
          const try_count = getData();
          return {
            render: () => `<div class="text-center">${try_count}</div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Attempts'));
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
      id: 'Update Time',
      accessorKey: 'update_ts',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Update Time',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[number]>((getData) => {
          const update_ts = getData();
          const tm = timeConverter(update_ts);
          return {
            render: () => `<div><p>${tm[0]}</p><p>${tm[1]}</p></div>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Update Time'));
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
    {value: 'id', label: 'ID'},
    {value: 'search_key', label: 'Search Key'},
    {value: 'target_product_ids_str', label: 'Product IDs'},
    {value: 'status', label: 'Status'},
    {value: 'reason', label: 'Reason'}
  ];

  let value = $state('id');

  const triggerContent = $derived(
    filter_fields.find((f) => f.value === value)?.label ?? 'ID'
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
              <Select.Item value={filter.value} label={filter.label}>{filter.label}</Select.Item>
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

    <Dialog.Root bind:open>
      <Dialog.Trigger class="mr-4">
        <Tooltip.Provider>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Button class="max-w-xs" onclick={ () => beforeCreateSelectSearchDialog()} variant="destructive">
                <Copy/>
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Content>
              <p>Resubmit tasks</p>
            </Tooltip.Content>
          </Tooltip.Root>
        </Tooltip.Provider>
      </Dialog.Trigger>

      <Dialog.Trigger class="mr-4">
        <Tooltip.Provider>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Button class="max-w-xs" onclick={ () => beforeArchiveSelectSearchDialog()} variant="destructive">
                <Archive/>
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Content>
              <p>Archive Tasks</p>
            </Tooltip.Content>
          </Tooltip.Root>
        </Tooltip.Provider>
      </Dialog.Trigger>

      <Dialog.Trigger class="mr-4">
        <Tooltip.Provider>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Button class="max-w-xs" onclick={ () => beforeDeleteSelectSearchDialog()} variant="destructive">
                <Trash2/>
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Content>
              <p>Delete Tasks</p>
            </Tooltip.Content>
          </Tooltip.Root>
        </Tooltip.Provider>
      </Dialog.Trigger>

      <Dialog.Content>
        <Dialog.Header>
          <Dialog.Title>{dialog_title}</Dialog.Title>
          <Dialog.Description>
            {dialog_body}
          </Dialog.Description>
        </Dialog.Header>
        <Dialog.Footer>
          <Button onclick={() => open = false} type="reset">Cancel</Button>
          <Button class="bg-red-500 hover:bg-red-500" onclick={() => handler(table.getSelectedRowModel().rows)}
                  type="submit">Continue
          </Button>
        </Dialog.Footer>
      </Dialog.Content>
    </Dialog.Root>

    <NewTaskDialog user={data.user}></NewTaskDialog>

    <Toaster/>

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