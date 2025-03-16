-- --------------------------------
-- Create taobao Database
-- --------------------------------
CREATE DATABASE IF NOT EXISTS taobao
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE taobao;

-- --------------------------------
-- Create product_info Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS product_info
(
    product_id            varchar(32)   NOT NULL,
    sku_id                varchar(32)   NOT NULL,
    product_title         varchar(128)  NOT NULL,
    product_link          varchar(512)  NOT NULL,
    product_cover         text          NOT NULL,
    shop_name             varchar(128)  NOT NULL,
    price_unit            varchar(3)    NOT NULL,
    display_price         int           NOT NULL,
    display_sale          int           NOT NULL,
    estimated_revenue     int           NOT NULL,
    title_imgs            text          NOT NULL,
    page_imgs             text          NOT NULL,
    offer_details         text          NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (product_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create shop_info Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS shop_info
(
    shop_name             varchar(128)  NOT NULL,
    shop_link             varchar(512)  NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (shop_name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create product_sale Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS product_sale
(
    product_id            varchar(32)   NOT NULL,
    shop_name             varchar(128)  NOT NULL,
    price_unit            varchar(3)    NOT NULL,
    display_price         int           NOT NULL,
    display_sale          int           NOT NULL,
    estimated_revenue     int           NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (product_id, create_ts)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create hot_product Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS hot_product
(
    product_id            varchar(32)   NOT NULL,
    shop_name             varchar(128)  NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (product_id, create_ts)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create operation_history Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS operation_history
(
    id                    int           NOT NULL AUTO_INCREMENT,
    pk                    varchar(128)  NOT NULL,
    table_name            varchar(32)   NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    operation_ts          int           NOT NULL,
    operation             int           NOT NULL,
    create_ts             int           NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create detail_crawl_task Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS detail_crawl_task
(
    id                    varchar(32)   NOT NULL,
    product_id            varchar(32)   NOT NULL,
    product_link          varchar(512)  NOT NULL,
    status                tinyint       NOT NULL,
    try_count             int           NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create shop_crawl_task Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS shop_crawl_task
(
    id                    varchar(32)   NOT NULL,
    shop_name             varchar(128)  NOT NULL,
    target_product_ids    varchar(1024) NOT NULL,
    status                tinyint       NOT NULL,
    try_count             int           NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create search_crawl_task Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS search_crawl_task
(
    id                    varchar(32)   NOT NULL,
    search_key            varchar(128)  NOT NULL,
    num_of_pages          int           NOT NULL,
    status                tinyint       NOT NULL,
    try_count             int           NOT NULL,
    target_product_ids    varchar(1024) NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- -------------------------------------
-- Create shop_search_crawl_task Table
-- -------------------------------------
CREATE TABLE IF NOT EXISTS shop_search_crawl_task
(
    id                    varchar(32)   NOT NULL,
    shop_name             varchar(128)  NOT NULL,
    status                tinyint       NOT NULL,
    try_count             int           NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create llm_analyze_task Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS llm_analyze_task
(
    id                    varchar(32)   NOT NULL,
    product_id            varchar(32)   NOT NULL,
    product_title         varchar(128)  NOT NULL,
    status                tinyint       NOT NULL,
    try_count             int           NOT NULL,
    additional_properties varchar(4096) NOT NULL,
    create_ts             int           NOT NULL,
    update_ts             int           NOT NULL,
    update_id             varchar(32)   NOT NULL,
    update_role           varchar(64)   NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- -----------------------------------
-- Create Indexes And Foreign Keys
-- -----------------------------------
ALTER TABLE product_info
    ADD INDEX idx_sku_id (sku_id);
ALTER TABLE product_info
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE product_info
    ADD INDEX idx_display_sale (display_sale);
ALTER TABLE product_info
    ADD INDEX idx_estimated_revenue (estimated_revenue);
ALTER TABLE product_info
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE product_info
    ADD INDEX idx_update_id (update_id);

ALTER TABLE shop_info
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE shop_info
    ADD INDEX idx_update_id (update_id);

ALTER TABLE product_sale
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE product_sale
    ADD INDEX idx_display_sale (display_sale);
ALTER TABLE product_sale
    ADD INDEX idx_estimated_revenue (estimated_revenue);
ALTER TABLE product_sale
    ADD INDEX idx_create_ts (create_ts);
ALTER TABLE product_sale
    ADD INDEX idx_update_id (update_id);

ALTER TABLE hot_product
    ADD INDEX idx_create_ts (create_ts);
ALTER TABLE hot_product
    ADD INDEX idx_update_id (update_id);

ALTER TABLE operation_history
    ADD INDEX idx_pk_table_name (pk, table_name);
ALTER TABLE operation_history
    ADD INDEX idx_update_id_operation_ts (update_id, operation_ts);
ALTER TABLE operation_history
    ADD INDEX idx_create_ts (create_ts);
ALTER TABLE operation_history
    ADD INDEX idx_update_id (update_id);

ALTER TABLE detail_crawl_task
    ADD INDEX idx_product_id (product_id);
ALTER TABLE detail_crawl_task
    ADD INDEX idx_status (status);
ALTER TABLE detail_crawl_task
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE detail_crawl_task
    ADD INDEX idx_update_id (update_id);

ALTER TABLE shop_crawl_task
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE shop_crawl_task
    ADD INDEX idx_status (status);
ALTER TABLE shop_crawl_task
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE shop_crawl_task
    ADD INDEX idx_update_id (update_id);

ALTER TABLE search_crawl_task
    ADD INDEX idx_search_key (search_key);
ALTER TABLE search_crawl_task
    ADD INDEX idx_status (status);
ALTER TABLE search_crawl_task
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE search_crawl_task
    ADD INDEX idx_update_id (update_id);

ALTER TABLE llm_analyze_task
    ADD INDEX idx_product_id (product_id);
ALTER TABLE llm_analyze_task
    ADD INDEX idx_status (status);
ALTER TABLE llm_analyze_task
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE llm_analyze_task
    ADD INDEX idx_update_id (update_id);

ALTER TABLE shop_search_crawl_task
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE shop_search_crawl_task
    ADD INDEX idx_status (status);
ALTER TABLE shop_search_crawl_task
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE shop_search_crawl_task
    ADD INDEX idx_update_id (update_id);

ALTER TABLE product_info
    ADD CONSTRAINT fk_product_info_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (shop_name);
ALTER TABLE product_sale
    ADD CONSTRAINT fk_product_sale_product_id FOREIGN KEY (product_id) REFERENCES product_info (product_id);
ALTER TABLE product_sale
    ADD CONSTRAINT fk_product_sale_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (shop_name);
ALTER TABLE hot_product
    ADD CONSTRAINT fk_hot_product_product_id FOREIGN KEY (product_id) REFERENCES product_info (product_id);
ALTER TABLE hot_product
    ADD CONSTRAINT fk_hot_product_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (shop_name);
ALTER TABLE detail_crawl_task
    ADD CONSTRAINT fk_detail_crawl_task_product_id FOREIGN KEY (product_id) REFERENCES product_info (product_id);
ALTER TABLE shop_crawl_task
    ADD CONSTRAINT fk_shop_crawl_task_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (shop_name);
ALTER TABLE shop_search_crawl_task
    ADD CONSTRAINT fk_shop_search_crawl_task_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (shop_name);
ALTER TABLE llm_analyze_task
    ADD CONSTRAINT fk_llm_analyze_task_product_id FOREIGN KEY (product_id) REFERENCES product_info (product_id);

-- --------------------------------------------
-- Create User taobao And Grant Permissions
-- --------------------------------------------
CREATE USER IF NOT EXISTS 'taobao'@'localhost'
    IDENTIFIED BY 'taobao';
GRANT ALL PRIVILEGES ON taobao.* TO 'taobao'@'localhost';
FLUSH PRIVILEGES;
