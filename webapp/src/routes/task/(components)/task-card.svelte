<script lang="ts">
  import * as Card from '$lib/components/ui/card/index.js';

  let {data} = $props();
  const STATE_COLOR = new Map<string, string>([
    ['NEW', 'oklch(0.623 0.214 259.815)'],
    ['RUNNING', 'oklch(0.795 0.184 86.047)'],
    ['DONE', 'oklch(0.723 0.219 149.579)'],
    ['ERROR', 'oklch(0.637 0.237 25.331)'],
    ['ARCHIVED', 'oklch(0.551 0.027 264.364)']
  ]);

</script>

<a href={data.link}>
  <Card.Root>
    <Card.Header>
      <Card.Title class="text-nowrap">{data.title}</Card.Title>
    </Card.Header>
    <Card.Content class="grid gap-4 text-l">
      <div>
        {#each Object.entries(data) as [status, count]}
          {#if STATE_COLOR.has(status)}
            <div class="flex items-center justify-between space-x-4">
							<span class="text-xl font-medium leading-none float-left">
								<b>{status}</b>
							</span>
              <span class="text-muted-foreground text-xl float-right" style="color: {STATE_COLOR.get(status)}">
								<b>{count}</b>
							</span>
            </div>
          {/if}
        {/each}
      </div>
    </Card.Content>
  </Card.Root>
</a>