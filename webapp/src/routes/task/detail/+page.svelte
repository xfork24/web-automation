<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import Tally_1 from '@lucide/svelte/icons/tally-1';
  import DataTable from './(components)/data-table.svelte';

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
            <Breadcrumb.Link href="/">Home</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/task">Tasks</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/task/detail">Detail Craw Tasks</Breadcrumb.Link>
          </Breadcrumb.Item>
        </Breadcrumb.List>
      </Breadcrumb.Root>
    </div>
  </header>
  <main>
    <div class="items-center justify-between px-4">
      <div class="text-4xl ">Detail Crawl Tasks</div>
      <div>
        <DataTable {data}/>
      </div>
    </div>
  </main>
</Sidebar.Inset>