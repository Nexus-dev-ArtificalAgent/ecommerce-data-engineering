set search_path to core, public;
select customer_id, 
-- Recency: Tính số ngày từ lần mua cuối tới thời điểm chốt (dùng CURRENT_DATE hoặc ngày đơn cuối của hệ thống)
       current_date - max(order_date)::date as recent_days, 
-- Frequency: Tổng số đơn hàng đã mua 
       count(order_id) as frequency, 
-- Monetary: Tổng chi tiêu của khách hàng 
       sum(order_total) as monetary 
  from orders 
 group by customer_id 
 order by monetary desc;