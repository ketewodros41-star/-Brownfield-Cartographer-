# CODEBASE.md

> **Generated:** 2026-03-14T12:46:09.179792  
> **Mode:** automated static + LLM analysis

## Architecture Overview
*confidence: **high***

Automated architecture summary derived from static analysis and lineage graph.

## Critical Path (Top Modules by PageRank)
*5 item(s) - confidence: **high***

- .pre-commit-config.yaml (evidence: .pre-commit-config.yaml:1-14, method: static)
- dbt_project.yml (evidence: dbt_project.yml:1-38, method: static)
- package-lock.yml (evidence: package-lock.yml:1-8, method: static)
- packages.yml (evidence: packages.yml:1-7, method: static)
- Taskfile.yml (evidence: Taskfile.yml:1-40, method: static)

## Data Sources & Sinks

### Sources - *11 item(s) - confidence: **high***

- analytics.orders (evidence: fixtures\lineage_example.sql:1-9, method: static)
- analytics.customers (evidence: fixtures\lineage_example.sql:1-9, method: static)
- data/orders.csv (evidence: fixtures\pipeline.py:6-6, method: static)
- raw.payments (evidence: fixtures\schema.yml:1-1, method: static)
- raw.customers (evidence: fixtures\schema.yml:1-1, method: static)
- raw_customers (evidence: models\staging\stg_customers.sql:1-23, method: static)
- raw_stores (evidence: models\staging\stg_locations.sql:1-29, method: static)
- raw_orders (evidence: models\staging\stg_orders.sql:1-33, method: static)
- raw_items (evidence: models\staging\stg_order_items.sql:1-22, method: static)
- raw_products (evidence: models\staging\stg_products.sql:1-34, method: static)
- raw_supplies (evidence: models\staging\stg_supplies.sql:1-31, method: static)

### Sinks - *10 item(s) - confidence: **high***

- data/orders_out.csv (evidence: fixtures\pipeline.py:12-12, method: static)
- data/orders.parquet (evidence: fixtures\pipeline.py:7-7, method: static)
- fct_payments (evidence: fixtures\schema.yml:1-1, method: static)
- cents_to_dollars (evidence: macros\cents_to_dollars.sql:1-21, method: static)
- generate_schema_name (evidence: macros\generate_schema_name.sql:1-23, method: static)
- customers (evidence: models\marts\customers.sql:1-58, method: static)
- locations (evidence: models\marts\locations.sql:1-9, method: static)
- metricflow_time_spine (evidence: models\marts\metricflow_time_spine.sql:1-19, method: static)
- products (evidence: models\marts\products.sql:1-9, method: static)
- supplies (evidence: models\marts\supplies.sql:1-9, method: static)

## Known Technical Debt
*41 item(s) - confidence: **high***

- Dead code candidate: .pre-commit-config.yaml (evidence: .pre-commit-config.yaml:1-14, method: static)
- Dead code candidate: dbt_project.yml (evidence: dbt_project.yml:1-38, method: static)
- Dead code candidate: package-lock.yml (evidence: package-lock.yml:1-8, method: static)
- Dead code candidate: packages.yml (evidence: packages.yml:1-7, method: static)
- Dead code candidate: Taskfile.yml (evidence: Taskfile.yml:1-40, method: static)
- Dead code candidate: .github\workflows\cd_prod.yml (evidence: .github\workflows\cd_prod.yml:1-79, method: static)
- Dead code candidate: .github\workflows\cd_staging.yml (evidence: .github\workflows\cd_staging.yml:1-79, method: static)
- Dead code candidate: .github\workflows\ci.yml (evidence: .github\workflows\ci.yml:1-81, method: static)
- Dead code candidate: .github\workflows\scripts\dbt_cloud_run_job.py (evidence: .github\workflows\scripts\dbt_cloud_run_job.py:1-134, method: static)
- Dead code candidate: fixtures\airflow_dag.py (evidence: fixtures\airflow_dag.py:1-10, method: static)
- Dead code candidate: fixtures\lineage_example.sql (evidence: fixtures\lineage_example.sql:1-9, method: static)
- Dead code candidate: fixtures\pipeline.py (evidence: fixtures\pipeline.py:1-12, method: static)
- Dead code candidate: fixtures\schema.yml (evidence: fixtures\schema.yml:1-18, method: static)
- Dead code candidate: macros\cents_to_dollars.sql (evidence: macros\cents_to_dollars.sql:1-21, method: static)
- Dead code candidate: macros\generate_schema_name.sql (evidence: macros\generate_schema_name.sql:1-23, method: static)
- Dead code candidate: models\marts\customers.sql (evidence: models\marts\customers.sql:1-58, method: static)
- Dead code candidate: models\marts\customers.yml (evidence: models\marts\customers.yml:1-107, method: static)
- Dead code candidate: models\marts\locations.sql (evidence: models\marts\locations.sql:1-9, method: static)
- Dead code candidate: models\marts\locations.yml (evidence: models\marts\locations.yml:1-24, method: static)
- Dead code candidate: models\marts\metricflow_time_spine.sql (evidence: models\marts\metricflow_time_spine.sql:1-19, method: static)
- Dead code candidate: models\marts\orders.sql (evidence: models\marts\orders.sql:1-77, method: static)
- Dead code candidate: models\marts\orders.yml (evidence: models\marts\orders.yml:1-183, method: static)
- Dead code candidate: models\marts\order_items.sql (evidence: models\marts\order_items.sql:1-66, method: static)
- Dead code candidate: models\marts\order_items.yml (evidence: models\marts\order_items.yml:1-181, method: static)
- Dead code candidate: models\marts\products.sql (evidence: models\marts\products.sql:1-9, method: static)
- Dead code candidate: models\marts\products.yml (evidence: models\marts\products.yml:1-26, method: static)
- Dead code candidate: models\marts\supplies.sql (evidence: models\marts\supplies.sql:1-9, method: static)
- Dead code candidate: models\marts\supplies.yml (evidence: models\marts\supplies.yml:1-24, method: static)
- Dead code candidate: models\staging\stg_customers.sql (evidence: models\staging\stg_customers.sql:1-23, method: static)
- Dead code candidate: models\staging\stg_customers.yml (evidence: models\staging\stg_customers.yml:1-9, method: static)
- Dead code candidate: models\staging\stg_locations.sql (evidence: models\staging\stg_locations.sql:1-29, method: static)
- Dead code candidate: models\staging\stg_locations.yml (evidence: models\staging\stg_locations.yml:1-43, method: static)
- Dead code candidate: models\staging\stg_orders.sql (evidence: models\staging\stg_orders.sql:1-33, method: static)
- Dead code candidate: models\staging\stg_orders.yml (evidence: models\staging\stg_orders.yml:1-12, method: static)
- Dead code candidate: models\staging\stg_order_items.sql (evidence: models\staging\stg_order_items.sql:1-22, method: static)
- Dead code candidate: models\staging\stg_order_items.yml (evidence: models\staging\stg_order_items.yml:1-16, method: static)
- Dead code candidate: models\staging\stg_products.sql (evidence: models\staging\stg_products.sql:1-34, method: static)
- Dead code candidate: models\staging\stg_products.yml (evidence: models\staging\stg_products.yml:1-9, method: static)
- Dead code candidate: models\staging\stg_supplies.sql (evidence: models\staging\stg_supplies.sql:1-31, method: static)
- Dead code candidate: models\staging\stg_supplies.yml (evidence: models\staging\stg_supplies.yml:1-12, method: static)
- Dead code candidate: models\staging\__sources.yml (evidence: models\staging\__sources.yml:1-20, method: static)

## High-Velocity Files
*0 item(s) - confidence: **low***

_No data available._

## Module Purpose Index
*41 item(s) - confidence: **high***

- .pre-commit-config.yaml - This module configures pre-commit hooks for code quality enforcement and formatting. It validates YAML files, fixes common text file issues like trailing whitespace and missing end-of-file newlines, ensures proper requirements.txt formatting, and applies Python code linting and formatting using Ruff. The purpose is to automate code quality checks and maintain consistent code style before commits are made. [None] (evidence: .pre-commit-config.yaml:1-14, method: static)
- dbt_project.yml - This dbt project configuration defines a data transformation pipeline for a jaffle shop business, organizing data models into staging views and mart tables. The configuration specifies file paths, project metadata, and deployment settings needed to build and deploy the analytics models. It also includes conditional seeding of raw data based on configuration variables and sets timezone preferences for date operations. [None] (evidence: dbt_project.yml:1-38, method: static)
- package-lock.yml - This module is a dbt project configuration file that manages dependencies for data transformation utilities, date handling, and audit functionality. It pulls in pre-built packages from dbt-labs for common utility functions and audit capabilities, along with a specialized date package from godatadriven. The configuration enables standardized data modeling practices by leveraging established dbt community packages rather than custom implementations. [None] (evidence: package-lock.yml:1-8, method: static)
- packages.yml - This module defines a set of dbt package dependencies for data transformation and analytics workflows. It includes utility functions for common dbt operations, date-related transformations, and audit helper tools for tracking changes in dimensional models. The configuration specifies exact versions for stability and references a git repository for the latest audit functionality. [None] (evidence: packages.yml:1-7, method: static)
- Taskfile.yml - This module is a data engineering workflow that generates synthetic e-commerce data and loads it into BigQuery for analytics purposes. It automates the process of creating sample datasets spanning multiple years, then transforms and seeds this data into a cloud data warehouse for business intelligence and reporting use cases. The workflow handles environment setup, data generation, and database loading through a series of orchestrated tasks. [None] (evidence: Taskfile.yml:1-40, method: static)
- .github\workflows\cd_prod.yml - This module automates the deployment of dbt jobs to production environments across multiple data warehouses (Snowflake, BigQuery, and Postgres) using GitHub Actions. It triggers dbt Cloud jobs when changes are pushed to the main branch, ensuring that data transformations and analytics workflows are updated in sync with code changes. The workflow authenticates with dbt Cloud using API keys and executes predefined jobs for each supported database platform. [None] (evidence: .github\workflows\cd_prod.yml:1-79, method: static)
- .github\workflows\cd_staging.yml - This module automates the deployment of dbt models to staging environments across multiple data warehouses (Snowflake, BigQuery, and Postgres) whenever changes are pushed to the `staging` branch. It triggers separate jobs for each warehouse, using dbt Cloud's API to run predefined jobs configured for each environment. The workflow ensures consistent and automated testing of dbt models in a staging environment before promoting changes to production. [None] (evidence: .github\workflows\cd_staging.yml:1-79, method: static)
- .github\workflows\ci.yml - This module automates continuous integration for dbt Cloud by triggering separate jobs for Snowflake, BigQuery, and Postgres environments when pull requests are opened against the main or staging branches. It sets up the necessary environment variables and runs a Python script to execute the dbt Cloud jobs with branch-specific schema overrides. The purpose is to validate database changes across multiple platforms before merging code into production. [None] (evidence: .github\workflows\ci.yml:1-81, method: static)
- .github\workflows\scripts\dbt_cloud_run_job.py - This module automates the execution and monitoring of dbt jobs through the dbt Cloud API. It triggers a specified job with configurable parameters like branch and schema override, then continuously polls the job's status until completion. The module handles authentication via API keys and provides real-time feedback on job progress through console output and status links. [None] (evidence: .github\workflows\scripts\dbt_cloud_run_job.py:1-134, method: static)
- fixtures\airflow_dag.py - This module defines an Apache Airflow DAG (Directed Acyclic Graph) that orchestrates a simple ETL (Extract, Transform, Load) data processing workflow. The DAG is scheduled to run daily and executes three sequential tasks: extracting data, transforming it, and then loading it to its final destination. The workflow follows a linear dependency pattern where each step must complete successfully before the next one begins. [None] (evidence: fixtures\airflow_dag.py:1-10, method: static)
- fixtures\lineage_example.sql - This module processes and transforms order data by filtering recent orders from the analytics schema. It creates a new table containing orders from 2024 onwards, joining order information with customer data to provide a comprehensive view of recent customer activity. The purpose is to generate a curated dataset of current orders for analytical reporting and business intelligence purposes. [None] (evidence: fixtures\lineage_example.sql:1-9, method: static)
- fixtures\pipeline.py - This module processes order data by reading it from a CSV file, converting it to Parquet format for efficient storage, and then querying it through a SQLite database engine. The results of the database query are then exported back to a CSV file. Essentially, it transforms and moves order data between different file formats and a database system. [None] (evidence: fixtures\pipeline.py:1-12, method: static)
- fixtures\schema.yml - This module defines a data model configuration that combines payment and customer data from raw sources into a fact table structure. The configuration specifies dependencies between raw data tables and the resulting fact table, establishing the foundational data relationships needed for analytics and reporting. The module essentially orchestrates the data flow and structure for payment-related business intelligence. [None] (evidence: fixtures\schema.yml:1-18, method: static)
- macros\cents_to_dollars.sql - This module provides a standardized way to convert cent values to dollar amounts across different database platforms. It defines a macro that automatically dispatches to the appropriate database-specific implementation for converting integer cent values to decimal dollar representations. The module ensures consistent monetary value formatting regardless of the underlying database system being used. [None] (evidence: macros\cents_to_dollars.sql:1-21, method: static)
- macros\generate_schema_name.sql - This module defines a macro that determines database schema names for different types of database objects (seeds, models, etc.) based on the deployment environment and custom naming rules. It routes seed data to a dedicated "raw" schema, uses the default target schema when no custom schema is specified, and applies environment-specific naming conventions by prepending the default schema name in production environments. The macro ensures proper schema organization and isolation across different deployment targets while maintaining consistent naming patterns. [None] (evidence: macros\generate_schema_name.sql:1-23, method: static)
- models\marts\customers.sql - This module creates a comprehensive customer analytics dataset by combining customer information with their order history and spending patterns. It calculates key customer lifetime metrics including total orders, first and last purchase dates, and lifetime spending amounts. The module also segments customers into "new" or "returning" categories based on their purchase behavior. [None] (evidence: models\marts\customers.sql:1-58, method: static)
- models\marts\customers.yml - This module defines a data model for analyzing customer behavior, focusing on lifetime spending, order history, and customer segmentation. It includes definitions for customer-level metrics such as total orders, first and last order dates, and tax-inclusive spending, along with derived metrics like average order value. The structure supports reporting and analysis by enabling aggregation and grouping of customer data through semantic models and saved queries. [None] (evidence: models\marts\customers.yml:1-107, method: static)
- models\marts\locations.sql - This module retrieves and processes location data from a staging table. It serves as a data transformation layer that prepares location information for downstream consumption, likely filtering or enriching the raw location records before they are used in reports or other business applications. The module essentially acts as an intermediary step in the location data pipeline. [None] (evidence: models\marts\locations.sql:1-9, method: static)
- models\marts\locations.yml - This module defines a semantic model for location data, serving as a dimension table that provides contextual information about business locations. It enables analysis by location through key attributes like location name, opening date, and average tax rates. The model supports time-based aggregation and filtering capabilities for location-related metrics. [None] (evidence: models\marts\locations.yml:1-24, method: static)
- models\marts\metricflow_time_spine.sql - This module generates a time spine table containing a continuous sequence of dates. It creates a dataset with one row per day over a 10-year period (3650 days) starting from a base date, which is typically used for time-series analysis and date-based joins in data warehouses. The final output provides a clean date dimension table with properly cast date values. [None] (evidence: models\marts\metricflow_time_spine.sql:1-19, method: static)
- models\marts\orders.sql - This module aggregates order data with detailed item-level information to create a comprehensive view of customer orders. It calculates order totals, counts of food and drink items, and determines whether each order contains food or drinks. The final output includes all order details along with customer-specific ordering sequence information. [None] (evidence: models\marts\orders.sql:1-77, method: static)
- models\marts\orders.yml - This module defines a data model and analytics framework for analyzing order data, including key metrics like order totals, food/drink item breakdowns, and customer ordering behavior. It supports reporting on order volume, revenue, and trends by organizing data into semantic models and precomputed metrics. The structure enables downstream analytics and reporting on business performance related to customer orders. [None] (evidence: models\marts\orders.yml:1-183, method: static)
- models\marts\order_items.sql - This module creates a comprehensive view of order data by joining together order items, orders, products, and supply cost information. It aggregates supply costs by product and combines all relevant order details with product information and supply chain costs. The result provides a complete dataset for analyzing order profitability and product performance. [None] (evidence: models\marts\order_items.sql:1-66, method: static)
- models\marts\order_items.yml - This module defines a data model for order items, including their relationships to orders and products, along with associated costs and revenue calculations. It includes unit tests to validate supply cost aggregation and semantic models that enable detailed analysis of order item performance by category (food/drink) and time. The module also specifies various metrics for tracking financial performance, such as revenue breakdowns, gross profit, and cumulative totals, supporting both simple and complex analytical queries. [None] (evidence: models\marts\order_items.yml:1-181, method: static)
- models\marts\products.sql - This module retrieves and presents product data from a staging table containing product information. It serves as a data access layer that provides a complete view of all available products in the system. The module is designed to support downstream reporting and analysis by making product data easily queryable. [None] (evidence: models\marts\products.sql:1-9, method: static)
- models\marts\products.yml - This module defines a semantic model for product data, establishing the structural foundation for how product-related information will be organized and accessed. The model creates a standardized representation of product dimensions and attributes that can be used consistently across different analytical queries and reporting needs. It serves as a central reference point for product master data, enabling unified access to product characteristics like type, description, pricing, and classification flags. [None] (evidence: models\marts\products.yml:1-26, method: static)
- models\marts\supplies.sql - This module transforms and stages supply chain data by selecting all records from a supplies staging table. It serves as a foundational layer in the data pipeline that prepares raw supply information for further analysis and reporting. The module essentially acts as a pass-through transformation that makes supply chain data available for downstream consumption. [None] (evidence: models\marts\supplies.sql:1-9, method: static)
- models\marts\supplies.yml - This module defines a semantic model for supplies data, representing a dimension table with detailed supply and product information. It provides structured metadata about supplies including identifiers, costs, and perishability status to support analytical querying and reporting. The model enables users to analyze supply-related metrics by various categorical dimensions such as supply type, product association, and cost factors. [None] (evidence: models\marts\supplies.yml:1-24, method: static)
- models\staging\stg_customers.sql - This module transforms raw customer data from an e-commerce source by renaming and selecting specific fields. It extracts customer records and maps the original 'id' field to 'customer_id' and the 'name' field to 'customer_name'. The purpose is to standardize customer data format and column naming conventions for downstream use. [None] (evidence: models\staging\stg_customers.sql:1-23, method: static)
- models\staging\stg_customers.yml - This module defines a staging model for customer data that includes basic data cleaning and transformation rules. The model ensures each customer record has a unique identifier and maintains data quality through validation tests for non-null and unique constraints on the customer ID field. [None] (evidence: models\staging\stg_customers.yml:1-9, method: static)
- models\staging\stg_locations.sql - This module transforms raw store data from an e-commerce system by renaming and formatting key fields. It extracts store identifiers, names, tax rates, and opening dates while standardizing the date format to daily granularity. The purpose is to create a cleaned and structured view of store location information for downstream reporting and analysis. [None] (evidence: models\staging\stg_locations.sql:1-29, method: static)
- models\staging\stg_locations.yml - This module processes and cleans raw store location data, transforming it into a standardized format with one row per location. It extracts and truncates timestamp information to dates, and applies basic data cleaning operations like renaming columns and filtering for open locations. The resulting dataset serves as a reliable source of location information for downstream analytics and reporting. [None] (evidence: models\staging\stg_locations.yml:1-43, method: static)
- models\staging\stg_orders.sql - This module transforms raw order data from an e-commerce system by renaming columns, converting currency amounts from cents to dollars, and standardizing timestamp formats. It processes order records to create a cleaned and formatted dataset that includes order identifiers, financial amounts, and date information. The transformed data provides a consistent format for order analysis and reporting purposes. [None] (evidence: models\staging\stg_orders.sql:1-33, method: static)
- models\staging\stg_orders.yml - This module defines a staging model for order data that includes basic data validation and transformation rules. The model ensures data quality by validating that the order total equals the sum of subtotal and tax paid, while also enforcing uniqueness and non-null constraints on order identifiers. This serves as a cleaned, standardized representation of order records for downstream analytics and reporting purposes. [None] (evidence: models\staging\stg_orders.yml:1-12, method: static)
- models\staging\stg_order_items.sql - This module transforms raw e-commerce item data by renaming and selecting specific fields. It extracts order item identifiers, order IDs, and product SKUs from the source table to create a standardized dataset for downstream processing. [None] (evidence: models\staging\stg_order_items.sql:1-22, method: static)
- models\staging\stg_order_items.yml - This module defines a staging table for order items that represents individual food and drink items within customer orders. It establishes the relationship between specific order items and their corresponding orders through foreign key references. The model ensures data integrity by requiring unique identifiers for each order item and maintaining referential integrity with the orders table. [None] (evidence: models\staging\stg_order_items.yml:1-16, method: static)
- models\staging\stg_products.sql - This module transforms raw product data from an e-commerce source by renaming and reformatting fields to create a standardized product catalog. It converts price values from cents to dollars and adds boolean flags to categorize products as food or beverage items based on their type. The output provides cleaned and structured product information including IDs, names, descriptions, prices, and category classifications. [None] (evidence: models\staging\stg_products.sql:1-34, method: static)
- models\staging\stg_products.yml - This module defines a data model for staging product information, specifically food and drink items that can be ordered. The model includes a unique identifier for each product and applies basic data quality tests to ensure the product ID is both present and unique across all records. [None] (evidence: models\staging\stg_products.yml:1-9, method: static)
- models\staging\stg_supplies.sql - This module transforms raw supply data from an e-commerce system into a standardized format with properly renamed columns and calculated fields. It generates a unique supply identifier, converts cost values from cents to dollars, and maintains key supply information including perishability status. The output provides a clean, consistent view of supply inventory data for downstream analytics and reporting purposes. [None] (evidence: models\staging\stg_supplies.sql:1-31, method: static)
- models\staging\stg_supplies.yml - This module manages supply expense data by creating a structured representation of supply costs with unique identifiers for each cost entry. It tracks individual supply expenses where each row represents a specific cost instance for a supply, allowing for historical cost tracking when prices change. The model ensures data quality through unique identification and non-null constraints on the primary key. [None] (evidence: models\staging\stg_supplies.yml:1-12, method: static)
- models\staging\__sources.yml - This module defines the raw data sources and table structures for an e-commerce system, specifically organizing customer, order, item, store, product, and supply information. It establishes a data model that captures the complete lifecycle of e-commerce transactions from customer purchases through to product supply chains. The configuration enables data loading and processing workflows by specifying the relationships between different business entities and their corresponding data fields. [None] (evidence: models\staging\__sources.yml:1-20, method: static)

## Change Summary (vs. previous run)

| Section | Previous | Current | Delta |
|---|---|---|---|
| critical_modules | 5 | 5 | 0 |
| sources | 11 | 11 | 0 |
| sinks | 10 | 10 | 0 |
| tech_debt | 41 | 41 | 0 |
| high_velocity | 0 | 0 | 0 |
| module_purposes | 41 | 41 | 0 |
