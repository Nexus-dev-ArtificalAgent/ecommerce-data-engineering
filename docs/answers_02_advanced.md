-- ====================================================================
-- Câu 2.1: Advanced Analytics - Doanh thu cộng dồn theo thời gian
-- Mục tiêu: Tính tổng doanh thu từng tháng và doanh thu tích lũy (Cumulative Revenue)
-- Kỹ thuật sử dụng: CTE + to_char() + Window Function SUM() OVER()
-- ====================================================================
set search_path to core, public;
-- Bước 1: Dùng CTE gom nhóm doanh thu theo từng tháng (YYYY-MM)
with monthly_revenue as ( 
	select to_char(order_date, 'YYYY-MM') as order_month, 
		   sum(order_total) as monthly_revenue 
	  from orders 
	 group by to_char(order_date, 'YYYY-MM') 
)
-- Bước 2: Dùng Window Function để tính tổng cộng dồn qua từng tháng
select order_month, monthly_revenue, 
	   sum(monthly_revenue) over (
	   					   order by order_month) as cumulative_revenue 
  from monthly_revenue 
 order by order_month; 

 -- -------------------------------------------------------------------
-- Yêu cầu 2: Tỷ trọng doanh thu từng category
-- Kỹ thuật: JOIN 4 bảng + Window Function SUM() OVER()
-- Ý nghĩa: Tính tổng doanh thu của từng ngành hàng và % đóng góp trên tổng doanh thu sàn.
-- --------------------------------------------------------------------
with category_revenue as (
    select 
        c.category_id,
        c.category_name,
        sum(o.order_total) as revenue
    from categories c
    join products p on c.category_id = p.category_id
    join order_items oi on p.product_id = oi.product_id
    join orders o on oi.order_id = o.order_id
    group by c.category_id, c.category_name
)
select 
    category_id,
    category_name,
    revenue,
    round((revenue / sum(revenue) over () * 100)::numeric, 2) as revenue_percentage
from category_revenue
order by revenue desc;

-- --------------------------------------------------------------------
-- Yêu cầu 3: Tìm customers "churn" (không có order trong 30 ngày qua so với MAX(order_date))
-- Kỹ thuật: CTE + Subquery MAX date + CROSS JOIN + Interval filtering
-- Ý nghĩa: xác định mốc thời gian mới nhất trong hệ thống và lọc ra khách hàng đã ngưng mua > 30 ngày.
-- --------------------------------------------------------------------
with max_date as (
    select max(order_date) as max_order_date from orders
),
customer_last_order as (
    select 
        c.customer_id,
        c.full_name,
        max(o.order_date) as last_order_date
    from customers c
    join orders o on c.customer_id = o.customer_id
    group by c.customer_id, c.full_name
)
select 
    clo.customer_id,
    clo.full_name,
    clo.last_order_date,
    md.max_order_date,
    (md.max_order_date::date - clo.last_order_date::date) as days_since_last_order
from customer_last_order clo
cross join max_date md
where clo.last_order_date < md.max_order_date - interval '30 days'
order by last_order_date desc;