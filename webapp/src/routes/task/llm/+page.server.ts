export const load = async () => {
	try {
		const response = await fetch('http://localhost:8000/api/v1/llm_tasks?limit=20&sort=update_ts&desc=true', {
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