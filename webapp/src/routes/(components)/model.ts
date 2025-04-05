export type LLMAnalyzeResult = {
  keyword: string;
  category: string;
  digital: boolean;
}
export type ErrorEntity = {
  err_code: number;
  call_stack: string;
  update_ts: number;
}
export type AdditionalProperties = {
  llm_analysis: LLMAnalyzeResult;
  errors: ErrorEntity[];
  diff: string;
}
export type OperationHistory = {
  id: number;
  pk: string;
  table_name: string;
  additional_properties: AdditionalProperties;
  operation: number;
  operation_ts: number;
  create_ts: number;
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
export type ProductInfo = {
  product_id: string;
  sku_id: string;
  product_cover: string;
  product_title: string;
  product_link: string;
  shop_name: string;
  shop_link: string;
  keyword: string;
  category: string;
  digital: boolean;
  digital_str: string;
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
  update_role: string;
};

export type ShadowProductInfo = {
  product_id: string;
  shadow_id: string;
  product_title: string;
  shop_name: string;
  keyword: string;
  category: string;
  digital: boolean;
  digital_str: string;
  price_unit: string;
  price: number;
  inventory: number;
  title_images: string[];
  page_images: string[];
  offer_details: OfferInfo;
  additional_properties: AdditionalProperties;
  status: number;
  status_str: string;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type ProductSale = {
  product_id: string;
  shop_name: string;
  price_unit: string;
  display_price: number;
  display_sale: number;
  estimated_revenue: number;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_id: string;
  update_role: string;
};

export type ProductHistory = {
  id: number;
  additional_properties: AdditionalProperties;
  operation: number;
  operation_ts: number;
  create_ts: number;
  update_id: string;
  update_role: string;
  updater: string;
  detail: string;
}

export type ShopInfo = {
  shop_name: string;
  shop_link: string;
  shop_cover: string;
  avg_price: number;
  total_sale: number;
  total_revenue: number;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type DetailCrawlTask = {
  id: string;
  product_id: string;
  product_link: string;
  status: number;
  status_str: string;
  reason: string;
  try_count: number;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type LLMAnalyzeTask = {
  id: string;
  product_id: string;
  product_title: string;
  status: number;
  status_str: string;
  reason: string;
  try_count: number;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type SearchCrawlTask = {
  id: string;
  search_key: string;
  num_of_pages: string;
  status: number;
  status_str: string;
  reason: string;
  try_count: number;
  target_product_ids: string[];
  target_product_ids_str: string;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type ShopCrawlTask = {
  id: string;
  shop_name: string;
  status: number;
  status_str: string;
  reason: string;
  try_count: number;
  target_product_ids: string[];
  target_product_ids_str: string;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type ShopSearchCrawlTask = {
  id: string;
  shop_name: string;
  status: number;
  status_str: string;
  reason: string;
  try_count: number;
  additional_properties: AdditionalProperties;
  create_ts: number;
  update_ts: number;
  update_id: string;
  update_role: string;
};

export type ProductManageTask = {
  id: string;
  product_id: string;
  shop_name: string;
  operation: number;
  operation_str: string;
  status: number;
  status_str: string;
  reason: string;
  try_count: number;
  additional_properties: AdditionalProperties;
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
  RUNNING: number;
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

export function parseUUID4(value: string) {
  const regexp = /^\w{32}$/g;
  if (value.match(regexp)) {
    return value.substring(0, 16);
  } else {
    return value;
  }
}

export function timeConverter(ts: number) {
  let a = new Date(ts * 1000);
  const d = `${a.getFullYear()}/${String(a.getMonth() + 1).padStart(2, '0')}/${String(a.getDate()).padStart(2, '0')}`;
  const t = `${String(a.getHours()).padStart(2, '0')}:${String(a.getMinutes()).padStart(2, '0')}:${String(a.getSeconds()).padStart(2, '0')}`;
  return [d, t];
}

export function statusToString(status: number) {
  let task_status = '';
  if (status === 1) {
    task_status = 'NEW';
  } else if (status === 2) {
    task_status = 'RUNNING';
  } else if (status === 3) {
    task_status = 'DONE';
  } else if (status === 4) {
    task_status = 'ERROR';
  } else if (status === 5) {
    task_status = 'ARCHIVED';
  }
  return task_status;
}

export function shadowStatusToString(status: number) {
  let shadow_status = '';
  if (status === 0) {
    shadow_status = 'NEW';
  } else if (status === 1) {
    shadow_status = 'READY';
  } else if (status === 2) {
    shadow_status = 'ON_SHELF';
  } else if (status === 3) {
    shadow_status = 'ONLINE';
  } else if (status === 4) {
    shadow_status = 'OFFLINE';
  } else if (status === 5) {
    shadow_status = 'OFF_SHELF';
  }
  return shadow_status;
}

export function shadowOperationToString(status: number) {
  let shadow_operation = '';
  if (status === 1) {
    shadow_operation = 'PREPARE';
  } else if (status === 2) {
    shadow_operation = 'ON_SHELF';
  } else if (status === 3) {
    shadow_operation = 'ONLINE';
  } else if (status === 4) {
    shadow_operation = 'OFFLINE';
  } else if (status === 5) {
    shadow_operation = 'OFF_SHELF';
  }
  return shadow_operation;
}

export function parseTaskReason(task: any) {
  const additionalProperties: AdditionalProperties = task.additional_properties;
  if ([1, 2, 3].includes(task.status)) {
    return 'SUCCESS';
  }
  if (additionalProperties.errors == undefined) {
    return 'SUCCESS';
  } else {
    let counts: Map<number, number> = new Map();
    let max = 0;
    additionalProperties.errors.forEach((error: ErrorEntity) => {
      const value = error.err_code;
      counts.set(value, (counts.get(value) || 0) + 1);
      if (max == 0 || counts.get(value)! > counts.get(max)!) {
        max = value;
      }
    });
    if (max === 0) {
      return 'SUCCESS';
    } else {
      let v = '';
      if (max === 1) {
        v = 'UNEXPECTED';
      } else if (max === 2) {
        v = 'NOT_STANDARD_SHOP';
      } else if (max === 3) {
        v = 'SHOP_SKU_EXCEEDS';
      } else if (max === 4) {
        v = 'SHOP_NOT_EXIST';
      } else if (max === 5) {
        v = 'SHOP_LINK_NOT_ACCESSIBLE';
      } else if (max === 6) {
        v = 'SHOP_NOT_FOUND_IN_SEARCH';
      } else if (max === 7) {
        v = 'SHOP_LINK_NOT_FOUND';
      } else {
        v = 'UNKNOWN'
      }
      return `${v}[${counts.get(max)!}]`;
    }
  }
}

export function assert(condition: boolean, message: string) {
  if (!condition) {
    throw message || 'Assertion failed';
  }
}