SELECT 'dim_date' AS table_name, COUNT(*) FROM dim_date
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_payment_method', COUNT(*) FROM dim_payment_method
UNION ALL
SELECT 'dim_order_status', COUNT(*) FROM dim_order_status
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales;

-- ==========================================
-- SCRIPT ĐỐI SOÁT TỔNG DOANH THU (REVENUE RECONCILIATION)
-- ==========================================
SELECT 
    (SELECT SUM((quantity * unit_price) - COALESCE(discount_amount, 0)) FROM core.order_items) AS oltp_revenue,
    (SELECT SUM(revenue) FROM fact_sales) AS mart_revenue,
    ABS(
        (SELECT SUM((quantity * unit_price) - COALESCE(discount_amount, 0)) FROM core.order_items) - 
        (SELECT SUM(revenue) FROM fact_sales)
    ) AS revenue_difference;