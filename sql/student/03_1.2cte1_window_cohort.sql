set search_path to core, public;
with customer_spending as (
	select o.customer_id, c.full_name, 
		   sum(o.order_total) as total_spending 
	  from orders as o
	  join customers as c on o.customer_id = c.customer_id 
	 group by o.customer_id, c.full_name  
)
select customer_id, full_name, total_spending, 
	   row_number() over (order by total_spending DESC) as customer_rank 
  from customer_spending; 