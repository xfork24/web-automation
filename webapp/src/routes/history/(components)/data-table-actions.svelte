<script lang="ts">
  import { Ellipsis } from '@lucide/svelte/icons';
  import { Button } from '$lib/components/ui/button';
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';

  let {row, user} = $props();

</script>

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
      <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.pk)}>
        Copy Primary Key
      </DropdownMenu.Item>
      <DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.update_id)}>
        Copy Operator ID
      </DropdownMenu.Item>
    </DropdownMenu.Group>
  </DropdownMenu.Content>
</DropdownMenu.Root>