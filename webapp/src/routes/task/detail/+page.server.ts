import { statusToString } from '../(components)/utils';
import type { DetailCrawlTask } from '../../(components)/model';

export const load = async () => {
	try {
		const response = await fetch('http://localhost:8000/api/v1/detail_tasks?limit=1000&sort=update_ts&desc=true', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		let body = await response.json();
		body.data.forEach((item: DetailCrawlTask) => {
			item.status = statusToString(item.status);
		});
		return {
			content: body.data
		};
	} catch (error) {
		console.error(`Error in load function: ${error}`);
	}
};