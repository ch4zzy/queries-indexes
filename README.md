db size after 100k products without indexes: 
```
postgres=# SELECT pg_size_pretty(pg_database_size('queries'));
 pg_size_pretty
----------------
 48 MB
(1 row)
```