<script lang="ts">
  import { Ellipsis } from '@lucide/svelte/icons';
  import { Button } from '$lib/components/ui/button';
  import { invalidateAll } from '$app/navigation';
  import type { ProductManageTask } from '../../../(components)/model';
  import { Toaster } from "$lib/components/ui/sonner/index.js";
  import { toast } from "svelte-sonner";
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Dialog from '$lib/components/ui/dialog/index.js';

  let {row, user} = $props();

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function (_: ProductManageTask) {
  });

  function beforeProductManageDialog() {
    dialog_body = 'This action will add a product manage task. The task will be scheduled later.';
    handler = createProductManageTask;
  }

  function beforeArchiveProductDialog() {
    dialog_body = 'This action will archive a product manage task. Archived tasks will no longer be scheduled.';
    handler = archiveProductManageTask;
  }

  function beforeDeleteProductManageDialog() {
    dialog_body = 'This action will try to delete a product manage task. You must fix all external constraints before this operation can be done.';
    handler = deleteProductManageTask;
  }

  async function createProductManageTask(row: ProductManageTask) {
    try {
      const response = await fetch('http://localhost:8000/api/v1/product_task', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'product_id': row.product_id,
          'shop_name': row.shop_name,
          'platform': row.platform,
          'operation': row.operation,
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

  async function archiveProductManageTask(row: ProductManageTask) {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/product_task/${row.id}/archive?update_id=${user.name}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
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

  async function deleteProductManageTask(row: ProductManageTask) {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/product_task/${row.id}?update_id=${user.name}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
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
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.id)}>
          Copy ID
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.product_id)}>
          Copy Product ID
        </DropdownMenu.Item>
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
        <DropdownMenu.Item onclick={() => window.open(row.product_link, '_blank')}>
          Taobao Product Page
        </DropdownMenu.Item>
      </DropdownMenu.Group>
      <DropdownMenu.Separator/>
      <DropdownMenu.Group>
        <DropdownMenu.GroupHeading>Other Actions</DropdownMenu.GroupHeading>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeProductManageDialog()}>
            <span>Resubmit Task</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeArchiveProductDialog()}>
            <span>Archive Task</span>
          </DropdownMenu.Item>
        </Dialog.Trigger>
        <Dialog.Trigger class="w-full">
          <DropdownMenu.Item onclick={() => beforeDeleteProductManageDialog()}>
            <span>Delete Task</span>
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