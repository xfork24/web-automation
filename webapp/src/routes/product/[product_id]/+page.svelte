<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import * as Table from '$lib/components/ui/table/index.js';
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";
  import { Tally1 } from "@lucide/svelte/icons";
  import { RangeCalendar } from '$lib/components/ui/range-calendar';
  import { Button } from '$lib/components/ui/button';
  import { Label } from '$lib/components/ui/label/index.js';
  import { getLocalTimeZone, today } from '@internationalized/date';
  import {
    PLATFORM_REDNOTE,
    PLATFORM_TAOBAO,
    type ProductSale,
    timeConverter
  } from '../../(components)/model';
  import DataTable from './(components)/data-table.svelte';
  import HistoryDataTable from './(components)/history-data-table.svelte';
  import { Toaster } from "$lib/components/ui/sonner";
  import { goto, invalidateAll } from "$app/navigation";
  import { toast } from "svelte-sonner";

  let {data} = $props();
  let sales = $state(data.product_sales);

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: string | undefined) {
  });

  function beforeOnshelfProductDialog() {
    dialog_body = 'This action will try to make this product ready for shelf. The task will be scheduled later.';
    handler = onShelfProduct;
  }

  async function onShelfProduct(product_id: string | undefined) {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/shadow_product`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'product_id': product_id,
          'update_id': data.user.name
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Successful");
        await goto(`/shadow`);
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  const product_id = data.product_id;
  const product = data.product_info!;
  const shadow = data.shadow_info!;
  const histories = data.product_histories;

  let formatter = $state(new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }));
  let create_tm = $state(['', '']);
  let update_tm = $state(['', '']);
  if (product != undefined) {
    formatter = new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: product.price_unit
    });
    create_tm = timeConverter(product.create_ts);
    update_tm = timeConverter(product.update_ts);
  }
  let platform_mask = $state(0);
  if (shadow != undefined && shadow.additional_properties.hasOwnProperty('platform_mask')) {
    platform_mask = shadow.additional_properties.platform_mask;
  }

  let end = today(getLocalTimeZone()).add({days: 1});
  let start = end.add({days: -30});
  let value = $state({
    start,
    end
  });

  function resetCalendar() {
    let end = today(getLocalTimeZone()).add({days: 1});
    let start = end.add({days: -30});
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
      <Sidebar.Trigger/>
      <Breadcrumb.Root>
        <Breadcrumb.List>
          <Breadcrumb.Separator>
            <Tally1/>
          </Breadcrumb.Separator>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/">Home</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/product">Products</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/product/{data.product_id}">Product Details</Breadcrumb.Link>
          </Breadcrumb.Item>
        </Breadcrumb.List>
      </Breadcrumb.Root>
    </div>
  </header>
  <main>
    {#if data.product_info !== undefined }
      <div class="items-center justify-between px-4 text-4xl">Product Basic Information</div>
      <div class="flex p-4">
        <div class="items-center justify-between w-1/5">
          <img src={product.product_cover} alt="product cover"/>
        </div>
        <div class="flex flex-wrap items-center gap-4 w-4/5">
          <div class="grid grid-cols-3 auto-cols-auto gap-4 p-4">
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Product ID: </Label></div>
              {product.product_id}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>SKU ID: </Label></div>
              {product.sku_id}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Product Title: </Label></div>
              <a class="font-medium text-blue-600 dark:text-blue-500 hover:underline"
                 href={product.product_link}
                 target="_blank">{product.product_title}</a>
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Shop Name: </Label></div>
              <a class="font-medium text-blue-600 dark:text-blue-500 hover:underline"
                 href={product.shop_link} target="_blank">{product.shop_name}</a>
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Keyword: </Label></div>
              {product.keyword}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Category: </Label></div>
              {product.category}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Digital: </Label></div>
              {product.digital_str}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Display Price: </Label></div>
              {formatter.format(product.display_price / 100)}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Product Sale: </Label></div>
              {product.display_sale}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Estimated Revenue: </Label></div>
              {formatter.format(product.estimated_revenue / 100)}
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Create Time: </Label></div>
              <div>
                <p>{create_tm[0]}</p>
                <p>{create_tm[1]}</p>
              </div>
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-1"><Label>Update Time: </Label></div>
              <div>
                <p>{update_tm[0]}</p>
                <p>{update_tm[1]}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div>
        {#if platform_mask === 0}
          <div class="flex flex-row w-full">
            <div class="items-center justify-between px-4 text-2xl w-3/5">Product has not been put on any platforms.
            </div>
            <div class="flex flex-row items-center px-4 justify-end w-2/5">
              <Dialog.Root bind:open>
                <Dialog.Trigger class="mr-4">
                  <Tooltip.Provider>
                    <Tooltip.Root>
                      <Tooltip.Trigger>
                        <Button class="max-w-xs" onclick={ () => beforeOnshelfProductDialog()} variant="destructive">
                          Ready for Onshelf
                        </Button>
                      </Tooltip.Trigger>
                      <Tooltip.Content>
                        <p>Make this product ready for on shelf</p>
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
                    <Button class="bg-red-500 hover:bg-red-500" onclick={() => handler(product_id)} type="submit">
                      Continue
                    </Button>
                  </Dialog.Footer>
                </Dialog.Content>
              </Dialog.Root>
            </div>
          </div>
        {:else}
          <div class="flex items-center">
            <div class="flex flex-wrap items-center justify-start w-3/5">
              {#if platform_mask & PLATFORM_TAOBAO }
                <div class="px-4 text-2xl">Product has been put on sale in
                  <a href="/shadow" class="italic text-yellow-500">Taobao</a>.
                </div>
              {/if}
              {#if platform_mask & PLATFORM_REDNOTE }
                <div class="px-4 text-2xl">Product has been put on sale in
                  <a href="/shadow" class="italic text-red-500">Rednote</a>.
                </div>
              {/if}
            </div>
            <div class="flex flex-row items-center px-4 justify-end w-2/5">
              <Tooltip.Provider>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Button class="max-w-xs" onclick={ () => goto(`/shadow/${product_id}/shelf`)}
                            variant="destructive">
                      Onshelf Product
                    </Button>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Onshelf this product to external platforms.</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </Tooltip.Provider>
            </div>
          </div>
        {/if}
        <Toaster/>
      </div>
      <div class="items-center justify-between px-4 text-4xl">Product Sale Information</div>
      <div class="flex p-4">
        <div class="items-center justify-between w-1/4">
          <RangeCalendar bind:value class="rounded-md border w-[200]"/>
          <div class="flex justify-end gap-4 py-4">
            <Button type="reset" class="bg-red-500 hover:bg-red-500" onclick={() => resetCalendar()}>Reset
            </Button>
            <Button type="submit" onclick={() => onQueryProductSales()}>Apply</Button>
          </div>
        </div>
        <div class="flex flex-wrap gap-4 px-4 w-3/4">
          <DataTable {sales}/>
        </div>
      </div>
      <div class="items-center justify-between px-4 text-4xl">Product Update History</div>
      <div class="items-center justify-between px-4">
        <HistoryDataTable {histories}/>
      </div>
    {:else}
      <div class="items-center justify-between px-4 text-4xl">Please select a valid product from <a
        class="italic font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/product'>All
        Products</a>
        page
        first.
      </div>
    {/if}
  </main>
</Sidebar.Inset>