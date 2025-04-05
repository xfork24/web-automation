import { type ProductInfo } from "../(components)/model";

export const load = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/products?limit=10000&sort=update_ts&desc=true', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const body = await response.json();
    body.data.forEach((product: ProductInfo) => {
      if (product.hasOwnProperty('additional_properties') && product.additional_properties.hasOwnProperty('llm_analysis')) {
        product.keyword = product.additional_properties.llm_analysis.keyword;
        product.category = product.additional_properties.llm_analysis.category;
        product.digital = product.additional_properties.llm_analysis.digital;
      } else {
        product.keyword = '';
        product.category = '';
        product.digital = false;
      }
      product.digital_str = product.digital ? 'TRUE' : 'FALSE';
    })
    return {
      products: body.data,
    };
  } catch (error) {
    console.error(`Error in load function: ${error}`);
  }
};