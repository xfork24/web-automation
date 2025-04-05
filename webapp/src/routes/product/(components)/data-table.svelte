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
  import DataTableCheckbox from '../../(components)/data-table-checkbox.svelte';
  import DataTableSortButton from '../../(components)/data-table-sort-button.svelte';
  import DataTableActions from './data-table-actions.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Toaster } from "$lib/components/ui/sonner";
  import { toast } from "svelte-sonner";
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Table from '$lib/components/ui/table';
  import * as Select from '$lib/components/ui/select';
  import * as Dialog from '$lib/components/ui/dialog';
  import {
    FlexRender,
    createSvelteTable,
    renderComponent,
    renderSnippet
  } from '$lib/components/ui/data-table';
  import FunnelX from '@lucide/svelte/icons/funnel-x';
  import { parseUUID4, type ProductInfo, timeConverter, assert } from '../../(components)/model';
  import { invalidateAll } from '$app/navigation';

  let {data} = $props();

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: Row<ProductInfo>[]) {
  });

  function beforeCrawlSelectProductDialog() {
    dialog_body = 'This action will add select product crawl task(s). The task(s) will be scheduled later.';
    handler = createSelectDetailCrawlTask;
  }

  function beforeCrawlSelectProductInShopDialog() {
    dialog_body = 'This action will add select shop crawl task(s) for target products. The task(s) will be scheduled later.';
    handler = createSelectShopCrawlTask;
  }

  function beforeDeleteSelectProductDialog() {
    dialog_body = 'This action will try to delete selected product(s). You must fix all external constraints before this operation can be done.';
    handler = deleteSelectProduct;
  }

  async function createSelectDetailCrawlTask(rows: Row<ProductInfo>[]) {
    try {
      for (const row of rows) {
        const response = await fetch('http://localhost:8000/api/v1/detail_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'product_id': row.original.product_id,
            'product_link': row.original.product_link,
            'update_id': data.user.name
          })
        });
        const result = await response.json();
        assert(result.code == 0, `create detail_crawl_task failed for product ${row.original.product_id}`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function createSelectShopCrawlTask(rows: Row<ProductInfo>[]) {
    try {
      for (const row of rows) {
        const response = await fetch('http://localhost:8000/api/v1/shop_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'shop_name': row.original.shop_name,
            'target_product_ids': [row.original.product_id],
            'update_id': data.user.name
          })
        });
        const result = await response.json();
        assert(result.code == 0, `create shop_crawl_task failed for shop ${row.original.shop_name} with target product ids [${row.original.product_id}]`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function deleteSelectProduct(rows: Row<ProductInfo>[]) {
    try {
      for (const row of rows) {
        const response = await fetch(`http://localhost:8000/api/v1/product/${row.original.product_id}?update_id=${data.user.name}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          }
        });
        const result = await response.json();
        assert(result.code == 0, `delete detail_crawl_task failed for product ${row.original.product_id}`);
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
  let columnVisibility = $state<VisibilityState>({'Sale/Year': false, 'Price': false, 'Operator ID': false});

  export const columns: ColumnDef<ProductInfo>[] = [
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
      id: 'Product Cover',
      accessorKey: 'product_cover',
      header: 'Product Cover',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const product_cover = getData();
          return {
            render: () => `<a href="${row.original.product_link}" target="_blank"><img class="h-16 w-16 object-scale-down" src=${product_cover} /></a>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Product Cover'));
      }
    },
    {
      id: 'Product ID',
      accessorKey: 'product_id',
      header: 'Product ID',
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const product_id = getData();
          return {
            render: () => `<div>${product_id}</div>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Product ID'));
      }
    },
    {
      id: 'Product Title',
      accessorKey: 'product_title',
      header: 'Product Title',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const product_title = getData();
          return {
            render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/product/${row.original.product_id}'>${product_title}</a>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Product Title'));
      }
    },
    {
      id: 'Shop Name',
      accessorKey: 'shop_name',
      header: 'Shop Name',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const shop_name = getData();
          return {
            render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/shop/${shop_name}'>${shop_name}</a>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Shop Name'));
      }
    },
    {
      id: 'Price',
      accessorKey: 'display_price',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Price',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
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
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Sale/Year',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        })
    },
    {
      id: 'Revenue/Year',
      accessorKey: 'estimated_revenue',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Revenue/Year',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
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
      id: 'Keyword',
      accessorKey: 'keyword',
      header: 'Keyword',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const keyword = getData();
          return {
            render: () => `<div>${keyword}</div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Keyword'));
      }
    },
    {
      id: 'Category',
      accessorKey: 'category',
      header: 'Category',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const category = getData();
          return {
            render: () => `<div>${category}</div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Category'));
      }
    },
    {
      id: 'Digital',
      accessorKey: 'digital_str',
      header: 'Digital',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[string]>((getData) => {
          const digital_str = getData();
          return {
            render: () => `<div>${digital_str}</div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Digital'));
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
      id: 'actions',
      enableHiding: false,
      cell: ({row}) =>
        renderComponent(DataTableActions, {row: row.original, user: data.user})
    }
  ];

  const table = createSvelteTable({
    get data() {
      return data.products;
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
    {value: 'product_id', label: 'Product ID'},
    {value: 'product_title', label: 'Product Title'},
    {value: 'shop_name', label: 'Shop Name'},
    {value: 'keyword', label: 'Keyword'},
    {value: 'category', label: 'Category'},
    {value: 'digital_str', label: 'Digital'},
    {value: 'update_id', label: 'Operator ID'}
  ];

  let value = $state('product_id');

  const triggerContent = $derived(
    filter_fields.find((f) => f.value === value)?.label ?? 'Product ID'
  );

  function clearAllTableFilters() {
    table.getAllColumns().forEach(column => {
      column.setFilterValue('');
    });
  }
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
              <Select.Item value={filter.value} label={filter.label}>
                {filter.label}
              </Select.Item>
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
    <Button class="max-w-xs mr-4" onclick={ () => clearAllTableFilters()} variant="destructive">
      <FunnelX/>
    </Button>

    <Dialog.Root bind:open>
      <Dialog.Trigger class="mr-4">
        <Button class="max-w-xs" onclick={ () => beforeCrawlSelectProductDialog()} variant="destructive">
          Crawl Products
        </Button>
      </Dialog.Trigger>
      <Dialog.Trigger class="mr-4">
        <Button class="max-w-xs" onclick={ () => beforeCrawlSelectProductInShopDialog()} variant="destructive">
          Crawl Products in Shop
        </Button>
      </Dialog.Trigger>
      <Dialog.Trigger class="mr-4">
        <Button class="max-w-xs" onclick={ () => beforeDeleteSelectProductDialog()} variant="destructive">
          Delete Products
        </Button>
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