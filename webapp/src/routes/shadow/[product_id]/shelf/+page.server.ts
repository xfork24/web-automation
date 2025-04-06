export const load = async ({url}) => {
  try {
    const regexp = /^\/shadow\/(?<product_id>[<_>%\w]+)\/shelf(?<query_params>\??[%_=&\w]*)(?<tag>[#\w]*)/;
    const matches = url.pathname.match(regexp);
    let product_id = undefined;
    if (matches && matches.groups) {
      product_id = matches.groups.product_id;
    }
    const product_response = await fetch(`http://localhost:8000/api/v1/shadow_product/${product_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const product = await product_response.json();
    return {
      product_id: decodeURI(product_id!),
      shadow_info: product.data
    };
  } catch (error) {
    console.error(`Error in load function: ${error}`);
  }
};