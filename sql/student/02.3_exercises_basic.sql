set search_path to core, public;
select o.order_id, o.order_total, 
	   sum(oi.quantity * oi.unit_price) as items_total, 
	   (sum(oi.quantity * oi.unit_price) - o.order_total) as difference 
  from orders as o 
  join order_items as oi on o.order_id = oi.order_id 
 group by o.order_id, o.order_total  
 order by o.order_id; 