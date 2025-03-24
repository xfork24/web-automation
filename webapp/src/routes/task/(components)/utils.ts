export function statusToString(status: string) {
	let task_status = '';
	if (status == '1') {
		task_status = 'NEW';
	} else if (status == '2') {
		task_status = 'IN PROGRESS';
	} else if (status == '3') {
		task_status = 'DONE';
	} else if (status == '4') {
		task_status = 'ERROR';
	} else if (status == '5') {
		task_status = 'ARCHIVED';
	}
	return task_status;
}