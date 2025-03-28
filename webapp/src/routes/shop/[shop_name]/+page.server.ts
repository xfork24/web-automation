export const load = async ({ url }) => {
	try {
		const regexp = /^\/shop\/(?<shop_name>[<_>%\w]+)(?<query_params>\??[%_=&\w]*)(?<tag>[#\w]*)/;
		const matches = url.pathname.match(regexp);
		let shop_name = undefined;
		if (matches && matches.groups) {
			shop_name = matches.groups.shop_name;
		}
		const shop_response = await fetch(`http://localhost:8000/api/v1/shop/${shop_name}`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		const shop = await shop_response.json();

		const products_response = await fetch(`http://localhost:8000/api/v1/products?shop_name=${shop_name}&limit=1000&sort=update_ts&desc=true`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		const products = await products_response.json();

		return {
			shop_info: shop.data,
			shop_products: products.data,
			shop_name: decodeURI(shop_name!)
		};
	} catch (error) {
		console.error(`Error in load function: ${error}`);
	}
};