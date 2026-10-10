# Báo cáo kiểm thử hiệu năng (Performance Testing)

## 1. Truy vấn trên hệ thống OLTP gốc
- **SQL Statement:** 
EXPLAIN ANALYZE
SELECT 
    EXTRACT(YEAR FROM o.order_date) AS yr,
    EXTRACT(MONTH FROM o.order_date) AS mth,
    SUM((oi.quantity * oi.unit_price) - COALESCE(oi.discount_amount, 0)) AS total_revenue
FROM core.orders o
JOIN core.order_items oi ON o.order_id = oi.order_id
GROUP BY yr, mth
ORDER BY yr, mth;

- **Execution Time:** 19.809 ms
- **Nhận xét:** Phải quét qua các bảng trung gian lớn (`orders`, `order_items`), thực hiện tính toán `SUM` và xử lý `COALESCE` trực tiếp trên dữ liệu thô, dẫn đến chi phí CPU và thời gian xử lý cao hơn.

## 2. Truy vấn trên Data Mart (Star Schema)
- **SQL Statement:** 
EXPLAIN ANALYZE
SELECT 
    d.year,
    d.month,
    SUM(f.revenue) AS total_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

- **Execution Time:** 6.550 ms
- **Nhận xét:** Tận dụng cấu trúc bảng phẳng `fact_sales` kết hợp với bảng chiều `dim_date`, giảm thiểu tối đa số lượng phép JOIN phức tạp, giúp câu lệnh thực thi nhanh hơn rõ rệt.

## 3. Kết luận chung
Mô hình Data Mart (Star Schema) tối ưu hóa hiệu năng truy vấn tốt hơn nhờ cấu trúc phi chuẩn hóa một phần, giúp các nhà quản trị trích xuất báo cáo KPI nhanh chóng mà không làm nghẽn hệ thống giao dịch OLTP chính.