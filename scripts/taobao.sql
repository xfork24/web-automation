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
    update_id   varchar(32)   NOT NULL,
    update_role varchar(64)   NOT NULL,
    PRIMARY KEY (id)
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
    update_id   varchar(32)  NOT NULL,
    update_role varchar(64)  NOT NULL,
    PRIMARY KEY (name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create commodity_sales Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS commodity_sale
(
    id                   varchar(32)  NOT NULL,
    shop_name            varchar(128) NOT NULL,
    price_unit           varchar(3)   NOT NULL,
    display_price        int          NOT NULL,
    display_sale         int          NOT NULL,
    estimated_total_sale int          NOT NULL,
    create_ts            int          NOT NULL,
    update_ts            int          NOT NULL,
    update_id            varchar(32)  NOT NULL,
    update_role          varchar(64)  NOT NULL,
    PRIMARY KEY (id, update_ts)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create operation_history Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS operation_history
(
    id           int          NOT NULL AUTO_INCREMENT,
    pk           varchar(128) NOT NULL,
    table_name   varchar(32)  NOT NULL,
    update_id    varchar(32)  NOT NULL,
    update_role  varchar(64)  NOT NULL,
    operation_ts int          NOT NULL,
    operation    int          NOT NULL,
    create_ts    int          NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create detail_crawl_tasks Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS detail_crawl_task
(
    id           varchar(32)  NOT NULL,
    commodity_id varchar(32)  NOT NULL,
    link         varchar(512) NOT NULL,
    status       tinyint      NOT NULL,
    create_ts    int          NOT NULL,
    update_ts    int          NOT NULL,
    update_id    varchar(32)  NOT NULL,
    update_role  varchar(64)  NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create shop_crawl_tasks Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS shop_crawl_task
(
    id          varchar(32)  NOT NULL,
    shop_name   varchar(128) NOT NULL,
    link        varchar(512) NOT NULL,
    status      tinyint      NOT NULL,
    create_ts   int          NOT NULL,
    update_ts   int          NOT NULL,
    update_id   varchar(32)  NOT NULL,
    update_role varchar(64)  NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- --------------------------------
-- Create search_crawl_tasks Table
-- --------------------------------
CREATE TABLE IF NOT EXISTS search_crawl_task
(
    id           varchar(32) NOT NULL,
    search_key   varchar(32) NOT NULL,
    num_of_pages int         NOT NULL,
    status       tinyint     NOT NULL,
    create_ts    int         NOT NULL,
    update_ts    int         NOT NULL,
    update_id    varchar(32) NOT NULL,
    update_role  varchar(64) NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- -----------------------------------
-- Create Indexes And Foreign Keys
-- -----------------------------------
ALTER TABLE commodity_info
    ADD INDEX idx_sku_id (sku_id);
ALTER TABLE commodity_info
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE commodity_info
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE commodity_info
    ADD INDEX idx_update_id (update_id);

ALTER TABLE shop_info
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE shop_info
    ADD INDEX idx_update_id (update_id);

ALTER TABLE commodity_sale
    ADD INDEX idx_shop_name (shop_name);
ALTER TABLE commodity_sale
    ADD INDEX idx_display_sale (display_sale);
ALTER TABLE commodity_sale
    ADD INDEX idx_estimated_total_sale (estimated_total_sale);
ALTER TABLE commodity_sale
    ADD INDEX idx_update_ts (update_ts);
ALTER TABLE commodity_sale
    ADD INDEX idx_update_id (update_id);

ALTER TABLE operation_history
    ADD INDEX idx_pk_table_name (pk, table_name);
ALTER TABLE operation_history
    ADD INDEX idx_update_role_operation_ts (update_role, operation_ts);
ALTER TABLE operation_history
    ADD INDEX idx_create_ts (create_ts);
ALTER TABLE operation_history
    ADD INDEX idx_update_id (update_id);

ALTER TABLE detail_crawl_task
    ADD INDEX idx_commodity_id (commodity_id);
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

ALTER TABLE commodity_info
    ADD CONSTRAINT fk_commodity_info_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (name);
ALTER TABLE commodity_sale
    ADD CONSTRAINT fk_commodity_sale_id FOREIGN KEY (id) REFERENCES commodity_info (id);
ALTER TABLE commodity_sale
    ADD CONSTRAINT fk_commodity_sale_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (name);
ALTER TABLE detail_crawl_task
    ADD CONSTRAINT fk_detail_crawl_task_commodity_id FOREIGN KEY (commodity_id) REFERENCES commodity_info (id);
ALTER TABLE shop_crawl_task
    ADD CONSTRAINT fk_shop_crawl_task_shop_name FOREIGN KEY (shop_name) REFERENCES shop_info (name);

-- --------------------------------------------
-- Create User taobao And Grant Permissions
-- --------------------------------------------
CREATE USER IF NOT EXISTS 'taobao'@'localhost'
    IDENTIFIED BY 'taobao';
GRANT ALL PRIVILEGES ON taobao.* TO 'taobao'@'localhost';
FLUSH PRIVILEGES;
