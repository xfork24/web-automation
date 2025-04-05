import type { TaskStatus, TaskStatusResult } from '../(components)/model';
import { getLocalTimeZone, today } from '@internationalized/date';


export const load = async () => {
  try {
    const end = today(getLocalTimeZone()).add({days: 1});
    const start_ts = end.add({days: -7}).toDate(getLocalTimeZone()).getTime() / 1000;
    const end_ts = end.toDate(getLocalTimeZone()).getTime() / 1000;
    const response = await fetch(`http://localhost:8000/api/v1/tasks?update_ts={"gte": ${start_ts}, "lt": ${end_ts}}`, {
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
      } else if (key === 'product_manage_task') {
        value.key = 'product_manage_task';
        value.title = 'Product Manage Tasks';
        value.link = '/task/product';
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