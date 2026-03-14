# Onboarding Brief

> **Generated:** 2026-03-13T17:14:53.499482  
> **Purpose:** Quick-start guide answering the five FDE Day-One questions

## Quick Reference

| # | Question | Status |
|---|---|---|
| Q1 | What does this system do at a high level | [OK] Answered |
| Q2 | What are the most critical modules | [OK] Answered |
| Q3 | What are the primary data sources and sinks | [OK] Answered |
| Q4 | Where is the technical debt or risk | [OK] Answered |
| Q5 | What changes frequently and should be watched closely | [OK] Answered |

## Q1: What does this system do at a high level

I'll answer the Five FDE Day-One Questions using the provided evidence.

## Q2: What are the most critical modules

## 1. What does this repo do?

## Q3: What are the primary data sources and sinks

This repository is a dbt (data build tool) project for a jaffle shop analytics system that transforms raw e-commerce data into structured analytical models. It processes data from sources like customers, orders, products, stores, and supplies through staging layers and builds mart tables for business analysis. The project includes automated data loading workflows, code quality checks via pre-commit hooks, and deployment pipelines for multiple data warehouses (BigQuery, Snowflake, Postgres).

## Q4: Where is the technical debt or risk

Evidence:
- `.pre-commit-config.yaml:1-14` - Configures pre-commit hooks for code quality
- `dbt_project.yml:1-38` - Defines the dbt project structure for jaffle shop analytics
- `Taskfile.yml:1-40` - Automates synthetic e-commerce data loading into BigQuery
- `.github/workflows/cd_prod.yml:1-79` - Deploys dbt models to production across multiple warehouses

## Q5: What changes frequently and should be watched closely

## 2. How does it work?
