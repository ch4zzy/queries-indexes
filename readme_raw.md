
# Data examples

```python
start_date = "2023-07-06 07:28:04"
end_date = "2023-08-06 07:28:04"


def filter_data() -> json:
    filter_dict = {
        "unpaid": start_date
    }
    return json.dumps([filter_dict])

def filter_data_diapason() -> json:
    filter_dict = {
        "unpaid":{
            "$gte": start_date,
            "$lte": end_date
        }
    }
    return json.dumps(filter_dict)
```

# queries and sql raw

The difference between email and email__contains search

### email

```sql
[utils 2023-11-07 15:08:50,226 DEBUG] (0.009) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", "queries_order"."email", 
"queries_order"."address", "queries_order"."postal_code", "queries_order"."city", "queries_order"."paid", 
"queries_order"."order_json", "queries_order"."status" 
FROM "queries_order" WHERE ("queries_order"."email" = 'hthj' AND "queries_order"."paid"); 
args=('hthj',); alias=default

"Index Scan using email_paid_idx_btree on queries_order 
(cost=0.42..16.48 rows=3 width=683) (actual time=1.612..1.613 rows=0 loops=1)\n  
Index Cond: ((email)::text = 'hthj'::text)\nPlanning Time: 0.166 ms\nExecution Time: 1.640 ms"
```

### email__contains and email__icontains

The query uses a parallel sequential scan, which can be less efficient compared to an index scan, 
especially when using the LIKE operator with a wildcard (%) in the filter condition. 
This can result in a longer execution time (Execution Time: 142.835 ms).

Query example: `Order.objects.filter(email__contains='gmail', paid=True)`

```sql
[utils 2023-11-07 15:11:57,110 DEBUG] (0.144) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", "queries_order"."email", 
"queries_order"."address", "queries_order"."postal_code", "queries_order"."city", "queries_order"."paid", 
"queries_order"."order_json", "queries_order"."status" 
FROM "queries_order" WHERE ("queries_order"."email"::text LIKE '%gmail%' AND "queries_order"."paid"); 
args=('%gmail%',); alias=default

"Gather  (cost=1000.00..96556.03 rows=67 width=683) (actual time=140.920..142.817 rows=0 loops=1)\n  
Workers Planned: 2\n  
Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  
(cost=0.00..95549.33 rows=28 width=683) (actual time=114.386..114.387 rows=0 loops=3)\n        
Filter: (paid AND ((email)::text ~~ '%gmail%'::text))\n        
Rows Removed by Filter: 333333\nPlanning Time: 0.089 ms\nExecution Time: 142.835 ms"
```

Query example: `Order.objects.filter(email__icontains='GMAIL', paid=True)`

This query also uses a parallel sequential scan, but it's case-insensitive due to the use of upper((email)::text). 
Again, it's less efficient than an index scan, resulting in a longer execution time (Execution Time: 177.080 ms).

```sql
[utils 2023-11-07 15:27:05,763 DEBUG] (0.179) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", "queries_order"."email", 
"queries_order"."address", "queries_order"."postal_code", "queries_order"."city", "queries_order"."paid", 
"queries_order"."order_json", "queries_order"."status" FROM "queries_order"
WHERE (UPPER("queries_order"."email"::text) LIKE UPPER('%GMAIL%') AND "queries_order"."paid"); 
args=('%GMAIL%',); alias=default

"Gather  (cost=1000.00..97698.30 rows=1073 width=683) (actual time=175.420..177.044 rows=0 loops=1)\n  
Workers Planned: 2\n  
Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  
(cost=0.00..96591.00 rows=447 width=683) (actual time=172.776..172.776 rows=0 loops=3)\n        
Filter: (paid AND (upper((email)::text) ~~ '%GMAIL%'::text))\n        
Rows Removed by Filter: 333333\nPlanning Time: 0.794 ms\nExecution Time: 177.080 ms"
```

In the provided code, the second and third queries utilize a parallel sequential scan **(Parallel Seq Scan)** rather than
an index scan. This occurs due to the specific nature of these queries and how the filtering conditions are structured.
In this query, the __contains condition is used, indicating a search for records where the "email" field contains the 
string "gmail." This condition is not an exact match and cannot be efficiently executed using an index. Consequently, 
Django resorts to a parallel sequential scan to examine all records. In this query, the **__icontains** condition is 
employed, indicating a search for records where the "email" field contains the string "gmail" without regard to case 
sensitivity. Similarly, this cannot be efficiently executed with an index due to the case insensitivity, leading Django 
to opt for a parallel sequential scan.

Indexed searches, as seen in the first query, are effective when filtering records with exact values. 
However, for queries that involve operators like **LIKE**, icontains, or other conditions that cannot be precisely matched 
with an index, a parallel sequential scan may be employed, potentially resulting in increased query execution times.


### email__endswith

```sql
[utils 2023-11-07 20:11:48,148 DEBUG] (1.142) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", "queries_order"."email", 
"queries_order"."address", "queries_order"."postal_code", "queries_order"."city", "queries_order"."paid", 
"queries_order"."order_json", "queries_order"."status" 
FROM "queries_order" WHERE ("queries_order"."email"::text LIKE '%gmail.com' AND "queries_order"."paid"); 
args=('%gmail.com',); alias=default

"Gather  (cost=1000.00..96556.03 rows=67 width=683) (actual time=1131.484..1132.576 rows=0 loops=1)\n  
Workers Planned: 2\n  
Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  
(cost=0.00..95549.33 rows=28 width=683) (actual time=1127.323..1127.323 rows=0 loops=3)\n        
Filter: (paid AND ((email)::text ~~ '%gmail.com'::text))\n        
Rows Removed by Filter: 333333\nPlanning Time: 6.570 ms\nExecution Time: 1132.703 ms"
```

Here, the query uses a parallel sequential scan, which can be less efficient compared to an index scan,
lets try GIN index for email field, and compare the results.

When you trying to create GIN index for email field, you will get an error like this:

`django.db.utils.ProgrammingError: operator class "gin_trgm_ops" does not exist for access method "gin"`

The reason is that the GIN index is not supported by the default PostgreSQL installation.
You should install the pg_trgm extension to use GIN index for not 
[built-in](https://www.postgresql.org/docs/current/gin-builtin-opclasses.html) operators.

[Django](https://docs.djangoproject.com/en/4.2/ref/contrib/postgres/indexes/) documentation about indexes and extensions.

[PostgreSQL](https://www.postgresql.org/docs/current/btree-gin.html) documentation about extensions.

Here is the 
[migration](https://github.com/ch4zzy/queries-indexes/blob/develop/apps/queries/migrations/0004_order_email_idx_gin.py), 
which will create the extension and index for email field:

index weight: 41mb

```
queries=# SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 927 MB
```

## Queries tests for email field with BTREE and GINondexes with condition `paid=True`

As a result, we can see how indexes are used with lookups and patterns can be traced:
  - btree used in: exact, in, isnull
  - gin used in: contains, endswith, regex, iregex, startswith
  - parallel seq scan used in: icontains, iendswith, iexact, istartswith

  In the last case, parallel seq scan is used because all of my records in email field are in lowercase.

### email__contains

```sql
[utils 2023-11-12 15:34:59,608 DEBUG] (0.018) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", "queries_order"."status" 
FROM "queries_order" 
WHERE 
("queries_order"."email"::text LIKE '%gmail%' AND "queries_order"."paid"); 
args=('%gmail%',); alias=default

"Bitmap Heap Scan on queries_order  (cost=44.52..307.88 rows=67 width=683) (actual time=2.347..2.348 rows=0 loops=1)\n  
Recheck Cond: (((email)::text ~~ '%gmail%'::text) 
AND paid)\n  ->  Bitmap Index Scan on email_idx_gin  (cost=0.00..44.50 rows=67 width=0) (actual time=2.343..2.344 rows=0 loops=1)\n        
Index Cond: ((email)::text ~~ '%gmail%'::text)\nPlanning Time: 11.146 ms\nExecution Time: 2.561 ms"
```

### email__icontains

```sql
[utils 2023-11-12 15:35:09,482 DEBUG] (1.557) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" 
FROM "queries_order" WHERE (UPPER("queries_order"."email"::text) LIKE UPPER('%GMAIL%') AND "queries_order"."paid"); 
args=('%GMAIL%',); alias=default

"Gather  (cost=1000.00..97698.30 rows=1073 width=683) (actual time=1551.262..1552.800 rows=0 loops=1)\n  
Workers Planned: 2\n  Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  
(cost=0.00..96591.00 rows=447 width=683) (actual time=1547.012..1547.013 rows=0 loops=3)\n        
Filter: (paid AND (upper((email)::text) ~~ '%GMAIL%'::text))\n        Rows Removed by Filter: 333333\n
Planning Time: 0.212 ms\nExecution Time: 1552.862 ms"
```

### email_endswith

```sql
[utils 2023-11-12 15:45:00,895 DEBUG] (0.037) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email"::text LIKE '%gmail.com' AND "queries_order"."paid"); 
args=('%gmail.com',); alias=default
"Bitmap Heap Scan on queries_order  (cost=108.52..371.88 rows=67 width=683) (actual time=21.876..21.878 rows=0 loops=1)\n  
Recheck Cond: (((email)::text ~~ '%gmail.com'::text) AND paid)\n  ->  Bitmap Index Scan on email_idx_gin  
(cost=0.00..108.50 rows=67 width=0) (actual time=21.874..21.875 rows=0 loops=1)\n        
Index Cond: ((email)::text ~~ '%gmail.com'::text)\nPlanning Time: 11.655 ms\nExecution Time: 22.038 ms"
```

### email_iendswith

```sql
[utils 2023-11-12 15:46:22,579 DEBUG] (0.984) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
(UPPER("queries_order"."email"::text) LIKE UPPER('%GMAIL.COM') AND "queries_order"."paid"); 
args=('%GMAIL.COM',); alias=default
"Gather  (cost=1000.00..97597.70 rows=67 width=683) (actual time=981.488..982.477 rows=0 loops=1)\n  
Workers Planned: 2\n  Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  
(cost=0.00..96591.00 rows=28 width=683) (actual time=975.973..975.973 rows=0 loops=3)\n        
Filter: (paid AND (upper((email)::text) ~~ '%GMAIL.COM'::text))\n        
Rows Removed by Filter: 333333\nPlanning Time: 0.175 ms\nExecution Time: 982.498 ms"
```

### email_exact

```sql
[utils 2023-11-12 15:46:36,173 DEBUG] (0.010) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email" = 'hartmankristina@example.com' AND "queries_order"."paid"); 
args=('hartmankristina@example.com',); alias=default
"Index Scan using email_paid_idx_btree on queries_order  (cost=0.42..16.48 rows=3 width=683) (actual time=1.869..1.871 rows=1 loops=1)\n  
Index Cond: ((email)::text = 'hartmankristina@example.com'::text)\nPlanning Time: 0.116 ms\nExecution Time: 1.885 ms"
```

### email_iexact

```sql
[utils 2023-11-12 15:47:06,231 DEBUG] (0.191) EXPLAIN (ANALYZE true) 
SELECT
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
(UPPER("queries_order"."email"::text) = UPPER('HARtmankristina@example.com') AND "queries_order"."paid"); 
args=('HARtmankristina@example.com',); alias=default
"Gather  (cost=1000.00..97926.40 rows=3354 width=683) (actual time=189.019..190.297 rows=1 loops=1)\n  
Workers Planned: 2\n  Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  (cost=0.00..96591.00 rows=1398 width=683) (actual time=186.844..186.846 rows=0 loops=3)\n        
Filter: (paid AND (upper((email)::text) = 'HARTMANKRISTINA@EXAMPLE.COM'::text))\n        
Rows Removed by Filter: 333333\nPlanning Time: 0.090 ms\nExecution Time: 190.322 ms"
```

### email_in

```sql
[utils 2023-11-12 15:47:22,697 DEBUG] (0.001) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email" IN ('hartmankristina@example.com') AND "queries_order"."paid"); 
args=('hartmankristina@example.com',); alias=default
"Index Scan using email_paid_idx_btree on queries_order  (cost=0.42..16.48 rows=3 width=683) (actual time=0.017..0.018 rows=1 loops=1)\n  
Index Cond: ((email)::text = 'hartmankristina@example.com'::text)\nPlanning Time: 0.118 ms\nExecution Time: 0.031 ms"
```

### email_isnull

```sql
'Index Scan using email_paid_idx_btree on queries_order  (cost=0.42..8.44 rows=1 width=683) (actual time=3.646..3.646 rows=0 loops=1)\n  
Index Cond: (email IS NULL)\nPlanning Time: 0.074 ms\nExecution Time: 3.665 ms'
[utils 2023-11-12 15:47:33,641 DEBUG] (0.005) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email" IS NULL AND "queries_order"."paid"); args=(); alias=default
```

### email_regex

```sql
[utils 2023-11-12 15:47:47,224 DEBUG] (0.784) EXPLAIN (ANALYZE true) 
SELECT "queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email"::text ~  E'^.*@.*\\.Com$' AND "queries_order"."paid"); args=('^.*@.*\\.Com$',); alias=default
"Bitmap Heap Scan on queries_order  (cost=28.52..291.88 rows=67 width=683) (actual time=778.884..778.885 rows=0 loops=1)\n  
Recheck Cond: (((email)::text ~ '^.*@.*\\.Com$'::text) AND paid)\n  Rows Removed by Index Recheck: 501925\n  Heap Blocks: exact=51546 lossy=33043\n  ->  
Bitmap Index Scan on email_idx_gin  (cost=0.00..28.50 rows=67 width=0) (actual time=47.166..47.166 rows=223003 loops=1)\n        
Index Cond: ((email)::text ~ '^.*@.*\\.Com$'::text)\nPlanning Time: 0.779 ms\nExecution Time: 779.031 ms"
```

### email_iregex

```sql
"Bitmap Heap Scan on queries_order  (cost=1649.58..101258.56 rows=176204 width=683) (actual time=82.727..810.075 rows=222908 loops=1)\n  
Recheck Cond: (((email)::text ~* '^.*@.*\\.cOm$'::text) AND paid)\n  Rows Removed by Index Recheck: 279017\n  
Heap Blocks: exact=51546 lossy=33043\n  ->  Bitmap Index Scan on email_idx_gin  (cost=0.00..1605.53 rows=176204 width=0) (actual time=42.387..42.388 rows=223003 loops=1)\n        
Index Cond: ((email)::text ~* '^.*@.*\\.cOm$'::text)\nPlanning Time: 1.406 ms\nJIT:\n  Functions: 2\n  Options: Inlining false, Optimization false, Expressions true, Deforming true\n  
Timing: Generation 0.316 ms, Inlining 0.000 ms, Optimization 8.227 ms, Emission 23.509 ms, Total 32.051 ms\nExecution Time: 953.086 ms"
[utils 2023-11-12 15:47:59,300 DEBUG] (0.961) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email"::text ~*  E'^.*@.*\\.cOm$' AND "queries_order"."paid"); args=('^.*@.*\\.cOm$',); alias=default
```

### email_startswith

```sql
[utils 2023-11-12 15:48:12,947 DEBUG] (0.029) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
("queries_order"."email"::text LIKE 'hartmankristina%' AND "queries_order"."paid"); args=('hartmankristina%',); alias=default
"Bitmap Heap Scan on queries_order  (cost=204.52..467.88 rows=67 width=683) (actual time=27.964..27.966 rows=1 loops=1)\n  
Recheck Cond: (((email)::text ~~ 'hartmankristina%'::text) AND paid)\n  Heap Blocks: exact=1\n  ->  
Bitmap Index Scan on email_idx_gin  (cost=0.00..204.50 rows=67 width=0) (actual time=27.955..27.956 rows=1 loops=1)\n        
Index Cond: ((email)::text ~~ 'hartmankristina%'::text)\nPlanning Time: 0.167 ms\nExecution Time: 27.992 ms"
```

### email_istartswith

```sql
[utils 2023-11-12 15:48:25,980 DEBUG] (0.218) EXPLAIN (ANALYZE true) 
SELECT 
"queries_order"."id", "queries_order"."first_name", "queries_order"."last_name", 
"queries_order"."email", "queries_order"."address", "queries_order"."postal_code", 
"queries_order"."city", "queries_order"."paid", "queries_order"."order_json", 
"queries_order"."status" FROM "queries_order" 
WHERE 
(UPPER("queries_order"."email"::text) LIKE UPPER('HARTMANKRISTINA%') AND "queries_order"."paid"); args=('HARTMANKRISTINA%',); alias=default
"Gather  (cost=1000.00..97926.40 rows=3354 width=683) (actual time=195.061..216.190 rows=1 loops=1)\n  Workers Planned: 2\n  
Workers Launched: 2\n  ->  Parallel Seq Scan on queries_order  (cost=0.00..96591.00 rows=1398 width=683) (actual time=160.883..160.884 rows=0 loops=3)\n        
Filter: (paid AND (upper((email)::text) ~~ 'HARTMANKRISTINA%'::text))\n        Rows Removed by Filter: 333333\nPlanning Time: 0.515 ms\nExecution Time: 216.220 ms"
```