set search_path to core, public;
EXPLAIN ANALYZE
with max_date as ( 
	select max(order_date) as max_order_date 
	  from orders 
),
	 customer_last_order as (
	select c.customer_id, c.full_name, 
		   max(o.order_date) as last_order_date
	  from customers as c
	  join orders as o on c.customer_id = o.customer_id 
	 group by c.customer_id, c.full_name
) 

select clo.customer_id, clo.full_name, clo.last_order_date,
	   md.max_order_date, 
	   (md.max_order_date::date - clo.last_order_date::date) as days_since_last_order
  from customer_last_order as clo 
 cross join max_date as md 
 where clo.last_order_date < md.max_order_date - interval '30 days'
 order by last_order_date desc; 

create index if not exists idx_orders_customer_id on orders(customer_id); 
create index if not exists idx_orders_order_date on orders(order_date);
