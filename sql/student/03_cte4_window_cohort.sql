set search_path to core, public;
with customer_metrics as (
	select customer_id, sum(order_total) as total_spending, 
		   count(order_id) as order_count 
	  from orders 
	 group by customer_id
)
select customer_id, total_spending, order_count, 
	   round(total_spending/order_count, 2) as AOV 
  from customer_metrics; 
  