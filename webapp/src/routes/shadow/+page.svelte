<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb';
  import * as Sidebar from '$lib/components/ui/sidebar';
  import DataTable from './(components)/data-table.svelte';
  import Tally_1 from '@lucide/svelte/icons/tally-1';

  let {data} = $props();
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
            <Breadcrumb.Link href="/shadow">Shadow Products</Breadcrumb.Link>
          </Breadcrumb.Item>
        </Breadcrumb.List>
      </Breadcrumb.Root>
    </div>
  </header>
  <main>
    <div class="items-center justify-between px-4">
      <div class="text-4xl ">Shadow Products</div>
      <div>
        <DataTable {data}/>
      </div>
    </div>
  </main>
</Sidebar.Inset>