# CODEBASE.md

## Architecture Overview
The jaffle_shop is a dbt project showing data modeling patterns.

## Critical Path (Top Modules by PageRank)
- customers.sql
- orders.sql

## Data Sources and Sinks
### Sources
- raw_customers
- raw_orders
- raw_payments
### Sinks
- customers
- orders

## Known Technical Debt
- Circular dependencies between staging models (detected)

