<script lang="ts">
  import type { ComponentProps } from 'svelte';
  import { ArrowUpDown } from '@lucide/svelte/icons';
  import { Button } from '$lib/components/ui/button';

  let {title, variant = 'ghost', ...restProps}: ComponentProps<typeof Button> =
    $props();
</script>

<Button {...restProps} {variant}>
  {title}
  <ArrowUpDown class="ml-2"/>
</Button>