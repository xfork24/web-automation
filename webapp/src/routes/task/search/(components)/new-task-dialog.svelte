<script lang="ts">
  import { Button } from "$lib/components/ui/button/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import * as Dialog from '$lib/components/ui/dialog/index.js';
  import { invalidateAll } from "$app/navigation";

  let {user} = $props();

  let open = $state(false);
  let search_key = $state('美剧');
  let num_of_pages = $state(5);

  async function createNewSearchCrawlTask(search_key: string, num_of_pages: number) {
    try {
      const response = await fetch('http://localhost:8000/api/v1/search_task', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'search_key': search_key,
          'num_of_pages': num_of_pages,
          'target_product_ids': [],
          'update_id': user.name
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger class="mr-4">
    <Button class="max-w-xs" variant="destructive">New Search</Button>
  </Dialog.Trigger>
  <Dialog.Content class="sm:max-w-[425px]">
    <Dialog.Header>
      <Dialog.Title>Create New Search</Dialog.Title>
      <Dialog.Description>
        This action will create a new search crawl task with specific key. The task will be scheduled later.
      </Dialog.Description>
    </Dialog.Header>
    <div class="grid gap-4 py-4">
      <div class="grid grid-cols-3 items-center gap-4">
        <Label for="search_key" class="text-right">Search Key</Label>
        <Input id="key" value={search_key} class="col-span-2"/>
      </div>
      <div class="grid grid-cols-3 items-center gap-4">
        <Label for="num_of_pages" class="text-right">Number of Pages</Label>
        <Input id="pages" value={num_of_pages} class="col-span-2"/>
      </div>
    </div>
    <Dialog.Footer>
      <Button onclick={() => open = false} type="reset">Cancel</Button>
      <Button class="bg-red-500 hover:bg-red-500"
              onclick={() => createNewSearchCrawlTask(search_key, num_of_pages)}
              type="submit">Submit
      </Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>