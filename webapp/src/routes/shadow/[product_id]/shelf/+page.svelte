<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb';
  import * as Sidebar from '$lib/components/ui/sidebar';
  import Tally_1 from '@lucide/svelte/icons/tally-1';

  let {data} = $props();
  const product_id = data.product_id;
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
            <Breadcrumb.Link href="/static">Home</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/product">Products</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/product/{product_id}/shelf">Product On Shelf</Breadcrumb.Link>
          </Breadcrumb.Item>
        </Breadcrumb.List>
      </Breadcrumb.Root>
    </div>
  </header>
  <main>
    {#if data.product_info !== undefined }
      <div class="items-center justify-between px-4 text-4xl">Product OnShelf for {product_id}</div>
    {:else}
      <div class="items-center justify-between px-4 text-4xl">Please select a valid product from <a
        class="italic font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/product'>All Products</a>
        or <a class="italic font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/shadow'>Shadow
          Products</a> page, and navigate here by clicking "Product OnShelf" menu item.
      </div>
    {/if}
  </main>
</Sidebar.Inset>