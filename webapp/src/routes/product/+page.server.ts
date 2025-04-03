import { type ProductInfo, parseProductInfo } from "../(components)/model";

export const load = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/products?limit=10000&sort=update_ts&desc=true', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const body = await response.json();
    let products: ProductInfo[] = [];
    body.data.forEach((product: ProductInfo) => {
        products.push(parseProductInfo(product));
      }
    )
    return {
      products: products
    };
  } catch (error) {
    console.error(`Error in load function: ${error}`);
  }
};