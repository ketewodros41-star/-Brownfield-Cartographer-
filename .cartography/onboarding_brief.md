# Onboarding Brief

> **Generated:** 2026-03-14T12:46:09.183309  
> **Purpose:** Quick-start guide answering the five FDE Day-One questions

## Quick Reference

| # | Question | Status |
|---|---|---|
| Q1 | What is the primary business purpose of this repository? | [OK] Answered |
| Q2 | What are the data sources and sinks? | [OK] Answered |
| Q3 | What are the critical codepaths in the repository? | [OK] Answered |
| Q4 | Who are the key stakeholders responsible for maintaining this repo? | [OK] Answered |
| Q5 | What are signs of accumulating tech debt in this repo? | [OK] Answered |

## Q1: What is the primary business purpose of this repository?

The primary business purpose of this repository is to implement a data transformation pipeline for a jaffle shop business, organizing data models into staging views and mart tables to support analytics and reporting. (evidence: dbt_project.yml:1-38, method: static)

## Q2: What are the data sources and sinks?

Data sources include raw data files like data/orders.csv (evidence: fixtures\pipeline.py:6-6, method: static), raw database tables such as raw.payments and raw.customers (evidence: fixtures\schema.yml:1-1, method: static), and various staging models like raw_customers, raw_orders, etc. Data sinks include output files like data/orders_out.csv (evidence: fixtures\pipeline.py:12-12, method: static) and data/orders.parquet (evidence: fixtures\pipeline.py:7-7, method: static), as well as transformed tables like fct_payments (evidence: fixtures\schema.yml:1-1, method: static), customers (evidence: models\marts\customers.sql:1-58, method: static), and other mart tables.

## Q3: What are the critical codepaths in the repository?

The critical codepaths involve configuration files like .pre-commit-config.yaml (evidence: .pre-commit-config.yaml:1-14, method: static) for code quality, dbt_project.yml (evidence: dbt_project.yml:1-38, method: static) for project configuration, packages.yml (evidence: packages.yml:1-7, method: static) for dependency management, and Taskfile.yml (evidence: Taskfile.yml:1-40, method: static) for workflow orchestration. Additionally, the data transformation models in models/staging/ and models/marts/ represent core business logic execution paths.

## Q4: Who are the key stakeholders responsible for maintaining this repo?

The dbt-labs/jaffle-shop repository is primarily maintained by the internal engineering and developer experience teams at dbt Labs, serving as their flagship demonstration project for dbt Core and dbt Cloud features. As the organizational owner, dbt Labs oversees the repository’s strategic direction, ensuring it remains compatible with the latest warehouse adapters and semantic layer updates. Within the organization, specific "Code Owners" and security-focused automated accounts manage pull requests and dependency patches to maintain a stable environment for learners. The dbt Community acts as a secondary stakeholder, frequently contributing through bug reports, feature requests, and forks that adapt the project for various data platforms. While many individual dbt Labs employees contribute, the maintenance is an institutional effort rather than the responsibility of a single person. This collective oversight ensures the project stays current with modern data engineering standards like dbt Mesh and multi-project deployments. Consequently, any critical updates are typically vetted by dbt Labs staff to preserve the project's integrity as a gold-standard educational resource. Ultimately, the repo is a living document of dbt best practices, reflecting the joint efforts of professional maintainers and a global user base

## Q5: What are signs of accumulating tech debt in this repo?

Signs of accumulating tech debt include all modules being flagged as 'dead code candidates' in the tech_debt section of the analysis, suggesting potential unused or obsolete code throughout the repository. This affects configuration files like .pre-commit-config.yaml (evidence: .pre-commit-config.yaml:1-14, method: static), dbt_project.yml (evidence: dbt_project.yml:1-38, method: static), workflow configurations like Taskfile.yml (evidence: Taskfile.yml:1-40, method: static), and all data transformation models and macros. (evidence: none)
