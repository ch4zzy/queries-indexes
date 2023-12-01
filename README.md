db size after 100k products without indexes: 
```
SELECT pg_size_pretty(pg_database_size('queries'));
postgres=# 
 pg_size_pretty
----------------
 48 MB
(1 row)
```

hash index on paid field

```
5 rows

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..1.05 rows=2 width=3169) (actual time=0.295..0.297 rows=3 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 2\nPlanning Time: 3.910 ms\nExecution Time: 0.333 ms'
```

```
50 rows 

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..5.25 rows=12 width=3169) (actual time=0.008..0.023 rows=28 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 22\nPlanning Time: 0.072 ms\nExecution Time: 0.035 ms'
```

```
100 rows 

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..9.90 rows=50 width=655) (actual time=0.007..0.036 rows=60 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 40\nPlanning Time: 0.254 ms\nExecution Time: 0.048 ms'
```

```
500 rows 

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..50.84 rows=322 width=685) (actual time=0.006..0.172 rows=338 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 162\nPlanning Time: 0.154 ms\nExecution Time: 0.194 ms'
```

```
1000 rows 

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..102.00 rows=676 width=687) (actual time=0.023..0.327 rows=672 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 328\nPlanning Time: 0.168 ms\nExecution Time: 0.359 ms'
```

```
50k rows

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..5016.00 rows=33460 width=683) (actual time=0.348..78.361 rows=33539 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 16461\nPlanning Time: 6.824 ms\nExecution Time: 79.494 ms'
```

```
70k rows 
The uniqueness of values in a column affects the performance of the index. 
In general, the more duplicates you have in a column, the worse the index performance. 
On the other hand, the more unique values you have, the better the performance of the index. 
In this case of low selectivity, we have True or False, with a ratio of 2/3 to 1/3.

postgres=# SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 100 MB
(1 row)

queries=# SELECT pg_size_pretty(pg_total_relation_size('queries_order'));
 pg_size_pretty
----------------
 52 MB
(1 row)

>>> Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..7022.76 rows=47339 width=683) (actual time=0.008..18.051 rows=46912 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 23088\nPlanning Time: 0.059 ms\nExecution Time: 19.375 ms'


>>> Order.objects.filter(paid=False).explain(analyze=True)
'Bitmap Heap Scan on queries_order  (cost=255.73..6805.10 rows=22637 width=683) (actual time=1.949..10.311 rows=23088 loops=1)\n  
Filter: (NOT paid)\n  Heap Blocks: exact=6238\n  ->  Bitmap Index Scan on paid_idx_btree  (cost=0.00..250.07 rows=22637 width=0) (actual time=1.164..1.164 rows=23088 loops=1)\n        
Index Cond: (paid = false)\nPlanning Time: 0.064 ms\nExecution Time: 11.023 ms'
```


### 1kk rows, we wee the index with low selectivity(btree on boolean field) is not used, we should try something else.

The db size: 

```
queries=# SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 788 MB
(1 row)
```

After index drop:

```
queries=# SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 782 MB
(1 row)
```

```
Order.objects.filter(paid=False).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..100339.22 rows=329075 width=683) (actual time=35.879..1486.696 rows=333443 loops=1)\n 
Filter: (NOT paid)\n  Rows Removed by Filter: 666557\nPlanning Time: 0.134 ms\nJIT:\n  
Functions: 2\n  Options: Inlining false, Optimization false, Expressions true, Deforming true\n  
Timing: Generation 0.360 ms, Inlining 0.000 ms, Optimization 6.306 ms, Emission 27.738 ms, Total 34.404 ms\n
Execution Time: 1628.116 ms'

Order.objects.filter(paid=True).explain(analyze=True)
'Seq Scan on queries_order  (cost=0.00..100339.22 rows=670747 width=683) (actual time=2.799..1355.710 rows=666557 loops=1)\n  
Filter: paid\n  Rows Removed by Filter: 333443\nPlanning Time: 0.152 ms\nJIT:\n  
Functions: 2\n  Options: Inlining false, Optimization false, Expressions true, Deforming true\n  
Timing: Generation 1.036 ms, Inlining 0.000 ms, Optimization 0.278 ms, Emission 1.862 ms, Total 3.176 ms\n
Execution Time: 1378.378 ms'
```

Let's try to use another index like btree for email field.
After the index creation db size is ~26mb:

```
queries=# SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 808 MB
(1 row)
```

Now our index is faster than latest version. 

```
BTreeIndex(fields=["email"], name="email_idx_btree",

Order.objects.filter(email='gtr').explain(analyze=True)
"Index Scan using email_idx_btree on queries_order  (cost=0.42..20.49 rows=4 width=683) (actual time=0.048..0.049 rows=0 loops=1)\n  
Index Cond: ((email)::text = 'gtr'::text)\nPlanning Time: 5.043 ms\nExecution Time: 0.499 ms"
```

We can make it even more productive and lighter in weight by adding condition by field paid.
Index size changed from 26mb to 19mb.
```
BTreeIndex(fields=["email"], name="email_paid_idx_btree", condition=models.Q(paid=True)),

SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 801 MB
(1 row)
``` 

``` 
>>> Order.objects.filter(email='hartmankristina@example.com', paid=True).explain(analyze=True)
"Index Scan using email_paid_idx_btree on queries_order  (cost=0.42..16.48 rows=3 width=683) (actual time=0.110..0.112 rows=1 loops=1)\n  
Index Cond: ((email)::text = 'hartmankristina@example.com'::text)\nPlanning Time: 0.196 ms\nExecution Time: 0.125 ms"
```

Now add GIN index for status field. 
It took 10-15 times longer to create the index compared to the previous ones.
Also, the index took up about 4-5 times more space than the previous one 85MB.

```
GinIndex(fields=["status"], name="status_idx_gin"),

queries=# SELECT pg_size_pretty(pg_database_size('queries'));
pg_size_pretty
----------------
 886 MB
(1 row)

```
```
filter_dict = {"unpaid": "2023-07-06 07:28:04"}
filter_json = json.dumps(filter_dict)
query = Order.objects.filter(status__contains=[filter_json])

[utils 2023-10-27 09:15:38,148 DEBUG] (0.002) EXPLAIN (ANALYZE true) SELECT "queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", "queries_order"."email", "queries_order"."address", "queries_order"."postal_code", "queries_order"."city", "queries_order"."paid", "queries_order"."order_json", "queries_order"."status" FROM "queries_order" WHERE "queries_order"."status" @> (ARRAY['{"unpaid": "2023-07-06 07:28:04"}'])::jsonb[]; args=('{"unpaid": "2023-07-06 07:28:04"}',); alias=default
'Bitmap Heap Scan on queries_order  (cost=20.26..150.78 rows=33 width=683) (actual time=0.021..0.022 rows=1 loops=1)\n  
Recheck Cond: (status @> \'{"{\\"unpaid\\": \\"2023-07-06 07:28:04\\"}"}\'::jsonb[])\n  
Heap Blocks: exact=1\n  ->  Bitmap Index Scan on status_idx_gin  (cost=0.00..20.25 rows=33 width=0) (actual time=0.016..0.016 rows=1 loops=1)\n        
Index Cond: (status @> \'{"{\\"unpaid\\": \\"2023-07-06 07:28:04\\"}"}\'::jsonb[])\n
Planning Time: 0.267 ms\nExecution Time: 0.041 ms'
```

## The final result is:
 - For btree and gin index (email field): [EMAIL](https://github.com/ch4zzy/queries-indexes/blob/main/readme_raw.md#queries-tests-for-status-field-with-gin-index)
 - For gin (status field): [STATUS](https://github.com/ch4zzy/queries-indexes/blob/main/readme_raw.md#queries-tests-for-status-field-with-gin-index)



