<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto, invalidateAll } from '$app/navigation';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import type { SearchCrawlTask } from '../../../(components)/model';

	let { row, user } = $props();
	let open = $state(false);
	let dialog_title = $state('Are you sure?');
	let dialog_body = $state('');
	let handler = $state(async function(_: SearchCrawlTask) {
	});

	function beforeCreateSearchDialog() {
		dialog_body = 'This action will add a search crawl task. The task will be scheduled later.';
		handler = createSearchCrawlTask;
	}

	function beforeDeleteSearchDialog() {
		dialog_body = 'This action will try to delete a search crawl task. You must fix all external constraints before this operation can be done.';
		handler = deleteSearchCrawlTask;
	}

	async function createSearchCrawlTask(row: SearchCrawlTask) {
		try {
			const response = await fetch('http://localhost:8000/api/v1/search_task', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				},
				body: JSON.stringify({
					'search_key': row.search_key,
					'num_of_pages': row.num_of_pages,
					'target_product_ids': row.target_product_ids,
					'update_id': user.name
				})
			});
			const result = await response.json();
			if (result.code == 0) {
				open = false;
				await invalidateAll();
				return;
			}
		} catch (error) {
			console.error(`Error in function: ${error}`);
		}
	}

	async function deleteSearchCrawlTask(row: SearchCrawlTask) {
		try {
			const response = await fetch(`http://localhost:8000/api/v1/search_task/${row.id}?update_id=${user.name}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				}
			});
			const result = await response.json();
			if (result.code == 0) {
				open = false;
				await invalidateAll();
				return;
			}
		} catch (error) {
			console.error(`Error in function: ${error}`);
		}
	}
</script>

<Dialog.Root bind:open>
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			{#snippet child({ props })}
				<Button
					{...props}
					variant="ghost"
					size="icon"
					class="relative size-8 p-0"
				>
					<span class="sr-only">Open menu</span>
					<Ellipsis />
				</Button>
			{/snippet}
		</DropdownMenu.Trigger>
		<DropdownMenu.Content>
			<DropdownMenu.Group>
				<DropdownMenu.GroupHeading>Copy IDs</DropdownMenu.GroupHeading>
				<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.id)}>
					Copy ID
				</DropdownMenu.Item>
				<DropdownMenu.Item onclick={() => navigator.clipboard.writeText(row.update_id)}>
					Copy Operator ID
				</DropdownMenu.Item>
			</DropdownMenu.Group>
			<DropdownMenu.Separator />
			<DropdownMenu.Group>
				<DropdownMenu.GroupHeading>Other Actions</DropdownMenu.GroupHeading>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeCreateSearchDialog()}>
						<span>Resubmit Task</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeDeleteSearchDialog()}>
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
			<Button type="reset" onclick={() => open = false}>Cancel</Button>
			<Button type="submit" class="bg-red-500 hover:bg-red-500" onclick={() => handler(row)}>Continue
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>