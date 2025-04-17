<script lang="ts">
  import { Ellipsis } from '@lucide/svelte/icons';
  import { Button } from '$lib/components/ui/button';
  import { goto, invalidateAll } from '$app/navigation';
  import {
    SHADOW_OPERATION_OFFLINE,
    SHADOW_OPERATION_ONLINE,
    SHADOW_STATUS_NEW,
    SHADOW_STATUS_OFFLINE,
    SHADOW_STATUS_ONLINE,
    SHADOW_STATUS_READY,
    type ShadowProductInfo
  } from '../../(components)/model';
  import { Toaster } from "$lib/components/ui/sonner";
  import { toast } from "svelte-sonner";
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Dialog from '$lib/components/ui/dialog';

  let {row, user} = $props();

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: ShadowProductInfo) {
  });

  function beforeOnlineProductDialog() {
    dialog_body = 'This action will online this product. The task will be scheduled later.';
    handler = createOnlineTask;
  }

  function beforeOfflineProductDialog() {
    dialog_body = 'This action will offline this product. The task will be scheduled later.';
    handler = createOfflineTask;
  }

  function beforeDeleteProductDialog() {
    dialog_body = 'This action will delete this product.';
    handler = deleteShadowProduct;
  }

  async function createOnlineTask(row: ShadowProductInfo) {
    try {
      if (row.status !== SHADOW_STATUS_OFFLINE) {
        open = false;
        await invalidateAll();
        toast("Operation Failed: Product must be in OFFLINE status.");
        return;
      }
      const response = await fetch('http://localhost:8000/api/v1/product_task', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'product_id': row.shadow_id,
          'shop_name': '归去来宝藏店',
          'operation': SHADOW_OPERATION_ONLINE,
          'update_id': user.name
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Successful");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function createOfflineTask(row: ShadowProductInfo) {
    try {
      if (row.status !== SHADOW_STATUS_ONLINE) {
        open = false;
        await invalidateAll();
        toast("Operation Failed: Product must be in ONLINE status.");
        return;
      }
      const response = await fetch('http://localhost:8000/api/v1/product_task', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'product_id': row.shadow_id,
          'shop_name': '归去来宝藏店',
          'operation': SHADOW_OPERATION_OFFLINE,
          'update_id': user.name
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Successful");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function deleteShadowProduct(row: ShadowProductInfo) {
    try {
      if (row.status !== SHADOW_STATUS_NEW && row.status !== SHADOW_STATUS_READY) {
        open = false;
        await invalidateAll();
        toast("Operation Failed: Product must be in NEW or READY status.");
        return;
      }
      const response = await fetch(`http://localhost:8000/api/v1/shadow_product/${row.product_id}?update_id=${user.name}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Successful");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function onshelfShadowProduct(row: ShadowProductInfo) {
    open = false;
    if (row.status == SHADOW_STATUS_NEW) {
      await invalidateAll();
      toast("Operation Failed: Product must be READY first.");
      return;
    } else {
      toast("Operation Successful");
      await goto(`/shadow/${row.product_id}/shelf`);
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
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.product_id)}>
          Copy Product ID
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.shadow_id)}>
          Copy Shadow ID
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.rednote_id)}>
          Copy Rednote ID
        </DropdownMenu.Item>
      </DropdownMenu.Group>
      <DropdownMenu.Separator/>
      <DropdownMenu.Group>
        <DropdownMenu.GroupHeading>Navigate to</DropdownMenu.GroupHeading>
        <DropdownMenu.Item onclick={() => window.open(row.product_link, '_blank')}>
          Taobao Product Page
        </DropdownMenu.Item>
      </DropdownMenu.Group>
      <DropdownMenu.Separator/>
      <DropdownMenu.Group>
        <DropdownMenu.GroupHeading>Other Actions</DropdownMenu.GroupHeading>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeOnlineProductDialog()}>
            <span>Online Product</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeOfflineProductDialog()}>
            <span>Offline Product</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeDeleteProductDialog()}>
            <span>Delete Product</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <DropdownMenu.Item onclick={() => onshelfShadowProduct(row)}>
          <span>Onshelf Product</span>
        </DropdownMenu.Item>
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