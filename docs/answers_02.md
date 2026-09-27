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

--------------------------------
## 2. Customer có tổng chi tiêu cao nhất
**Query SQL**
```sql
set search_path to core, public;
select c.customer_id, c.full_name,
	   sum(o.order_total) as total_expenditure 
  from customers as c
  join orders as o on c.customer_id = o.customer_id
 group by c.customer_id, c.full_name
 order by total_expenditure desc
 limit 10;
 ```

Đáp án: ID: CUS000575 | Tên: Jessica Marquez | Tổng chi tiêu: 209,701,000 VNĐ
Nhận xét: Jessica Marquez là khách hàng VIP đóng góp doanh thu cao nhất cho hệ thống trong toàn bộ giai đoạn ghi nhận dữ liệu, với tổng chi tiêu vượt mốc 200 triệu VNĐ.

--------------------------------
## 3. Category có số lượng orders cao nhất
**Query SQL:**
```sql 
set search_path to core, public;
select c.category_id, c.category_name, 
	   count(distinct oi.order_id) as total_orders 
  from categories as c 
  join products as p on c.category_id = p.category_id
  join order_items as oi on p.product_id = oi.product_id 
 group by c.category_id, c.category_name
 order by total_orders desc 
 limit 10;
 ```
 Đáp án:Category: Kitchen (ID: CAT009) | Số lượng đơn hàng: 1,046 đơn
 Nhận xét: Ngành hàng Kitchen (Dụng cụ nhà bếp) dẫn đầu về lượng đơn đặt hàng phát sinh trên hệ thống với 1,046 đơn, cho thấy đây là danh mục sản phẩm thu hút nhu cầu mua sắm cao nhất của người dùng. 

--------------------------------
 ## 4. Average order value (AOV)
**Query SQL:**
```sql
set search_path to core, public;
select avg(order_total) as average_order_value
from orders;
```

Đáp án: 12,341,286.4 VNĐ
Nhận xét: Chỉ số AOV đạt hơn 12.3 triệu VNĐ phản ánh sức mua cao của tệp khách hàng và định vị sản phẩm giá trị lớn của sàn. Đây là metric cơ sở để đánh giá hiệu quả của các chiến lược bán hàng cross-sell/up-sell và tính toán biên lợi nhuận trên chi phí thu hút khách hàng (CAC).

--------------------------------
## 5. Số lượng customers có hơn 3 orders 
**Query SQL:**
```sql
set search_path to core, public;
select count(*) as total_customers_over_3_orders
  from (
select customer_id from orders 
 group by customer_id 
having count(order_id) > 3
) as subquery; 
```
Đáp án: 719 khách hàng
Nhận xét: Có 719 khách hàng phát sinh hơn 3 đơn hàng. Đây là nhóm khách hàng trung thành (loyal customers) đóng vai trò duy trì dòng tiền và doanh thu ổn định cho nền tảng.