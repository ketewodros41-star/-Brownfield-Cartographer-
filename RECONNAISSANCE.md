# RECONNAISSANCE.md - jaffle_shop

## Five FDE Day-One Questions

### 1. What is the primary data ingestion path?
The primary data ingestion path for this project is through **dbt seeds**. The repository contains three CSV files in the `seeds/` directory:
- `raw_customers.csv`
- `raw_orders.csv`
- `raw_payments.csv`
These are loaded into the data warehouse as base tables.

### 2. What are the 3–5 most critical output datasets or endpoints?
The most critical output models are:
1. `customers`: A dimensional model containing customer information and lifetime value calculations.
2. `orders`: A model aggregating order details and payment methods.

### 3. What is the blast radius if the most critical module fails?
The staging models in `models/staging/` (`stg_customers`, `stg_orders`, `stg_payments`) form the foundation.
- If `stg_orders` fails, both the `orders` and `customers` models will be broken or provide incomplete data, as they both rely on order history.
- If `stg_payments` fails, the `orders` model loses its payment method breakdown, and `customers` loses lifetime value calculations.

### 4. Where is business logic concentrated vs distributed?
- **Concentrated**: The complex aggregations and joins are in the terminal models `customers.sql` and `orders.sql`.
- **Distributed**: Light business logic (renaming, basic filtering) is distributed across the staging models in `models/staging/`.

### 5. What files changed most frequently in the last 90 days?
*(Based on git history analysis)*
Top changed files:
1. `models/customers.sql`
2. `models/orders.sql`
3. `models/schema.yml`
4. `models/staging/stg_payments.sql`

## Manual Exploration Challenges
- **Difficulty**: Identifying the exact database dialect wasn't immediately obvious without checking `profiles.yml` (which is usually local and not in the repo). However, the SQL syntax is generic enough for standard dialects.
- **Missing Context**: The repository lacks a `profiles.yml` example, which is required for dbt to run. The `dbt_project.yml` references `jaffle_shop` profile.
- **Lineage**: Visually tracing the lineage from `stg_payments` to `customers` requires reading multiple CTEs and `ref` calls, which becomes difficult as the model count grows.
