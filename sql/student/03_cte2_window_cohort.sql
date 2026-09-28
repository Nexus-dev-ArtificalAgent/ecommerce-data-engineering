set search_path to core, public;
with total_spending as (
	select o.customer_id, c.full_name, sum(o.order_total) as total_expenditure 
	  from orders as o 
	  join customers as c on o.customer_id = c.customer_id 
	 group by o.customer_id, c.full_name
)
select *, 
  case 
  	  when total_expenditure < 500 then 'Low' 
  	  when total_expenditure between 500 and 2000 then 'Medium'
  	  else 'High'
  end as spending_tier 
 from total_spending;
  