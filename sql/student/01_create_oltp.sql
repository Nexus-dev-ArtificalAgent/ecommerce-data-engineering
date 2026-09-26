-- ============================================================
-- File: sql/student/01_create_oltp.sql
-- Description: Core Schema Initialization for PostgreSQL 16
-- ============================================================

-- 1. Khởi tạo Schema
CREATE SCHEMA IF NOT EXISTS core;
SET search_path TO core, public;

-- 2. Bảng Danh mục Sản phẩm (categories)
CREATE TABLE IF NOT EXISTS core.categories (
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Bảng Trạng thái Đơn hàng (order_status)
CREATE TABLE IF NOT EXISTS core.order_status (
    status_id   SERIAL PRIMARY KEY,
    status_code VARCHAR(20) UNIQUE NOT NULL,
    status_name VARCHAR(50) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Bảng Khách hàng (customers)
CREATE TABLE IF NOT EXISTS core.customers (
    customer_id      SERIAL PRIMARY KEY,
    full_name        VARCHAR(100) NOT NULL,
    email            VARCHAR(150) UNIQUE NOT NULL,
    phone            VARCHAR(20),
    city             VARCHAR(50),
    customer_segment VARCHAR(20) DEFAULT 'Standard',
    status           VARCHAR(20) NOT NULL DEFAULT 'active',
    source_system    VARCHAR(50) NOT NULL DEFAULT 'unknown',
    ingested_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Bảng Sản phẩm (products)
CREATE TABLE IF NOT EXISTS core.products (
    product_id    SERIAL PRIMARY KEY,
    category_id   INT NOT NULL REFERENCES core.categories(category_id),
    sku           VARCHAR(100) UNIQUE NOT NULL,
    product_name  VARCHAR(200) NOT NULL,
    unit_price    NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    cost_price    NUMERIC(14,2) NOT NULL CHECK (cost_price >= 0),
    status        VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'discontinued')),
    source_system VARCHAR(50) NOT NULL DEFAULT 'unknown',
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Bảng Đơn hàng (orders)
CREATE TABLE IF NOT EXISTS core.orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES core.customers(customer_id),
    order_date   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_amount NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    status_id    INT NOT NULL REFERENCES core.order_status(status_id),
    source_system VARCHAR(50) NOT NULL DEFAULT 'unknown',
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Bảng Chi tiết Đơn hàng (order_items)
CREATE TABLE IF NOT EXISTS core.order_items (
    order_item_id  SERIAL PRIMARY KEY,
    order_id       INT NOT NULL REFERENCES core.orders(order_id) ON DELETE CASCADE,
    product_id     INT NOT NULL REFERENCES core.products(product_id),
    quantity       INT NOT NULL CHECK (quantity > 0),
    unit_price     NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    source_system  VARCHAR(50) NOT NULL DEFAULT 'unknown',
    ingested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Bảng Thanh toán (payments)
CREATE TABLE IF NOT EXISTS core.payments (
    payment_id     SERIAL PRIMARY KEY,
    order_id       INT NOT NULL REFERENCES core.orders(order_id),
    payment_date   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    amount         NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('credit_card', 'bank_transfer', 'e_wallet', 'cod')),
    source_system  VARCHAR(50) NOT NULL DEFAULT 'unknown',
    ingested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Seed lookup data cho order_status
INSERT INTO core.order_status (status_code, status_name) VALUES
    ('pending',   'Chờ xử lý'),
    ('confirmed', 'Đã xác nhận'),
    ('shipped',   'Đang giao'),
    ('completed', 'Hoàn tất'),
    ('cancelled', 'Đã hủy')
ON CONFLICT (status_code) DO NOTHING;

-- 10. Tạo các Indexes tối ưu hiệu năng
CREATE INDEX IF NOT EXISTS idx_products_category ON core.products(category_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON core.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON core.orders(status_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON core.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON core.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON core.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON core.payments(order_id);