# Phần 1.4: Business Questions - Trả lời và nhận xét

## 1. Total revenue tháng 7/2026
**Query SQL:**
```sql 
set search_path to core, public;
select sum(order_total) as total_revenue_july_2026 from orders 
 where order_date >= '2026-07-01' and order_date < '2026-08-01';
```

Đáp án: 0 VNĐ
Nhận xét: Dữ liệu trong bảng "orders" hiện tại chỉ ghi nhận các đơn hàng từ ngày 01/01/2026 đến ngày 29/06/2026, do đó tháng 07/2026 chưa phát sinh giao dịch nào và doanh thu đạt 0VNĐ. 