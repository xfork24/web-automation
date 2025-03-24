type AdditionalProperties = {}
export type ShopInfo = {
	shop_name: string;
	shop_link: string;
	avg_price: number;
	total_sale: number;
	total_revenue: number;
	additional_properties: AdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};

export const load = async () => {
	try {
		const response = await fetch('http://localhost:8000/api/v1/shops?limit=20&&sort=total_revenue&desc=true', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		const body = await response.json();
		return {
			content: body.data
		};
	} catch (error) {
		console.error(`Error in load function: ${error}`);
	}
};