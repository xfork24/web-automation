import { type ShadowProductInfo, shadowStatusToString } from "../(components)/model";

export const load = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/shadow_products?limit=10000&sort=update_ts&desc=true', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      }
    });
    const body = await response.json();
    body.data.forEach((shadow: ShadowProductInfo) => {
      if (shadow.additional_properties.hasOwnProperty('llm_analysis')) {
        shadow.keyword = shadow.additional_properties.llm_analysis.keyword;
        shadow.category = shadow.additional_properties.llm_analysis.category;
        shadow.digital = shadow.additional_properties.llm_analysis.digital;
      } else {
        shadow.keyword = '';
        shadow.category = '';
        shadow.digital = false;
      }
      shadow.digital_str = shadow.digital ? 'TRUE' : 'FALSE';
      shadow.status_str = shadowStatusToString(shadow.status);
    })
    return {
      shadow_products: body.data,
    };
  } catch (error) {
    console.error(`Error in load function: ${error}`);
  }
};