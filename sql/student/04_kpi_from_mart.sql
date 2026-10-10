-- KPI 1: Xu hướng doanh thu theo tháng (Monthly Revenue Trend)
select d.year, d.month, sum(f.revenue) as total_revenue, 
	   count(distinct f.order_id) as total_orders 
  from fact_sales as f 
  join dim_date as d on f.date_id = d.date_id  
 group by d.year, d.month 
 order by d.year, d.month; 

-- KPI 2: Top 10 khách hàng VIP mang lại doanh thu cao nhất (Top 10 Customers)
select c.customer_id, c.customer_name, c.city, 
	   sum(f.revenue) as total_spent 
  from fact_sales as f 
  join dim_customer as c on f.customer_id = c.customer_id 
 group by c.customer_id, c.customer_name, c.city 
 order by total_spent desc 
 limit 10; 

-- KPI 3: Hiệu suất doanh thu theo danh mục sản phẩm (Revenue by Product Category)
select p.category, sum(f.quantity) as total_units_sold, 
	   sum(f.revenue) as total_revenue 
  from fact_sales as f
  join dim_product as p on f.product_id = p.product_id
 group by p.category 
 order by total_revenue desc; 

-- KPI 4: Phân tích hành vi thanh toán của khách hàng
select pm.method_name, count(distinct f.order_id) as total_orders, 
	   sum(f.revenue) as total_revenue
  from fact_sales as f 
  join dim_payment_method as pm on f.payment_method_id = pm.payment_method_id 
 group by pm.method_name  
 order by total_revenue desc; 

-- KPI 5: Tỷ lệ và giá trị theo trạng thái đơn hàng
select os.status_name, count(distinct f.order_id) as order_count, 
	   sum(f.revenue) as total_revenue 
  from fact_sales as f 
  join dim_order_status as os on f.order_status_id = os.order_status_id 
 group by os.status_name  
 order by order_count desc; 