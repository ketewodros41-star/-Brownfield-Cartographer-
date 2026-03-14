# CODEBASE.md

> **Generated:** 2026-03-13T17:14:53.494245  
> **Mode:** automated static + LLM analysis

## Architecture Overview
*confidence: **high***

Automated architecture summary derived from static analysis and lineage graph.

## Critical Path (Top Modules by PageRank)
*5 item(s) � confidence: **high***

- .pre-commit-config.yaml (evidence: .pre-commit-config.yaml:1-14, method: static)
- dbt_project.yml (evidence: dbt_project.yml:1-38, method: static)
- package-lock.yml (evidence: package-lock.yml:1-8, method: static)
- packages.yml (evidence: packages.yml:1-7, method: static)
- Taskfile.yml (evidence: Taskfile.yml:1-40, method: static)

## Data Sources & Sinks

### Sources � *9 item(s) � confidence: **high***

- macros\cents_to_dollars.sql::sql (evidence: macros\cents_to_dollars.sql:1-21, method: static)
- macros\generate_schema_name.sql::sql (evidence: macros\generate_schema_name.sql:1-23, method: static)
- models\marts\metricflow_time_spine.sql::sql (evidence: models\marts\metricflow_time_spine.sql:1-19, method: static)
- raw_customers (evidence: models\staging\stg_customers.sql:1-23, method: static)
- raw_stores (evidence: models\staging\stg_locations.sql:1-29, method: static)
- raw_orders (evidence: models\staging\stg_orders.sql:1-33, method: static)
- raw_items (evidence: models\staging\stg_order_items.sql:1-22, method: static)
- raw_products (evidence: models\staging\stg_products.sql:1-34, method: static)
- raw_supplies (evidence: models\staging\stg_supplies.sql:1-31, method: static)

### Sinks � *7 item(s) � confidence: **high***

- cents_to_dollars (evidence: macros\cents_to_dollars.sql:1-21, method: static)
- generate_schema_name (evidence: macros\generate_schema_name.sql:1-23, method: static)
- customers (evidence: models\marts\customers.sql:1-58, method: static)
- locations (evidence: models\marts\locations.sql:1-9, method: static)
- metricflow_time_spine (evidence: models\marts\metricflow_time_spine.sql:1-19, method: static)
- products (evidence: models\marts\products.sql:1-9, method: static)
- supplies (evidence: models\marts\supplies.sql:1-9, method: static)

## Known Technical Debt
*36 item(s) � confidence: **high***

- Dead code candidate: .pre-commit-config.yaml (evidence: .pre-commit-config.yaml:1-14, method: static)
- Dead code candidate: dbt_project.yml (evidence: dbt_project.yml:1-38, method: static)
- Dead code candidate: package-lock.yml (evidence: package-lock.yml:1-8, method: static)
- Dead code candidate: packages.yml (evidence: packages.yml:1-7, method: static)
- Dead code candidate: Taskfile.yml (evidence: Taskfile.yml:1-40, method: static)
- Dead code candidate: .github\workflows\cd_prod.yml (evidence: .github\workflows\cd_prod.yml:1-79, method: static)
- Dead code candidate: .github\workflows\cd_staging.yml (evidence: .github\workflows\cd_staging.yml:1-79, method: static)
- Dead code candidate: .github\workflows\ci.yml (evidence: .github\workflows\ci.yml:1-81, method: static)
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
*0 item(s) � confidence: **low***

_No data available._

## Module Purpose Index
*36 item(s) � confidence: **high***

- .pre-commit-config.yaml - This module configures pre-commit hooks for code quality assurance and formatting. It automatically validates YAML files, fixes whitespace issues, ensures proper file endings, and sorts requirements files. Additionally, it integrates Ruff for Python code linting and formatting with automatic fix capabilities. [None] (evidence: .pre-commit-config.yaml:1-14, method: static)
- dbt_project.yml - This module is a dbt project configuration for a jaffle shop analytics system that defines the project structure, database connection settings, and model materialization strategies. It organizes data transformation workflows by separating staging views from final mart tables, and includes seed data loading capabilities with conditional enablement. The configuration specifies file paths for different dbt components and sets timezone variables for date operations. [None] (evidence: dbt_project.yml:1-38, method: static)
- package-lock.yml - This module defines a set of external dependencies for a dbt project, including core utilities, date handling functions, and audit helper tools. It establishes the foundational components needed for data transformation, temporal logic, and data quality auditing within the dbt ecosystem. The configuration ensures consistent versions of these packages are used across the project for reliable and reproducible data workflows. [None] (evidence: package-lock.yml:1-8, method: static)
- packages.yml - This module defines a set of external dependencies for a dbt (data build tool) project, including utility functions, date dimension helpers, and audit tools. It imports pre-built packages from dbt-labs and godatadriven to extend core dbt functionality with additional macros, models, and testing capabilities. The configuration enables enhanced data transformation workflows by leveraging community-developed extensions for common data engineering tasks. [None] (evidence: packages.yml:1-7, method: static)
- Taskfile.yml - This module automates the setup and loading of synthetic e-commerce data for analytics purposes. It creates a Python virtual environment, installs required dependencies including dbt for data transformation, generates sample retail data using jafgen, and loads that data into a BigQuery database. The workflow is designed to bootstrap a complete data analytics environment with realistic test data for demonstration or development use cases. [None] (evidence: Taskfile.yml:1-40, method: static)
- .github\workflows\cd_prod.yml - This module automates the deployment of dbt models to production environments across multiple data warehouses (Snowflake, BigQuery, and Postgres) using GitHub Actions. It triggers dbt Cloud jobs when changes are pushed to the main branch, ensuring that updated models are built and deployed consistently. The workflow handles environment setup, dependency installation, and job execution for each supported database platform. [None] (evidence: .github\workflows\cd_prod.yml:1-79, method: static)
- .github\workflows\cd_staging.yml - This GitHub Actions workflow automatically deploys dbt models to staging environments across multiple data warehouses (Snowflake, BigQuery, and Postgres) when changes are pushed to the `staging` branch. It triggers separate dbt Cloud jobs for each warehouse using API calls authenticated via a shared secret key. The workflow ensures consistent deployment of analytics transformations in development environments prior to production release. [None] (evidence: .github\workflows\cd_staging.yml:1-79, method: static)
- .github\workflows\ci.yml - This module automates continuous integration for dbt Cloud by triggering separate CI jobs for Snowflake, BigQuery, and Postgres when pull requests are opened against the main or staging branches. It sets up the necessary environment variables and dependencies to run dbt jobs in each respective data warehouse environment using a shared Python script. [None] (evidence: .github\workflows\ci.yml:1-81, method: static)
- macros\cents_to_dollars.sql - This module provides a standardized macro for converting cent values to dollar amounts across different database platforms. It offers a consistent interface that automatically adapts the conversion logic based on the target database system, ensuring proper numeric precision and rounding behavior regardless of whether you're using PostgreSQL, BigQuery, SQL Server Fabric, or other supported databases. The macro handles the mathematical conversion (dividing by 100) while applying appropriate data type casting and precision settings for each specific database engine. [None] (evidence: macros\cents_to_dollars.sql:1-21, method: static)
- macros\generate_schema_name.sql - This module defines a macro that determines database schema names for different types of database objects (seeds, models, etc.) based on the deployment environment and custom naming rules. It routes seed data to a dedicated "raw" schema, applies custom schema names with environment-specific prefixes in production, and uses default schemas for non-production environments. The macro ensures proper data organization and isolation across different deployment contexts while maintaining consistent naming conventions. [None] (evidence: macros\generate_schema_name.sql:1-23, method: static)
- models\marts\customers.sql - This module creates a comprehensive customer analytics view by combining customer data with their order history and purchase behavior. It calculates key customer lifetime metrics including total orders, spending amounts, and purchase dates to determine whether each customer is new or returning. The resulting dataset provides a complete profile of customer purchasing patterns and value segmentation for business analysis and marketing purposes. [None] (evidence: models\marts\customers.sql:1-58, method: static)
- models\marts\customers.yml - This module creates a customer analytics data model that tracks and measures customer lifetime value and ordering behavior. It provides a comprehensive view of each customer's purchasing history, including total orders, spending amounts, and customer type classification. The module enables business users to analyze customer performance through pre-built metrics like lifetime spend, order counts, and average order value, supporting customer segmentation and retention strategies. [None] (evidence: models\marts\customers.yml:1-107, method: static)
- models\marts\locations.sql - This module retrieves and processes location data from a staging table containing location information. It serves as a data access layer that extracts location records from the raw staging source and makes them available for further analysis or reporting. The module provides a clean, standardized view of location data that can be consumed by other parts of the system. [None] (evidence: models\marts\locations.sql:1-9, method: static)
- models\marts\locations.yml - This module defines a semantic model for location data, establishing the business context and analytical structure for location-based information. It creates a dimensional table with location as the primary entity and includes key attributes like location name and opening date, along with calculated measures such as average tax rate. The model enables business users to analyze location performance and characteristics through standardized semantic definitions. [None] (evidence: models\marts\locations.yml:1-24, method: static)
- models\marts\metricflow_time_spine.sql - This module generates a time spine containing a continuous sequence of dates, spanning approximately 10 years (3650 days) starting from January 1, 2000. It creates a foundational date dimension table that can be used for time-based analysis, reporting, and joining with other datasets that require temporal context. The resulting dataset contains a single column with properly formatted date values covering this multi-year period. [None] (evidence: models\marts\metricflow_time_spine.sql:1-19, method: static)
- models\marts\orders.sql - This module creates a comprehensive order summary dataset by combining order information with detailed item-level analytics. It calculates order costs, subtotals, and categorizes orders by food and drink items while determining if each order contains food or drink items. The final output includes all order details along with customer-specific ordering sequence information based on chronological order placement. [None] (evidence: models\marts\orders.sql:1-77, method: static)
- models\marts\orders.yml - This module defines a data model and analytics framework for tracking and analyzing order data, including key metrics like order totals, customer ordering behavior, and item categorization (food vs. drink). It supports reporting on order volume, revenue, and customer acquisition by exposing structured datasets and precomputed metrics. The module also enables filtering and aggregation capabilities for business intelligence dashboards through semantic modeling and saved queries. [None] (evidence: models\marts\orders.yml:1-183, method: static)
- models\marts\order_items.sql - This module creates a comprehensive view of order data by joining together order items, orders, products, and supply cost information. It aggregates supply costs by product and combines all relevant order details with product information and supply chain costs. The result provides a complete dataset for analyzing order performance, pricing, and profitability at the individual order item level. [None] (evidence: models\marts\order_items.sql:1-66, method: static)
- models\marts\order_items.yml - This module defines a data model for analyzing order items, including their associated costs, revenues, and categorization as food or drink items. It enables detailed financial and operational reporting through semantic models, metrics (such as revenue, cost, and profit), and saved queries that aggregate and analyze order data over time. The unit test ensures accurate aggregation of supply costs at the order level. [None] (evidence: models\marts\order_items.yml:1-181, method: static)
- models\marts\products.sql - This module retrieves and processes product data from a staging table containing product information. It serves as a data transformation layer that prepares product data for downstream usage, likely in reporting or analysis workflows. The module acts as an intermediary step to ensure consistent and clean product data is available for business intelligence purposes. [None] (evidence: models\marts\products.sql:1-9, method: static)
- models\marts\products.yml - This module defines a semantic model named "products" that represents a product dimension table. The model provides a structured view of product data with one row per product, including various product attributes like name, type, description, and pricing information. It serves as a dimensional reference table that can be used to add contextual information to metrics and support analytical queries about products. [None] (evidence: models\marts\products.yml:1-26, method: static)
- models\marts\supplies.sql - This module retrieves and processes supply chain data from a staging table containing supply information. It appears to be part of a larger data pipeline that transforms raw supply data into a format suitable for analysis or reporting. The module serves as an intermediate step in preparing supply chain metrics and inventory data for business intelligence purposes. [None] (evidence: models\marts\supplies.sql:1-9, method: static)
- models\marts\supplies.yml - This module defines a semantic model for supply chain data, specifically modeling the relationship between supplies and products. It provides a structured representation of supply information including supply identifiers, product associations, cost data, and perishability status. The model enables business users to analyze supply-related metrics and dimensions for reporting and analytical purposes. [None] (evidence: models\marts\supplies.yml:1-24, method: static)
- models\staging\stg_customers.sql - This module transforms raw customer data by extracting and renaming key fields from the e-commerce customers table. It specifically pulls customer IDs and names, standardizing them into a clean format with explicit column naming conventions. The transformed data is then made available for downstream consumption through a final selection of all renamed fields. [None] (evidence: models\staging\stg_customers.sql:1-23, method: static)
- models\staging\stg_customers.yml - This module defines a staging model for customer data that applies basic cleansing and transformation rules to create a standardized dataset with one record per customer. The model ensures data quality by enforcing that each customer has a unique identifier and that no customer records contain null values in the key field. This serves as a foundational layer for downstream customer analytics and reporting applications. [None] (evidence: models\staging\stg_customers.yml:1-9, method: static)
- models\staging\stg_locations.sql - This module transforms raw store data from an e-commerce source by renaming and reformatting key fields. It extracts location information including identifiers, names, tax rates, and opening dates, while standardizing the date format to daily granularity. The resulting dataset provides a clean, structured view of store locations for downstream analysis and reporting. [None] (evidence: models\staging\stg_locations.sql:1-29, method: static)
- models\staging\stg_locations.yml - This module transforms raw store location data by cleaning and standardizing the information into a structured format. It processes timestamp fields by truncating them to dates and ensures each location has a unique identifier. The resulting dataset provides a consistent view of open locations with basic business attributes like location name, tax rate, and opening date. [None] (evidence: models\staging\stg_locations.yml:1-43, method: static)
- models\staging\stg_orders.sql - This module transforms raw e-commerce order data by renaming columns and converting currency amounts from cents to dollars. It extracts order information including IDs, financial amounts, and timestamps while maintaining data consistency through standardized column naming conventions. The transformed data provides a clean, standardized view of order transactions for downstream analysis and reporting. [None] (evidence: models\staging\stg_orders.sql:1-33, method: static)
- models\staging\stg_orders.yml - This module defines a staging model for order data that includes basic data validation and transformation rules. The model ensures data quality by validating that the order total minus tax paid equals the subtotal, while also enforcing uniqueness and non-null constraints on the order ID. This serves as a cleaned, standardized representation of order records for downstream processing. [None] (evidence: models\staging\stg_orders.yml:1-12, method: static)
- models\staging\stg_order_items.sql - This module transforms raw e-commerce item data by renaming and reorganizing key identifiers. It extracts order item records from the e-commerce source system and standardizes the column names for better data consistency. The output provides a clean mapping of order items with their corresponding order and product identifiers. [None] (evidence: models\staging\stg_order_items.sql:1-22, method: static)
- models\staging\stg_order_items.yml - This module defines a staging model for order items that represents individual food and drink items within customer orders. It establishes a normalized structure where each row corresponds to a single item from an order, with references back to the parent order through a foreign key relationship. The model ensures data integrity by requiring non-null values for both the unique item identifier and the associated order ID, while maintaining referential integrity with the orders table. [None] (evidence: models\staging\stg_order_items.yml:1-16, method: static)
- models\staging\stg_products.sql - This module transforms raw product data from an e-commerce system by renaming and reformatting fields to create a standardized product dataset. It converts pricing from cents to dollars, categorizes products as food or drink items based on their type, and structures the data with clear column names for downstream use. The result is a cleaned and enriched product catalog ready for analysis or integration with other systems. [None] (evidence: models\staging\stg_products.sql:1-34, method: static)
- models\staging\stg_products.yml - This module defines a staging model for product data that represents food and drink items available for ordering. The model includes basic data cleaning and transformation rules to ensure data quality, with each row representing a unique product identified by a product ID. The implementation enforces data integrity through null and uniqueness constraints on the product ID field. [None] (evidence: models\staging\stg_products.yml:1-9, method: static)
- models\staging\stg_supplies.sql - This module transforms raw supply data from an e-commerce system into a standardized format with properly typed and renamed columns. It generates a unique supply identifier, converts cost values from cents to dollars, and preserves key supply characteristics like name and perishability status. The transformed data provides a clean, consistent view of supply inventory information for downstream analysis and reporting. [None] (evidence: models\staging\stg_supplies.sql:1-31, method: static)
- models\staging\stg_supplies.yml - This module manages supply expense data by creating a structured representation of supply costs with proper identification and validation. It tracks individual supply expenses through unique identifiers and ensures data quality by validating that each supply cost record has a non-null, unique key. The model handles the complexity of fluctuating supply costs by maintaining separate records for each cost change while preserving the relationship to the original supply item. [None] (evidence: models\staging\stg_supplies.yml:1-12, method: static)
- models\staging\__sources.yml - This module defines the raw data schema for an e-commerce system, specifically organizing customer, order, item, store, product, and supply data into separate logical tables. The structure supports tracking complete purchase histories with detailed information about customers, their orders, individual items within each order, store locations, product SKUs, and associated supplies needed for those products. [None] (evidence: models\staging\__sources.yml:1-20, method: static)
