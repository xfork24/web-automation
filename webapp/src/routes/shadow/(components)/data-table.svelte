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
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";
  import { BookmarkCheck, BookmarkX, FunnelX, RotateCcw, Trash2 } from "@lucide/svelte/icons";
  import {
    FlexRender,
    createSvelteTable,
    renderComponent,
    renderSnippet
  } from '$lib/components/ui/data-table';
  import {
    parseUUID4,
    type ShadowProductInfo,
    timeConverter,
    assert,
    PLATFORM_NONE,
    PLATFORM_TAOBAO,
    PLATFORM_REDNOTE,
    SHADOW_STATUS_OFFLINE,
    SHADOW_OPERATION_ONLINE,
    SHADOW_STATUS_ONLINE,
    SHADOW_OPERATION_OFFLINE,
    SHADOW_STATUS_NEW, SHADOW_STATUS_READY, shadowStatusToString
  } from '../../(components)/model';
  import { invalidateAll } from '$app/navigation';

  let {data} = $props();
  let shadows = $state(data.shadow_products);

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: Row<ShadowProductInfo>[]) {
  });

  const shadow_status_badge_class = [
    'inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-yellow-600/20 ring-inset',
    'inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-700/10 ring-inset',
    'inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-green-600/20 ring-inset',
    'inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-red-600/10 ring-inset',
    'inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-gray-500/10 ring-inset',
  ]

  function beforeOnlineSelectProductDialog() {
    dialog_body = 'This action will try to online select product(s). The task(s) will be scheduled later.';
    handler = createSelectOnlineTask;
  }

  function beforeOfflineSelectProductDialog() {
    dialog_body = 'This action will try to offline select product(s). The task(s) will be scheduled later.';
    handler = createSelectOfflineTask;
  }

  function beforeDeleteSelectProductDialog() {
    dialog_body = 'This action will try to delete select product(s)';
    handler = deleteSelectShadowProduct;
  }

  async function createSelectOnlineTask(rows: Row<ShadowProductInfo>[]) {
    try {
      // 必须所有的商品都是Offline=4状态才可以操作上线
      for (const row of rows) {
        if (row.original.status !== SHADOW_STATUS_OFFLINE) {
          open = false;
          await invalidateAll();
          toast("Operation Failed: Product(s) must be in OFFLINE status.");
          return;
        }
      }
      for (const row of rows) {
        const response = await fetch('http://localhost:8000/api/v1/product_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'product_id': row.original.shadow_id,
            'shop_name': '归去来宝藏店',
            'operation': SHADOW_OPERATION_ONLINE,
            'update_id': data.user.name
          })
        });
        const result = await response.json();
        assert(result.code == 0, `create product_manage_task failed for product ${row.original.shadow_id}`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function createSelectOfflineTask(rows: Row<ShadowProductInfo>[]) {
    try {
      // 必须所有的商品都是Online=3状态才可以操作下线
      for (const row of rows) {
        if (row.original.status !== SHADOW_STATUS_ONLINE) {
          open = false;
          await invalidateAll();
          toast("Operation Failed: Product(s) must be in ONLINE status.");
          return;
        }
      }
      for (const row of rows) {
        const response = await fetch('http://localhost:8000/api/v1/product_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'product_id': row.original.shadow_id,
            'shop_name': '归去来宝藏店',
            'operation': SHADOW_OPERATION_OFFLINE,
            'update_id': data.user.name
          })
        });
        const result = await response.json();
        assert(result.code == 0, `create product_manage_task failed for product ${row.original.shadow_id}`);
      }
      open = false;
      table.resetRowSelection(false);
      await invalidateAll();
      toast("Operation Successful");
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function deleteSelectShadowProduct(rows: Row<ShadowProductInfo>[]) {
    try {
      // 必须所有的商品都是New=0或Ready=1状态才可以操作删除
      for (const row of rows) {
        if (row.original.status !== SHADOW_STATUS_NEW && row.original.status !== SHADOW_STATUS_READY) {
          open = false;
          await invalidateAll();
          toast("Operation Failed: Product(s) must be in NEW or READY status.");
          return;
        }
      }
      for (const row of rows) {
        const response = await fetch(`http://localhost:8000/api/v1/shadow_product/${row.original.product_id}?update_id=${data.user.name}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
        });
        const result = await response.json();
        assert(result.code == 0, `delete shadow product failed for product ${row.original.product_id}`);
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
    'Shadow ID': false,
    'Rednote ID': false,
    'Shop Name': false,
    'Inventory': false,
    'Operator ID': false,
    'Operator Role': false
  });

  export const columns: ColumnDef<ShadowProductInfo>[] = [
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
      id: 'Product ID',
      accessorKey: 'product_id',
      header: 'Product ID',
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const product_id = getData();
          return {
            render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/product/${product_id}'>${product_id}</a>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Product ID'));
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
      id: 'Shadow ID',
      accessorKey: 'shadow_id',
      header: 'Shadow ID',
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const shadow_id = getData();
          return {
            render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="https://item.taobao.com/item.htm?id=${shadow_id}" target="_blank">${shadow_id}</a>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Shadow ID'));
      }
    },
    {
      id: 'Rednote ID',
      accessorKey: 'rednote_id',
      header: 'Rednote ID',
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const rednote_id = getData();
          return {
            render: () => `<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="https://www.xiaohongshu.com/goods-detail/${rednote_id}" target="_blank" >${rednote_id}</a>`
          };
        });
        return renderSnippet(amountCellSnippet, row.getValue('Rednote ID'));
      }
    },
    {
      id: 'Status',
      accessorKey: 'status_str',
      header: 'Status',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[number]>((getData) => {
          const status = getData();
          const badge_class = shadow_status_badge_class[row.original.status];
          return {
            render: () => `<div><span class="${badge_class}">${status}</span></div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Status'));
      }
    },
    {
      id: 'Platform',
      accessorKey: 'platform_mask',
      header: 'Platform',
      cell: ({row}) => {
        const statusSnippet = createRawSnippet<[number]>((getData) => {
          const platform = getData();
          let body = `<div>`
          if (platform == PLATFORM_NONE) {
            body += `<p class="italic">None</p>`
          }
          if (platform & PLATFORM_TAOBAO) {
            body += `<p><a href="https://item.taobao.com/item.htm?id=${row.original.shadow_id}" target="_blank" class="italic text-yellow-500">Taobao</a></p>`
          }
          if (platform & PLATFORM_REDNOTE) {
            body += `<p><a href="https://www.xiaohongshu.com/goods-detail/${row.original.rednote_id}" target="_blank" class="italic text-red-500">Rednote</a></p>`
          }
          body += `</div>`
          return {
            render: () => body
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Platform'));
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
            render: () => `<div>${product_title}</div>`
          };
        });
        return renderSnippet(statusSnippet, row.getValue('Product Title'));
      }
    },
    {
      id: 'Price',
      accessorKey: 'price',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Price',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }),
      cell: ({row}) => {
        const amountCellSnippet = createRawSnippet<[string]>((getData) => {
          const price = getData();
          return {
            render: () => `<div>${price}</div>`
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
      id: 'Inventory',
      accessorKey: 'inventory',
      header: ({column}) =>
        renderComponent(DataTableSortButton, {
          title: 'Inventory',
          onclick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        })
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
      return shadows;
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
    {value: 'shop_name', label: 'Shop Name'},
    {value: 'shadow_id', label: 'Shadow ID'},
    {value: 'status_str', label: 'Status'},
    {value: 'product_title', label: 'Product Title'},
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

  export const refreshData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/shadow_products?limit=1000&sort=update_ts&desc=true', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
      });
      const body = await response.json();
      body.data.forEach((shadow: ShadowProductInfo) => {
        if (shadow.additional_properties.hasOwnProperty('llm_analysis')) {
          shadow.keyword = shadow.additional_properties.llm_analysis.keyword;
          shadow.category = shadow.additional_properties.llm_analysis.category;
          shadow.digital = shadow.additional_properties.llm_analysis.digital;
        } else {
          shadow.keyword = '';
          shadow.category = '';
          shadow.digital = false;
        }
        if (shadow.additional_properties.hasOwnProperty('platform_mask')) {
          shadow.platform_mask = shadow.additional_properties.platform_mask;
        } else {
          shadow.platform_mask = 0;
        }
        shadow.digital_str = shadow.digital ? 'TRUE' : 'FALSE';
        shadow.status_str = shadowStatusToString(shadow.status);
      })
      shadows = body.data;
    } catch (error) {
      console.error(`Error in load function: ${error}`);
    }
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
              <Button class="max-w-xs" onclick={ () => beforeOnlineSelectProductDialog()} variant="destructive">
                <BookmarkCheck/>
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Content>
              <p>Make shadow products online</p>
            </Tooltip.Content>
          </Tooltip.Root>
        </Tooltip.Provider>
      </Dialog.Trigger>

      <Dialog.Trigger class="mr-4">
        <Tooltip.Provider>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Button class="max-w-xs" onclick={ () => beforeOfflineSelectProductDialog()} variant="destructive">
                <BookmarkX/>
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Content>
              <p>Make shadow products offline</p>
            </Tooltip.Content>
          </Tooltip.Root>
        </Tooltip.Provider>
      </Dialog.Trigger>

      <Dialog.Trigger class="mr-4">
        <Tooltip.Provider>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Button class="max-w-xs" onclick={ () => beforeDeleteSelectProductDialog()} variant="destructive">
                <Trash2/>
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Content>
              <p>Delete shadow products</p>
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