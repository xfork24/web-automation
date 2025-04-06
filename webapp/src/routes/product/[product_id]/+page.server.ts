import { type ProductSale } from '../../(components)/model';
import { getLocalTimeZone, today } from '@internationalized/date';

export const load = async ({url}) => {
  try {
    const regexp = /^\/product\/(?<product_id>[<_>%\w]+)(?<query_params>\??[%_=&\w]*)(?<tag>[#\w]*)/;
    const matches = url.pathname.match(regexp);
    let product_id = undefined;
    if (matches && matches.groups) {
      product_id = matches.groups.product_id;
    }
    const product_response = await fetch(`http://localhost:8000/api/v1/product/${product_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const product = await product_response.json();
    if (product.hasOwnProperty('data') && product.data.hasOwnProperty('additional_properties') && product.data.additional_properties.hasOwnProperty('llm_analysis')) {
      product.data.keyword = product.data.additional_properties.llm_analysis.keyword;
      product.data.category = product.data.additional_properties.llm_analysis.category;
      product.data.digital = product.data.additional_properties.llm_analysis.digital;
    } else {
      product.data.keyword = '';
      product.data.category = '';
      product.data.digital = false;
    }
    product.data.digital_str = product.data.digital ? 'TRUE' : 'FALSE';

    const end = today(getLocalTimeZone()).add({days: 1});
    const start_ts = end.add({days: -30}).toDate(getLocalTimeZone()).getTime() / 1000;
    const end_ts = end.toDate(getLocalTimeZone()).getTime() / 1000;
    const sale_response = await fetch(`http://localhost:8000/api/v1/product_sales?product_id=${product_id}&create_ts={"gte": ${start_ts}, "lt": ${end_ts}}&limit=1000&sort=create_ts&desc=true}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const sale = await sale_response.json();

    const history_response = await fetch(`http://localhost:8000/api/v1/product/${product_id}/history`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const histories = await history_response.json();

    return {
      product_id: decodeURI(product_id!),
      product_info: product.data,
      product_sales: sale.data.filter((item: ProductSale) => {
        return item.display_sale != -1 && item.estimated_revenue != -1;
      }),
      product_histories: histories.data
    };
  } catch (error) {
    console.error(`Error in load function: ${error}`);
  }
};