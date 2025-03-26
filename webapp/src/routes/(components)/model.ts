export type OperationHistoryAdditionalProperties = {}
export type OperationHistory = {
	id: number;
	pk: string;
	table_name: string;
	additional_properties: OperationHistoryAdditionalProperties;
	operation_ts: number;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};

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
export type ProductInfoAdditionalProperties = {
	llm_analysis: LLMAnalyzeResult;
}
export type ProductInfo = {
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
	additional_properties: ProductInfoAdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};
export type ProductSaleAdditionalProperties = {
	llm_analysis: LLMAnalyzeResult;
}
export type ProductSale = {
	product_id: string;
	shop_name: string;
	price_unit: string;
	display_price: number;
	display_sale: number;
	estimated_revenue: number;
	additional_properties: ProductSaleAdditionalProperties;
	create_ts: number;
	update_id: string;
	update_role: string;
};

export type ShopInfoAdditionalProperties = {}
export type ShopInfo = {
	shop_name: string;
	shop_link: string;
	avg_price: number;
	total_sale: number;
	total_revenue: number;
	additional_properties: ShopInfoAdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};


export type DetailCrawlTaskAdditionalProperties = {}
export type DetailCrawlTask = {
	id: number;
	product_id: string;
	product_link: string;
	status: string;
	try_count: number;
	additional_properties: DetailCrawlTaskAdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};


type LLMAnalyzeTaskAdditionalProperties = {}
export type LLMAnalyzeTask = {
	id: number;
	product_id: string;
	product_title: string;
	status: string;
	try_count: number;
	additional_properties: LLMAnalyzeTaskAdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};

export type AdditionalProperties = {}
export type SearchCrawlTask = {
	id: number;
	search_key: string;
	num_of_pages: string;
	status: string;
	try_count: number;
	target_product_ids: string;
	additional_properties: AdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};


type ShopCrawlTaskAdditionalProperties = {}
export type ShopCrawlTask = {
	id: number;
	shop_name: string;
	status: string;
	try_count: number;
	target_product_ids: string;
	additional_properties: ShopCrawlTaskAdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};


export type ShopSearchCrawlTaskAdditionalProperties = {}
export type ShopSearchCrawlTask = {
	id: number;
	shop_name: string;
	status: string;
	try_count: number;
	target_product_ids: string;
	additional_properties: ShopSearchCrawlTaskAdditionalProperties;
	create_ts: number;
	update_ts: number;
	update_id: string;
	update_role: string;
};

export type TaskStatus = {
	key: string;
	title: string;
	link: string;
	NEW: number;
	IN_PROGRESS: number;
	DONE: number;
	ERROR: number;
	ARCHIVED: number;
}
export type TaskStatusResult = {
	detail_crawl_task: TaskStatus;
	search_crawl_task: TaskStatus;
	shop_crawl_task: TaskStatus;
	shop_search_crawl_task: TaskStatus;
	llm_analyze_task: TaskStatus;
}