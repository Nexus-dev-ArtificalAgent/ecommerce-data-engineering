set search_path to core, public;
with first_order_cohort as (	
	select customer_id, date_trunc('month', MIN(order_date)) as cohort_month 
	  from orders 
	 group by customer_id
), 
	 customer_activities as ( 
	select distinct o.customer_id, f.cohort_month,
					date_trunc('month', o.order_date) as activity_month 
	  from orders as o 
	  join first_order_cohort as f on o.customer_id = f.customer_id 
)

select cohort_month, count(distinct customer_id) as total_customers, 
	   count(distinct case when activity_month > cohort_month then customer_id end) as retained_customers,
	   round(count(distinct case when activity_month > cohort_month then customer_id end)*100/count(distinct customer_id),
	   2) as retention_rate_pct
  from customer_activities 
 group by cohort_month
 order by cohort_month; 
