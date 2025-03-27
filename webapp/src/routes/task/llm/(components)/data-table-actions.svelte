<script lang="ts">
	import { Ellipsis } from 'lucide-svelte/icons';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { goto } from '$app/navigation';
	import type { LLMAnalyzeTask } from '../../../(components)/model';
	import * as Dialog from '$lib/components/ui/dialog/index.js';

	let { row, user } = $props();
	let open = $state(false);
	let dialog_title = $state('Are you sure?');
	let dialog_body = $state('');
	let handler = $state(async function(_: LLMAnalyzeTask) {
	});

	function beforeCreateLLMDialog() {
		dialog_body = 'This action will add an LLM analyze task. The task will be scheduled later.';
		handler = createLLMAnalyzeTask;
	}

	function beforeDeleteLLMDialog() {
		dialog_body = 'This action will try to delete an LLM analyze task. You must fix all external constraints before this operation can be done.';
		handler = deleteLLMAnalyzeTask;
	}


	async function createLLMAnalyzeTask(row: LLMAnalyzeTask) {
		try {
			const response = await fetch('http://localhost:8000/api/v1/llm_task', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				},
				body: JSON.stringify({
					'product_id': row.product_id,
					'product_link': row.product_title,
					'update_id': user.name
				})
			});
			const result = await response.json();
			console.log(result);
			if (result.code == 0) {
				open = false;
				return;
			}
		} catch (error) {
			console.error(`Error in function: ${error}`);
		}
	}

	async function deleteLLMAnalyzeTask(row: LLMAnalyzeTask) {
		try {
			const response = await fetch(`http://localhost:8000/api/v1/llm_task/${row.id}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json;charset=UTF-8'
				}
			});
			const result = await response.json();
			if (result.code == 0) {
				open = false;
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
				<DropdownMenu.GroupHeading>Actions</DropdownMenu.GroupHeading>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeCreateLLMDialog()}>
						<span>Resubmit Task</span>
					</DropdownMenu.Item>
				</Dialog.Trigger>
				<Dialog.Trigger class="w-full">
					<DropdownMenu.Item onclick={() => beforeDeleteLLMDialog()}>
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