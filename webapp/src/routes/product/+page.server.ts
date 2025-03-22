export type OfferItem = {
	name: string;
	img: string;
}
export type OfferInfo = {
	offer_items: OfferItem[][];
	valid_offers: string[][];
}
export type LLMAnalyzeResult = {
	keyword: string;
	category: string;
	digital: boolean;
}
export type AdditionalProperties = {
	llm_analysis: LLMAnalyzeResult;
}
export type ProductInfo = {
	id: string;
	product_id: string;
	sku_id: string;
	product_cover: string;
	product_title: string;
	product_link: string;
	shop_name: string;
	shop_link: string;
	price_unit: string;
	display_price: number;
	display_sale: number;
	estimated_revenue: number;
	title_images: string[];
	page_images: string[];
	offer_details: OfferInfo;
	additional_properties: AdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
};

export const load = async () => {
	try {
		const response = await fetch('http://localhost:8000/api/v1/products?limit=20&sort=update_ts&desc=true', {
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
		console.error(`Error in load function for /: ${error}`);
	}
};