set search_path to core, public;
select order_id, order_date, order_total, 
 	   sum(order_total) over (order by order_date, order_id) as running_total_revenue 
  from orders; 
