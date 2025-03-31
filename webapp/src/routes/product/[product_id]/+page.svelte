<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import * as Table from '$lib/components/ui/table/index.js';
  import Tally_1 from '@lucide/svelte/icons/tally-1';
  import { RangeCalendar } from '$lib/components/ui/range-calendar';
  import { Button } from '$lib/components/ui/button';
  import { Label } from '$lib/components/ui/label/index.js';
  import { getLocalTimeZone, today } from '@internationalized/date';
  import { type ProductSale, timeConverter } from '../../(components)/model';
  import DataTable from './(components)/data-table.svelte';

  let {data} = $props();
  let sales = $state(data.product_sales);

  const product_id = data.product_id;
  const product = data.product_info;

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
            <Tally_1/>
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
      <div class="items-center justify-between px-4 text-4xl">Product Detail for Product: {product_id}</div>
      <div class="flex p-4">
        <div class="items-center justify-between w-1/5">
          <img src={product.product_cover} alt="product cover"/>
        </div>
        <div class="flex flex-wrap items-center gap-4 w-4/5">
          <div class="grid grid-cols-2 auto-cols-auto gap-4 p-4">
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
              <div class="mr-2"><Label>Shop Name: </Label></div>
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
              <div>
                <p>{create_tm[0]}</p>
                <p>{create_tm[1]}</p>
              </div>
            </div>
            <div class="flex flex-nowrap">
              <div class="mr-2"><Label>Update Time: </Label></div>
              <div>
                <p>{update_tm[0]}</p>
                <p>{update_tm[1]}</p>
              </div>
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
          <RangeCalendar bind:value class="rounded-md border"/>
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