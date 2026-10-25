-- Tạo schema mart nếu chưa tồn tại
CREATE SCHEMA IF NOT EXISTS mart;

-- Xóa các bảng cũ (nếu có xung đột kiểu dữ liệu từ lần chạy trước)
DROP TABLE IF EXISTS mart.fact_sales CASCADE;
DROP TABLE IF EXISTS mart.dim_customer CASCADE;
DROP TABLE IF EXISTS mart.dim_product CASCADE;

-- 1. Làm mới bảng chiều Khách hàng (dim_customer)
CREATE TABLE mart.dim_customer (
    customer_id VARCHAR(255) PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP
);

INSERT INTO mart.dim_customer (customer_id, customer_name, email, created_at)
SELECT DISTINCT customer_id, full_name AS customer_name, email, created_at
FROM core.customers
ON CONFLICT (customer_id) DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    email = EXCLUDED.email;

-- 2. Làm mới bảng chiều Sản phẩm (dim_product)
CREATE TABLE mart.dim_product (
    product_id VARCHAR(255) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(255),
    price NUMERIC
);

INSERT INTO mart.dim_product (product_id, product_name, category, price)
SELECT DISTINCT p.product_id, p.product_name, c.category_name AS category, p.unit_price AS price
FROM core.products p
LEFT JOIN core.categories c ON p.category_id = c.category_id
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name,
    category = EXCLUDED.category,
    price = EXCLUDED.price;

-- 3. Làm mới bảng chiều Phương thức thanh toán (dim_payment_method)
CREATE TABLE IF NOT EXISTS mart.dim_payment_method (
    payment_method_id SERIAL PRIMARY KEY,
    payment_method_name VARCHAR(100) UNIQUE
);

INSERT INTO mart.dim_payment_method (payment_method_name)
SELECT DISTINCT payment_method FROM core.payments WHERE payment_method IS NOT NULL
ON CONFLICT (payment_method_name) DO NOTHING;

-- 4. Làm mới bảng chiều Trạng thái đơn hàng (dim_order_status)
CREATE TABLE IF NOT EXISTS mart.dim_order_status (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE
);

INSERT INTO mart.dim_order_status (status_name)
SELECT DISTINCT status FROM core.orders WHERE status IS NOT NULL
ON CONFLICT (status_name) DO NOTHING;

-- 5. Tự động sinh bảng chiều thời gian (dim_date) từ 2025-01-01 đến 2027-12-31
CREATE TABLE IF NOT EXISTS mart.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE UNIQUE,
    year INT,
    quarter INT,
    month INT,
    day INT,
    day_of_week INT
);

INSERT INTO mart.dim_date (date_key, full_date, year, quarter, month, day, day_of_week)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_key,
    d AS full_date,
    EXTRACT(YEAR FROM d)::INT AS year,
    EXTRACT(QUARTER FROM d)::INT AS quarter,
    EXTRACT(MONTH FROM d)::INT AS month,
    EXTRACT(DAY FROM d)::INT AS day,
    EXTRACT(ISODOW FROM d)::INT AS day_of_week
FROM generate_series('2025-01-01'::date, '2027-12-31'::date, '1 day'::interval) d
ON CONFLICT (date_key) DO NOTHING;

-- 6. Nạp bảng sự kiện mart.fact_sales từ core.order_items kết hợp core.orders và các bảng chiều
CREATE TABLE mart.fact_sales (
    order_item_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255),
    customer_id VARCHAR(255),
    product_id VARCHAR(255),
    date_key INT,
    quantity INT,
    unit_price NUMERIC,
    net_amount NUMERIC,
    status VARCHAR(50)
);

INSERT INTO mart.fact_sales (order_item_id, order_id, customer_id, product_id, date_key, quantity, unit_price, net_amount, status)
SELECT 
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    oi.product_id,
    TO_CHAR(o.order_date::date, 'YYYYMMDD')::INT AS date_key,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS net_amount,
    o.status
FROM core.order_items oi
JOIN core.orders o ON oi.order_id = o.order_id
ON CONFLICT (order_item_id) DO NOTHING;