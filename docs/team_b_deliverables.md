# Team A → Team B Handoff

## Database Connection String
```
mssql+pyodbc://teama_app:Sup3rSecure!@localhost:1433/teama_supermarket?driver=ODBC+Driver+18+for+SQL+Server
```
- Uses SQL Server (local dev). Update host/user/pass for shared environments.
- Schema + seed scripts live under `db/`.

## Reference Artifacts
- ER diagram: `docs/er_diagram.png`
- Schema DDL: `db/schema.sql`
- Seed data: `db/seed_data.sql`
- ORM models + helpers: `orm/models.py`
- Sample queries: see below
- JSON join example: `docs/price_join_example.json`

## Sample Queries

### 1. Inventory overview
```sql
SELECT id, name, category
FROM Products
ORDER BY name;
```

### 2. All supermarkets
```sql
SELECT id, name, city
FROM Supermarkets
ORDER BY name;
```

### 3. Milk prices across stores (returns 3 rows)
```sql
SELECT p.name AS product,
       s.name AS store,
       s.city,
       pr.price
FROM Prices pr
JOIN Products p ON p.id = pr.product_id
JOIN Supermarkets s ON s.id = pr.store_id
WHERE p.name = 'milk'
ORDER BY s.name;
```

### 4. Full product × store price matrix
```sql
SELECT p.name AS product,
       s.name AS store,
       pr.price
FROM Prices pr
JOIN Products p ON p.id = pr.product_id
JOIN Supermarkets s ON s.id = pr.store_id
ORDER BY p.name, s.name;
```
Expected rows: `10 products × 3 stores = 30`.

### 5. Cheapest store per product (useful for API baseline)
```sql
SELECT product,
       FIRST_VALUE(store) OVER (PARTITION BY product ORDER BY price ASC, store ASC) AS cheapest_store,
       MIN(price) AS min_price
FROM (
    SELECT p.name AS product, s.name AS store, pr.price
    FROM Prices pr
    JOIN Products p ON p.id = pr.product_id
    JOIN Supermarkets s ON s.id = pr.store_id
) sub
GROUP BY product;
```

## JSON Example (price join)
See `docs/price_join_example.json` for the serialized result of query #4 filtered to `milk`/`eggs`. Team B can reuse the structure for contract tests.

## Validation Checklist
- `Products` table ≥ 10 rows (see tests in `tests/test_products.py`).
- `Supermarkets` table = 3 rows.
- Every `(product, store)` pair has a price ≥ 0.01.
- Joins + FK behavior covered by `tests/test_prices.py` & `tests/test_query_helpers.py`.

Ping Team A if additional columns or aggregates are needed.
