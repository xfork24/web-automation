<script lang="ts">
  import { Ellipsis } from '@lucide/svelte/icons';
  import { Button } from '$lib/components/ui/button';
  import { goto, invalidateAll } from '$app/navigation';
  import type { ShopInfo } from '../../(components)/model';
  import { Toaster } from "$lib/components/ui/sonner/index.js";
  import { toast } from "svelte-sonner";
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Dialog from '$lib/components/ui/dialog/index.js';

  let {row, user} = $props();

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: ShopInfo) {
  });

  function beforeCrawlShopDialog() {
    dialog_body = 'This action will add a shop crawl task. The task will be scheduled later.';
    handler = createShopCrawlTask;
  }

  function beforeCrawlShopInSearchDialog() {
    dialog_body = 'This action will add a shop search crawl task. The task will be scheduled later.';
    handler = createShopSearchCrawlTask;
  }

  function beforeDeleteShopDialog() {
    dialog_body = 'This action will try to delete a shop. You must fix all external constraints before this operation can be done.';
    handler = deleteShop;
  }

  async function createShopCrawlTask(row: ShopInfo) {
    try {
      const response = await fetch('http://localhost:8000/api/v1/shop_task', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'shop_name': row.shop_name,
          'target_product_ids': [],
          'update_id': user.name
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Success");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function createShopSearchCrawlTask(row: ShopInfo) {
    try {
      const response = await fetch('http://localhost:8000/api/v1/shop_search_task', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'shop_name': row.shop_name,
          'update_id': user.name
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Success");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function deleteShop(row: ShopInfo) {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/shop/${row.shop_name}?update_id=${user.name}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Success");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

</script>

<Toaster/>

<Dialog.Root bind:open>
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      {#snippet child({props})}
        <Button
          {...props}
          variant="ghost"
          size="icon"
          class="relative size-8 p-0"
        >
          <span class="sr-only">Open menu</span>
          <Ellipsis/>
        </Button>
      {/snippet}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content>
      <DropdownMenu.Group>
        <DropdownMenu.GroupHeading>Copy IDs</DropdownMenu.GroupHeading>
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.shop_name)}>
          Copy Shop Name
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.update_id)}>
          Copy Operator ID
        </DropdownMenu.Item>
      </DropdownMenu.Group>
      <DropdownMenu.Separator/>
      <DropdownMenu.Group>
        <DropdownMenu.GroupHeading>Navigate to</DropdownMenu.GroupHeading>
        <DropdownMenu.Item onclick={() => goto('/shop/' + row.shop_name)}>
          Shop Detail Page
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => window.open(row.shop_link, '_blank')}>
          Taobao Shop Page
        </DropdownMenu.Item>
      </DropdownMenu.Group>
      <DropdownMenu.Separator/>
      <DropdownMenu.Group>
        <DropdownMenu.GroupHeading>Other Actions</DropdownMenu.GroupHeading>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeCrawlShopDialog()}>
            <span>Crawl Shop</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeCrawlShopInSearchDialog()}>
            <span>Crawl Shop in Search</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeDeleteShopDialog()}>
            <span>Delete Shop</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
      </DropdownMenu.Group>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
  <Dialog.Content>
    <Dialog.Header>
      <Dialog.Title>{dialog_title}</Dialog.Title>
      <Dialog.Description>
        {dialog_body}
      </Dialog.Description>
    </Dialog.Header>
    <Dialog.Footer>
      <Button onclick={() => open = false} type="reset">Cancel</Button>
      <Button class="bg-red-500 hover:bg-red-500" onclick={() => handler(row)} type="submit">Continue
      </Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>