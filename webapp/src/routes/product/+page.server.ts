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
const products: ProductInfo[] = [
	{
		id: '1',
		product_id: '562503956948',
		sku_id: '0',
		product_cover: 'https://g-search3.alicdn.com/img/bao/uploaded/i4/i1/3954853577/O1CN01cFoXX21cIJlZJNmHo_!!4611686018427381449-0-item_pic.jpg_580x580q90.jpg',
		product_title: '作词作曲编曲高端定制音乐制作伴奏写歌曲原创音乐创作配乐后期',
		product_link: 'https://item.taobao.com/item.htm?priceTId=2147843d17421088719178993e1033&utparam=%7B%22aplus_abtest%22%3A%22a23fe5c14afda98f3e9b1f0774566f35%22%7D&id=562503956948&ns=1&abbucket=4&xxc=taobaoSearch&spm=a21n57.1.item.22',
		shop_name: '资料素材代下',
		shop_link: 'https://store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWUQk2MXwmvg354TY9NmnoC8bk3uSg9FYNswMvTCSYcFW9&spm=a21n57.1.item.22',
		price_unit: 'CNY',
		display_price: 100,
		display_sale: 200,
		estimated_revenue: 20000,
		title_images: ['https://img.alicdn.com/imgextra/i3/711413373/O1CN01VnYGzA1amsmbQfKuY_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i3/711413373/O1CN01VnYGzA1amsmbQfKuY_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i4/711413373/O1CN01YCguTD1amshrZKnD3_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i2/711413373/O1CN01skxSMa1amsi0yE3Q5_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i4/711413373/O1CN0135THPk1amsp6lQQOl_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i2/711413373/O1CN01kDgyII1amshnA2Afd_!!711413373.jpg_q50.jpg_.webp'],
		page_images: ['https://img.alicdn.com/imgextra/i2/711413373/O1CN01kDgyII1amshnA2Afd_!!711413373.jpg', 'https://img.alicdn.com/imgextra/i1/711413373/O1CN01eFDRq01amsmmWI3sk_!!711413373.jpg'],
		offer_details: { offer_items: [], valid_offers: [['CNY', '10000']] },
		additional_properties: { llm_analysis: { keyword: '修图', category: '修图', digital: true } },
		create_ts: 1741845547,
		update_ts: 1742108947,
		update_id: 'tb_crawler_task'
	},
	{
		id: '2',
		product_id: '562503956941',
		sku_id: '0',
		product_cover: 'https://g-search3.alicdn.com/img/bao/uploaded/i4/i1/3954853577/O1CN01cFoXX21cIJlZJNmHo_!!4611686018427381449-0-item_pic.jpg_580x580q90.jpg',
		product_title: '作词作曲编曲高端定制音乐制作伴奏写歌曲原创音乐创作配乐后期',
		product_link: 'https://item.taobao.com/item.htm?priceTId=2147843d17421088719178993e1033&utparam=%7B%22aplus_abtest%22%3A%22a23fe5c14afda98f3e9b1f0774566f35%22%7D&id=562503956948&ns=1&abbucket=4&xxc=taobaoSearch&spm=a21n57.1.item.22',
		shop_name: '资料素材代下',
		shop_link: 'https://store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWUQk2MXwmvg354TY9NmnoC8bk3uSg9FYNswMvTCSYcFW9&spm=a21n57.1.item.22',
		price_unit: 'CNY',
		display_price: 100,
		display_sale: 200,
		estimated_revenue: 20000,
		title_images: ['https://img.alicdn.com/imgextra/i3/711413373/O1CN01VnYGzA1amsmbQfKuY_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i3/711413373/O1CN01VnYGzA1amsmbQfKuY_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i4/711413373/O1CN01YCguTD1amshrZKnD3_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i2/711413373/O1CN01skxSMa1amsi0yE3Q5_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i4/711413373/O1CN0135THPk1amsp6lQQOl_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i2/711413373/O1CN01kDgyII1amshnA2Afd_!!711413373.jpg_q50.jpg_.webp'],
		page_images: ['https://img.alicdn.com/imgextra/i2/711413373/O1CN01kDgyII1amshnA2Afd_!!711413373.jpg', 'https://img.alicdn.com/imgextra/i1/711413373/O1CN01eFDRq01amsmmWI3sk_!!711413373.jpg'],
		offer_details: { offer_items: [], valid_offers: [['CNY', '10000']] },
		additional_properties: { llm_analysis: { keyword: '修图', category: '修图', digital: true } },
		create_ts: 1741845547,
		update_ts: 1742108947,
		update_id: 'tb_crawler_task'
	},
	{
		id: '3',
		product_id: '562503956949',
		sku_id: '0',
		product_cover: 'https://g-search3.alicdn.com/img/bao/uploaded/i4/i1/3954853577/O1CN01cFoXX21cIJlZJNmHo_!!4611686018427381449-0-item_pic.jpg_580x580q90.jpg',
		product_title: '作词作曲编曲高端定制音乐制作伴奏写歌曲原创音乐创作配乐后期',
		product_link: 'https://item.taobao.com/item.htm?priceTId=2147843d17421088719178993e1033&utparam=%7B%22aplus_abtest%22%3A%22a23fe5c14afda98f3e9b1f0774566f35%22%7D&id=562503956948&ns=1&abbucket=4&xxc=taobaoSearch&spm=a21n57.1.item.22',
		shop_name: '资料素材代下',
		shop_link: 'https://store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWUQk2MXwmvg354TY9NmnoC8bk3uSg9FYNswMvTCSYcFW9&spm=a21n57.1.item.22',
		price_unit: 'CNY',
		display_price: 100,
		display_sale: 200,
		estimated_revenue: 20000,
		title_images: ['https://img.alicdn.com/imgextra/i3/711413373/O1CN01VnYGzA1amsmbQfKuY_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i3/711413373/O1CN01VnYGzA1amsmbQfKuY_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i4/711413373/O1CN01YCguTD1amshrZKnD3_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i2/711413373/O1CN01skxSMa1amsi0yE3Q5_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i4/711413373/O1CN0135THPk1amsp6lQQOl_!!711413373.jpg_q50.jpg_.webp', 'https://img.alicdn.com/imgextra/i2/711413373/O1CN01kDgyII1amshnA2Afd_!!711413373.jpg_q50.jpg_.webp'],
		page_images: ['https://img.alicdn.com/imgextra/i2/711413373/O1CN01kDgyII1amshnA2Afd_!!711413373.jpg', 'https://img.alicdn.com/imgextra/i1/711413373/O1CN01eFDRq01amsmmWI3sk_!!711413373.jpg'],
		offer_details: { offer_items: [], valid_offers: [['CNY', '10000']] },
		additional_properties: { llm_analysis: { keyword: '修图', category: '修图', digital: true } },
		create_ts: 1741845547,
		update_ts: 1742108947,
		update_id: 'tb_crawler_task'
	}
];

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