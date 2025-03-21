<script>
	import { page } from '$app/state';

	let product_id = page.params.product_id;
	console.log(product_id);
</script>
<p>Product detail page with sale information: {product_id}</p>