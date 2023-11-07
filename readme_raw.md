
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

Query example: `Order.objects.filter(email__icontains='gmail', paid=True)`

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
