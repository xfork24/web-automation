-- --------------------------------
-- Create taobao Database
-- --------------------------------
CREATE DATABASE IF NOT EXISTS taobao
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE taobao;

-- --------------------------------
-- Create commodity_info Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS commodity_info
(
    id          varchar(32)   NOT NULL,
    sku_id      varchar(32)   NOT NULL,
    title       varchar(128)  NOT NULL,
    link        varchar(512)  NOT NULL,
    shop_name   varchar(128)  NOT NULL,
    title_imgs  varchar(4096) NOT NULL,
    page_imgs   varchar(4096) NOT NULL,
    details     varchar(4096) NOT NULL,
    create_ts   int           NOT NULL,
    update_ts   int           NOT NULL,
    update_role varchar(64)   NOT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create shop_info Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS shop_info
(
    name        varchar(128) NOT NULL,
    link        varchar(512) NOT NULL,
    create_ts   int          NOT NULL,
    update_ts   int          NOT NULL,
    update_role varchar(64)  NOT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create commodity_sales Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS commodity_sales
(
    id                   varchar(32)  NOT NULL,
    ts                   int          NOT NULL,
    shop_name            varchar(128) NOT NULL,
    price_unit           varchar(3)   NOT NULL,
    display_price        int          NOT NULL,
    display_sale         int          NOT NULL,
    estimated_total_sale int          NOT NULL,
    create_ts            int          NOT NULL,
    update_ts            int          NOT NULL,
    update_role          varchar(64)  NOT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create detail_crawl_tasks Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS detail_crawl_tasks
(
    id           int          NOT NULL,
    commodity_id varchar(32)  NOT NULL,
    link         varchar(512) NOT NULL,
    status       tinyint      NOT NULL,
    create_ts    int          NOT NULL,
    update_ts    int          NOT NULL,
    update_role  varchar(64)  NOT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- -----------------------------------
-- Create Indexes And Foreign Keys
-- -----------------------------------
ALTER TABLE commodity_info
    ADD PRIMARY KEY (id);
ALTER TABLE commodity_info
    ADD INDEX idx_sku_id (sku_id);
ALTER TABLE commodity_info
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE commodity_info
    ADD INDEX idx_update_ts (update_ts);

ALTER TABLE shop_info
    ADD PRIMARY KEY (name);
ALTER TABLE shop_info
    ADD INDEX idx_update_ts (update_ts);

ALTER TABLE commodity_sales
    ADD PRIMARY KEY (id, ts);
ALTER TABLE commodity_sales
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE commodity_sales
    ADD INDEX idx_display_sale (display_sale);
ALTER TABLE commodity_sales
    ADD INDEX idx_estimated_total_sale (estimated_total_sale);
ALTER TABLE commodity_sales
    ADD INDEX idx_update_ts (update_ts);

ALTER TABLE detail_crawl_tasks
    ADD PRIMARY KEY (id);
ALTER TABLE detail_crawl_tasks
    ADD INDEX idx_commodity_id (commodity_id);
ALTER TABLE detail_crawl_tasks
    ADD INDEX idx_status (status);
ALTER TABLE detail_crawl_tasks
    ADD INDEX idx_update_ts (update_ts);

ALTER TABLE commodity_info
    ADD CONSTRAINT fk_commodity_info_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (name);
ALTER TABLE commodity_sales
    ADD CONSTRAINT fk_commodity_sales_id FOREIGN KEY (id) REFERENCES commodity_info (id);
ALTER TABLE commodity_sales
    ADD CONSTRAINT fk_commodity_sales_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (name);
ALTER TABLE detail_crawl_tasks
    ADD CONSTRAINT fk_detail_crawl_tasks_commodity_id FOREIGN KEY (commodity_id) REFERENCES commodity_info (id);

-- --------------------------------------------
-- Create User taobao And Grant Permissions
-- --------------------------------------------
CREATE USER IF NOT EXISTS 'taobao'@'localhost'
    IDENTIFIED BY 'taobao';
GRANT ALL PRIVILEGES ON taobao.* TO 'taobao'@'localhost';
FLUSH PRIVILEGES;
