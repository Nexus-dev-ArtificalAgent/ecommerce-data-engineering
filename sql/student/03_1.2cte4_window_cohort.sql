set search_path to core, public;
select order_id, customer_id, order_date, order_total, 
 	   lag(order_total) over (partition by customer_id order by order_date) as prev_order_total, 
 	   lead(order_total) over (partition by customer_id order by order_date) as next_order_total, 
 	   order_total - lag(order_total) over (partition by customer_id order by order_date) as diff_with_prev
  from orders; 
