export function timeConverter(ts: number) {
	let a = new Date(ts * 1000);
	return `${a.getFullYear()}/${String(a.getMonth()).padStart(2, '0')}/${String(a.getDate()).padStart(2, '0')} ${String(a.getHours()).padStart(2, '0')}:${String(a.getMinutes()).padStart(2, '0')}:${String(a.getSeconds()).padStart(2, '0')}`;
}