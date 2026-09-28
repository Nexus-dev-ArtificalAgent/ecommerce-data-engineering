set search_path to core, public;
with total_spending as (
	select o.customer_id, c.full_name, sum(o.order_total) as total_expenditure 
	  from orders as o 
	  join customers as c on o.customer_id = c.customer_id 
	 group by o.customer_id, c.full_name
)
select * from total_spending 
 order by total_expenditure desc
 limit 10;