set search_path to core, public;
select order_id, customer_id, order_date, order_total, 
	   row_number() over (partition by customer_id order by order_date) as order_sequence 
  from orders; 