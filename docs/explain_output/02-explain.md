## BEFORE
Sort  (cost=262.45..263.29 rows=333 width=44) (actual time=3.152..3.177 rows=432 loops=1)
  Sort Key: (max(o.order_date)) DESC
  Sort Method: quicksort  Memory: 56kB
  ->  Nested Loop  (cost=220.99..248.50 rows=333 width=44) (actual time=2.563..2.852 rows=432 loops=1)
        Join Filter: ((max(o.order_date)) < (($0) - '30 days'::interval))
        Rows Removed by Join Filter: 562
        ->  Result  (cost=0.31..0.32 rows=1 width=8) (actual time=0.055..0.056 rows=1 loops=1)
              InitPlan 1 (returns $0)
                ->  Limit  (cost=0.28..0.31 rows=1 width=8) (actual time=0.051..0.052 rows=1 loops=1)
                      ->  Index Only Scan Backward using idx_orders_date on orders  (cost=0.28..151.78 rows=5000 width=8) (actual time=0.050..0.051 rows=1 loops=1)
                            Index Cond: (order_date IS NOT NULL)
                            Heap Fetches: 0
        ->  HashAggregate  (cost=220.68..230.68 rows=1000 width=32) (actual time=2.482..2.589 rows=994 loops=1)
              Group Key: c.customer_id
              Batches: 1  Memory Usage: 193kB
              ->  Hash Join  (cost=54.50..195.68 rows=5000 width=32) (actual time=0.849..1.758 rows=5000 loops=1)
                    Hash Cond: ((o.customer_id)::text = (c.customer_id)::text)
                    ->  Seq Scan on orders o  (cost=0.00..128.00 rows=5000 width=18) (actual time=0.005..0.227 rows=5000 loops=1)
                    ->  Hash  (cost=42.00..42.00 rows=1000 width=24) (actual time=0.830..0.831 rows=1000 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 63kB
                          ->  Seq Scan on customers c  (cost=0.00..42.00 rows=1000 width=24) (actual time=0.003..0.684 rows=1000 loops=1)
Planning Time: 0.855 ms
Execution Time: 3.480 ms

-------------------------------------------------------
## AFTER 
Sort  (cost=262.45..263.29 rows=333 width=44) (actual time=2.040..2.056 rows=432 loops=1)
  Sort Key: (max(o.order_date)) DESC
  Sort Method: quicksort  Memory: 56kB
  ->  Nested Loop  (cost=220.99..248.50 rows=333 width=44) (actual time=1.667..1.924 rows=432 loops=1)
        Join Filter: ((max(o.order_date)) < (($0) - '30 days'::interval))
        Rows Removed by Join Filter: 562
        ->  Result  (cost=0.31..0.32 rows=1 width=8) (actual time=0.034..0.035 rows=1 loops=1)
              InitPlan 1 (returns $0)
                ->  Limit  (cost=0.28..0.31 rows=1 width=8) (actual time=0.032..0.032 rows=1 loops=1)
                      ->  Index Only Scan Backward using idx_orders_order_date on orders  (cost=0.28..151.78 rows=5000 width=8) (actual time=0.031..0.031 rows=1 loops=1)
                            Index Cond: (order_date IS NOT NULL)
                            Heap Fetches: 0
        ->  HashAggregate  (cost=220.68..230.68 rows=1000 width=32) (actual time=1.614..1.741 rows=994 loops=1)
              Group Key: c.customer_id
              Batches: 1  Memory Usage: 193kB
              ->  Hash Join  (cost=54.50..195.68 rows=5000 width=32) (actual time=0.202..1.101 rows=5000 loops=1)
                    Hash Cond: ((o.customer_id)::text = (c.customer_id)::text)
                    ->  Seq Scan on orders o  (cost=0.00..128.00 rows=5000 width=18) (actual time=0.002..0.212 rows=5000 loops=1)
                    ->  Hash  (cost=42.00..42.00 rows=1000 width=24) (actual time=0.177..0.178 rows=1000 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 63kB
                          ->  Seq Scan on customers c  (cost=0.00..42.00 rows=1000 width=24) (actual time=0.003..0.082 rows=1000 loops=1)
Planning Time: 0.590 ms
Execution Time: 2.123 ms