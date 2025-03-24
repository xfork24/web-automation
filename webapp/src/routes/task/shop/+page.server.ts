import { statusToString } from '../(components)/utils';

type AdditionalProperties = {}
export type ShopCrawlTask = {
	id: number;
	shop_name: string;
	status: string;
	try_count: number;
	target_product_ids: string;
	additional_properties: AdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};

export const load = async () => {
	try {
		const response = await fetch('http://localhost:8000/api/v1/shop_tasks?limit=1000&sort=update_ts&desc=true', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		let body = await response.json();
		body.data.forEach((item: ShopCrawlTask) => {
			item.status = statusToString(item.status);
		});
		return {
			content: body.data
		};
	} catch (error) {
		console.error(`Error in load function: ${error}`);
	}
};