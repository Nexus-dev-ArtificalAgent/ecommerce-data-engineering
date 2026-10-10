-- ==========================================
-- 0. DROP BẢNG CŨ (để làm sạch schema)
-- ==========================================
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_payment_method CASCADE;
DROP TABLE IF EXISTS dim_order_status CASCADE;


-- ==========================================
-- 1. DDL DIMENSION & FACT TABLES (Kiểu VARCHAR chuẩn xác)
-- ==========================================

CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    day_of_week INT NOT NULL
);

CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100)
);

CREATE TABLE dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit_price NUMERIC(12,2)
);

CREATE TABLE dim_payment_method (
    payment_method_id INT PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL
);

CREATE TABLE dim_order_status (
    order_status_id INT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL
);

CREATE TABLE fact_sales (
    sales_id SERIAL PRIMARY KEY,
    date_id INT REFERENCES dim_date(date_id),
    customer_id VARCHAR(50) REFERENCES dim_customer(customer_id),
    product_id VARCHAR(50) REFERENCES dim_product(product_id),
    payment_method_id INT REFERENCES dim_payment_method(payment_method_id),
    order_status_id INT REFERENCES dim_order_status(order_status_id),
    
    order_id VARCHAR(50) NOT NULL,
    
    quantity INT NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    discount NUMERIC(12,2) DEFAULT 0,
    revenue NUMERIC(12,2) NOT NULL
);


-- ==========================================
-- 2. DATA LOADING SCRIPTS
-- ==========================================

-- 2.1. Load dim_date
INSERT INTO dim_date (date_id, full_date, day, month, quarter, year, day_of_week)
SELECT DISTINCT 
    TO_CHAR(order_date, 'YYYYMMDD')::INT AS date_id,
    order_date::DATE AS full_date,
    EXTRACT(DAY FROM order_date)::INT AS day,
    EXTRACT(MONTH FROM order_date)::INT AS month,
    EXTRACT(QUARTER FROM order_date)::INT AS quarter,
    EXTRACT(YEAR FROM order_date)::INT AS year,
    EXTRACT(ISODOW FROM order_date)::INT AS day_of_week
FROM core.orders
ON CONFLICT (date_id) DO NOTHING;

-- 2.2. Load dim_customer
INSERT INTO dim_customer (customer_id, customer_name, email, phone, city)
SELECT customer_id, full_name AS customer_name, email, phone, city
FROM core.customers
ON CONFLICT (customer_id) DO NOTHING;

-- 2.3. Load dim_product
INSERT INTO dim_product (product_id, product_name, category, unit_price)
SELECT 
    p.product_id, 
    p.product_name, 
    c.category_name AS category, 
    p.unit_price
FROM core.products p
LEFT JOIN core.categories c ON p.category_id = c.category_id
ON CONFLICT (product_id) DO NOTHING;

-- 2.4. Load dim_payment_method
INSERT INTO dim_payment_method (payment_method_id, method_name)
SELECT 
    ROW_NUMBER() OVER (ORDER BY payment_method)::INT AS payment_method_id,
    payment_method AS method_name
FROM (SELECT DISTINCT payment_method FROM core.payments WHERE payment_method IS NOT NULL) sub
ON CONFLICT (payment_method_id) DO NOTHING;

-- 2.5. Load dim_order_status
INSERT INTO dim_order_status (order_status_id, status_name)
SELECT 
    ROW_NUMBER() OVER (ORDER BY status)::INT AS order_status_id,
    status AS status_name
FROM (SELECT DISTINCT status FROM core.orders WHERE status IS NOT NULL) sub
ON CONFLICT (order_status_id) DO NOTHING;

-- 2.6. Load fact_sales
INSERT INTO fact_sales (
    date_id, 
    customer_id, 
    product_id, 
    payment_method_id, 
    order_status_id, 
    order_id, 
    quantity, 
    unit_price, 
    discount, 
    revenue
)
SELECT 
    TO_CHAR(o.order_date, 'YYYYMMDD')::INT AS date_id,
    o.customer_id,
    oi.product_id,
    pm.payment_method_id,
    os.order_status_id,
    o.order_id,
    oi.quantity,
    oi.unit_price,
    COALESCE(oi.discount_amount, 0) AS discount,
    (oi.quantity * oi.unit_price - COALESCE(oi.discount_amount, 0)) AS revenue
FROM core.orders o
JOIN core.order_items oi ON o.order_id = oi.order_id
LEFT JOIN core.payments p ON o.order_id = p.order_id
LEFT JOIN dim_payment_method pm ON p.payment_method = pm.method_name
LEFT JOIN dim_order_status os ON o.status = os.status_name;