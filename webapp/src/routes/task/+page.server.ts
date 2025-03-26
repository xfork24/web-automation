export type TaskStatus = {
	key: string;
	title: string;
	link: string;
	NEW: number;
	IN_PROGRESS: number;
	DONE: number;
	ERROR: number;
	ARCHIVED: number;
}
type TaskStatusResult = {
	detail_crawl_task: TaskStatus;
	search_crawl_task: TaskStatus;
	shop_crawl_task: TaskStatus;
	shop_search_crawl_task: TaskStatus;
	llm_analyze_task: TaskStatus;
}

export const load = async () => {
	try {
		const response = await fetch('http://localhost:8000/api/v1/tasks', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8'
			}
		});
		const body = await response.json();
		let data: TaskStatusResult = body.data;
		let results: TaskStatus[] = [];
		for (let [key, value] of Object.entries(data)) {
			if (key === 'detail_crawl_task') {
				value.key = 'detail_crawl_task';
				value.title = 'Detail Crawl Tasks';
				value.link = '/task/detail';
			} else if (key === 'search_crawl_task') {
				value.key = 'search_crawl_task';
				value.title = 'Search Crawl Tasks';
				value.link = '/task/search';
			} else if (key === 'shop_crawl_task') {
				value.key = 'shop_crawl_task';
				value.title = 'Shop Crawl Tasks';
				value.link = '/task/shop';
			} else if (key === 'shop_search_crawl_task') {
				value.key = 'shop_search_crawl_task';
				value.title = 'Shop Search Crawl Tasks';
				value.link = '/task/shop_search';
			} else if (key === 'llm_analyze_task') {
				value.key = 'llm_analyze_task';
				value.title = 'LLM Analyze Tasks';
				value.link = '/task/llm';
			}
			results.push(value);
		}
		return {
			content: results
		};
	} catch (error) {
		console.error(`Error in load function: ${error}`);
	}
};