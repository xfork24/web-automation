import { statusToString } from '../(components)/utils';

type AdditionalProperties = {}
export type SearchCrawlTask = {
	id: number;
	search_key: string;
	num_of_pages: string;
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
		const response = await fetch('http://localhost:8000/api/v1/search_tasks?limit=1000&sort=update_ts&desc=true', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		let body = await response.json();
		body.data.forEach((item: SearchCrawlTask) => {
			item.status = statusToString(item.status);
		});
		return {
			content: body.data
		};
	} catch (error) {
		console.error(`Error in load function: ${error}`);
	}
};