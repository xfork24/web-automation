<script lang="ts">
	import DataTable from './(components)/data-table.svelte';

	let { data } = $props();
</script>

<div class="items-center justify-between px-4">
	<div class="text-4xl ">All Products</div>
	<div>
		<DataTable {data} />
	</div>
</div>
