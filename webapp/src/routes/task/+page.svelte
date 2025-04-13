<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import { Tally1 } from "@lucide/svelte/icons";
  import TaskCard from './(components)/task-card.svelte';
  import { type TaskStatus, type TaskStatusResult } from '../(components)/model';
  import { getLocalTimeZone, today } from '@internationalized/date';
  import { RangeCalendar } from '$lib/components/ui/range-calendar/index.js';
  import { Button } from '$lib/components/ui/button/index.js';

  let {data} = $props();
  let tasks: TaskStatus[] = $state(data.content!);

  let end = today(getLocalTimeZone()).add({days: 1});
  let start = end.add({days: -7});
  let value = $state({
    start,
    end
  });

  function resetCalendar() {
    let end = today(getLocalTimeZone()).add({days: 1});
    let start = end.add({days: -7});
    value = {
      start,
      end
    };
  }

  async function onQueryTaskStatus() {
    try {
      const start_ts = value.start.toDate(getLocalTimeZone()).getTime() / 1000;
      const end_ts = value.end.toDate(getLocalTimeZone()).getTime() / 1000;
      const response = await fetch(`http://localhost:8000/api/v1/tasks?update_ts={"gte": ${start_ts}, "lt": ${end_ts}}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
      });
      const body = await response.json();
      let data: TaskStatusResult = body.data;
      let results: TaskStatus[] = [];
      for (let [key, value] of Object.entries(data)) {
        if (key === 'detail_crawl_task') {
          value.key = 'detail_crawl_task';
          value.title = 'Detail Crawl Tasks';
          value.link = '/task/detail';
        } else if (key === 'search_crawl_task') {
          value.key = 'search_crawl_task';
          value.title = 'Search Crawl Tasks';
          value.link = '/task/search';
        } else if (key === 'shop_crawl_task') {
          value.key = 'shop_crawl_task';
          value.title = 'Shop Crawl Tasks';
          value.link = '/task/shop';
        } else if (key === 'shop_search_crawl_task') {
          value.key = 'shop_search_crawl_task';
          value.title = 'Shop Search Crawl Tasks';
          value.link = '/task/shop_search';
        } else if (key === 'llm_analyze_task') {
          value.key = 'llm_analyze_task';
          value.title = 'LLM Analyze Tasks';
          value.link = '/task/llm';
        } else if (key === 'product_manage_task') {
          value.key = 'product_manage_task';
          value.title = 'Product Manage Tasks';
          value.link = '/task/product';
        }
        results.push(value);
      }
      tasks = results;
    } catch (error) {
      console.error(`Error in load function: ${error}`);
    }
  };
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
            <Breadcrumb.Link href="/task">Tasks</Breadcrumb.Link>
          </Breadcrumb.Item>
        </Breadcrumb.List>
      </Breadcrumb.Root>
    </div>
  </header>
  <main>
    <div class="items-center justify-between px-4">
      <div class="text-4xl">All Tasks Overview</div>
      <div class="flex py-4">
        <div class="items-center justify-between w-1/4">
          <RangeCalendar bind:value class="rounded-md border"/>
          <div class="flex justify-end gap-4 py-4">
            <Button class="bg-red-500 hover:bg-red-500" onclick={() => resetCalendar()} type="reset">Reset
            </Button>
            <Button onclick={() => onQueryTaskStatus()} type="submit">Apply</Button>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-4 px-4 w-3/4">
          {#each tasks as data (data.key)}
            <TaskCard {data}/>
          {/each}
        </div>
      </div>
    </div>
  </main>
</Sidebar.Inset>