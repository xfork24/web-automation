<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import Tally_1 from 'lucide-svelte/icons/tally-1';

	import { page } from '$app/state';

	let product_id = page.params.product_id;
</script>

<Sidebar.Inset>
	<header class="flex h-16 shrink-0 items-center gap-2">
		<div class="flex items-center gap-2 px-4">
			<Sidebar.Trigger />
			<Breadcrumb.Root>
				<Breadcrumb.List>
					<Breadcrumb.Separator>
						<Tally_1 />
					</Breadcrumb.Separator>
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/">Home</Breadcrumb.Link>
					</Breadcrumb.Item>
					<Breadcrumb.Separator />
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/product">Products</Breadcrumb.Link>
					</Breadcrumb.Item>
					<Breadcrumb.Separator />
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/product/{product_id}/shelf">Product On Shelf</Breadcrumb.Link>
					</Breadcrumb.Item>
				</Breadcrumb.List>
			</Breadcrumb.Root>
		</div>
	</header>
	<main>
		<p>Product on shelf with sale information: {product_id}</p>
	</main>
</Sidebar.Inset>