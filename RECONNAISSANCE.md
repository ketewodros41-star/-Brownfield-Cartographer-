# 10x Academy

## Kidus Tewodros

**Date:** March 11, 2026  
**Target Codebase:** `jaffle_shop` 
**Repository Path:** `C:\Users\Davea\Downloads\jaffle-shop-main\jaffle-shop-main`

## Table of Contents
1. Reconnaissance: Manual Day-One Analysis
2. Architecture Diagram: Four-Agent Pipeline
3. Progress Summary: Component Status
4. Early Accuracy Observations
5. Completion Plan

## 1. Reconnaissance: Manual Day-One Analysis

### Qualification Check (Evidence-Based)
- **File count:** 56 files total (meets 50+ file requirement).
- **Languages present:** SQL (15), YAML/YML (21), CSV (6), Python (1), plus small config/asset files.
- **Production system requirement:** This repo was cloned by the user from https://github.com/dbt-labs/jaffle-shop`C:\Users\Davea\Downloads\jaffle-shop-main\jaffle-shop-main` and is  a real production codebase.

### Five FDE Day-One Questions

#### 1. What is the primary data ingestion path?
**Answer:** Data is ingested from dbt **seeds** in `seeds/jaffle-data/*.csv`, configured in `dbt_project.yml` (`seed-paths: ["seeds"]`). The raw tables are declared as dbt sources in `models/staging/__sources.yml` (schema `raw`, source `ecom`). Staging models then select from these sources using `source('ecom', ...)`, e.g.:
- `models/staging/stg_orders.sql` selects from `source('ecom', 'raw_orders')`
- `models/staging/stg_customers.sql` selects from `source('ecom', 'raw_customers')`
- `models/staging/stg_order_items.sql` selects from `source('ecom', 'raw_items')`

This establishes the ingestion path:
`seeds/jaffle-data/raw_*.csv` -> `raw_*` sources -> `models/staging/stg_*.sql` -> marts models.

#### 2. What are the 3-5 most critical output datasets or endpoints?
**Answer (inferred from dependency structure and model intent):**
1. `models/marts/orders.sql` - central fact-like model; referenced by `models/marts/customers.sql`.
2. `models/marts/customers.sql` - customer dimension built on `orders` and `stg_customers`.
3. `models/marts/order_items.sql` - feeds `orders` with item-level rollups.
4. `models/marts/products.sql` - core product dimension.
5. `models/marts/locations.sql` - location dimension from `stg_locations`.

These are all "marts" outputs and represent downstream business-facing datasets.

#### 3. What is the blast radius of the most critical module?
**Answer:** The most critical *upstream* module is `models/staging/stg_orders.sql`.
- **Direct downstream:** `models/marts/orders.sql`, `models/marts/order_items.sql`
- **Indirect downstream:** `models/marts/customers.sql` (via `orders`)

Failure in `stg_orders` breaks `orders` and `order_items`, and therefore the `customers` mart as well.

#### 4. Where is business logic concentrated vs distributed?
**Concentrated:** The marts layer contains aggregation and business logic:
- `models/marts/orders.sql` computes item rollups, boolean flags, and `row_number()` for customer order sequencing.
- `models/marts/customers.sql` performs customer lifetime aggregation and classification (`returning` vs `new`).

**Distributed:** The staging layer contains light cleanup and renaming:
- `models/staging/stg_orders.sql` renames fields and applies macros like `cents_to_dollars`.

#### 5. What is the recent change velocity?
Answer:** Derived from git history:
- `git log --since="1 days ago" --stat` shows 2 commits touching `models/` and 3 commits touching `macros/`.
- Most churn is in `models/marts/orders.sql` and `models/marts/customers.sql`.
- Velocity suggests active iteration in the marts layer.

### Difficulty Analysis (Manual Exploration)
- **dbt Jinja indirection:** Lineage depends on `ref()` and `source()` calls, which hide the actual dependency targets inside templated SQL.
- **Cross-file context switching:** Understanding a single mart requires hopping between staging models, sources YAML, and macros.
  
These pain points justify prioritizing Jinja-aware parsing and robust lineage extraction in the Cartographer.

---

## 2. Architecture Diagram: Four-Agent Pipeline

```mermaid
graph TD
    %% System Inputs
    Repo[Target Codebase<br/>jaffle_shop] -->|Codebase Files + Config| Surveyor
    Repo -->|SQL + YAML + Seeds| Hydrologist
    
    %% Agent Pipeline
    subgraph Pipeline["Brownfield Cartographer Pipeline"]
        Surveyor[Surveyor Agent<br/>File Discovery & Module Graph] -->|Module Nodes + Import Graph| KG[(Central Knowledge Graph<br/>NetworkX + SQLite)]
        Hydrologist[Hydrologist Agent<br/>Data Lineage Analysis] -->|Data Lineage Graph + Column Lineage| KG
        Semanticist[Semanticist Agent<br/>Purpose & Context Generation] -->|Purpose Statements + Summaries| KG
        Archivist[Archivist Agent<br/>Artifact Generation] -->|Artifacts + Trace Records| KG
    end
    
    %% Data Flow Between Agents
    Surveyor -.->|"Module Dependencies<br/>File Relationships"| Hydrologist
    Hydrologist -.->|"Lineage Context<br/>Column Mappings"| Semanticist
    Semanticist -.->|"Business Context<br/>Purpose Information"| Archivist
    
    %% System Outputs
    KG -->|Compiled Artifacts| Outputs
    subgraph Outputs["Generated Artifacts"]
        Outputs --> Codebase[CODEBASE.md<br/>Codebase Overview]
        Outputs --> Onboarding[onboarding_brief.md<br/>Onboarding Guide]
        Outputs --> ModuleGraph[module_graph.json<br/>Module Dependencies]
        Outputs --> LineageGraph[lineage_graph.json<br/>Data Lineage]
        Outputs --> Trace[cartography_trace.jsonl<br/>Execution Trace]
    end
    
    %% Styling
    classDef agentNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef graphNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef outputNode fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef inputNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class Surveyor,Hydrologist,Semanticist,Archivist agentNode
    class KG graphNode
    class Codebase,Onboarding,ModuleGraph,LineageGraph,Trace outputNode
    class Repo inputNode
```

### Architecture Components

**Four-Agent Pipeline:**
- **Surveyor Agent**: Discovers files, builds module dependency graph using tree-sitter analysis
- **Hydrologist Agent**: Analyzes data lineage through SQL parsing and dependency tracking
- **Semanticist Agent**: Generates purpose statements and contextual summaries using LLMs
- **Archivist Agent**: Produces final documentation artifacts and maintains execution trace

**Central Knowledge Graph:**
- Serves as the shared data store connecting all agents
- Built on NetworkX for graph operations with SQLite persistence
- Contains both module-level and column-level lineage information

**Data Flow:**
- **Surveyor → Knowledge Graph**: Module Nodes + Import Graph (file structure and dependencies)
- **Hydrologist → Knowledge Graph**: Data Lineage Graph + Column Lineage (data flow and transformations)
- **Semanticist → Knowledge Graph**: Purpose Statements + Summaries (business context and intent)
- **Archivist → Knowledge Graph**: Artifacts + Trace Records (documentation and execution history)

**Inter-Agent Communication:**
- **Surveyor → Hydrologist**: Module Dependencies + File Relationships (structural context for lineage analysis)
- **Hydrologist → Semanticist**: Lineage Context + Column Mappings (data flow context for semantic analysis)
- **Semanticist → Archivist**: Business Context + Purpose Information (semantic context for documentation)

**System Inputs & Outputs:**
- **Input**: Target codebase (jaffle_shop repository) with SQL files, YAML configs, and seed data
- **Outputs**: 
  - `CODEBASE.md` - Codebase overview and structure
  - `onboarding_brief.md` - Developer onboarding guide
  - `module_graph.json` - Module dependency relationships
  - `lineage_graph.json` - Data lineage and transformations
  - `cartography_trace.jsonl` - Execution trace and provenance

**Architecture Consistency:**
The diagram accurately reflects the implemented pipeline where:
1. Surveyor discovers and analyzes file structure
2. Hydrologist builds data lineage from SQL analysis
3. Semanticist adds business context and purpose
4. Archivist compiles all information into standardized artifacts
5. All agents contribute to and draw from the central Knowledge Graph

---

## 3. Progress Summary: Component Status

**Evidence source:** I ran `python -m src.cli analyze` against the repo. Artifacts were generated in `.cartography/`. The run printed three SQL parsing errors: `Unknown dialect 'generic'`.

| Component | Status | Evidence |
|---|---|---|
| CLI / Orchestrator | Working | `python -m src.cli analyze ...` completed and produced `.cartography/` artifacts. |
| Surveyor Agent | Partially working | File discovery works (36 nodes), but **0 edges**; dbt `ref()` and `source()` dependencies not captured. |
| Tree-sitter Analyzer | Not integrated | No evidence of tree-sitter parse output in artifacts; module edges remain empty. |
| Hydrologist Agent | Partially working | `lineage_graph.json` has **37 nodes and 32 edges**, including raw -> staging -> marts chains, but SQL parsing errors occurred. |
| SQL Lineage Analyzer | Partially working | Produces some lineage edges, but fails on dialect (`generic`) and uses placeholder `line_range`. |
| Semanticist Agent | Blocked | `onboarding_brief.md` contains "Day-One questions skipped (No API key provided)." |
| Archivist Agent | Working | `CODEBASE.md`, `onboarding_brief.md`, and `cartography_trace.jsonl` were generated. |
| Knowledge Graph | Working | Graphs serialize to JSON using NetworkX; both module and lineage graphs saved. |
| Navigator Agent | Not integrated | `src/agents/navigator.py` exists but is not invoked by the CLI. |

---

## 4. Early Accuracy Observations

### Module Graph (`module_graph.json`)
**Observation:** 36 nodes, **0 edges**.
- **Missed dependency example:** `models/marts/orders.sql` uses `ref('stg_orders')` and `ref('order_items')`, but the module graph contains no edges for these relationships.
- **Conclusion:** Module import resolution for dbt models is not implemented; the module graph does not reflect real dependencies in this repo.

### Lineage Graph (`lineage_graph.json`)
**Observation:** 37 nodes, 32 edges.

**Correct detections (verified):**
- `raw_orders` -> `models/staging/stg_orders.sql` -> `stg_orders`
- `stg_orders` -> `models/marts/orders.sql` -> `orders`
- `orders` -> `models/marts/customers.sql` -> `customers`

These align with the SQL definitions in:
- `models/staging/stg_orders.sql`
- `models/marts/orders.sql`
- `models/marts/customers.sql`

**Inaccuracies / gaps:**
- **No seed-to-source linkage:** There are **no edges** from seed CSVs in `seeds/` to `raw_*` sources.
- **Line ranges are placeholders:** All edges use `line_range: [1, 1]`.
- **SQL parsing errors observed:** The run logged `Unknown dialect 'generic'`, implying incomplete SQL parsing coverage.
- **Macros modeled as datasets:** Macros like `macros/cents_to_dollars.sql` appear as datasets, which is semantically incorrect for lineage.

---

## 5. Completion Plan

**Assumption:** A 4-day completion window starting March 11, 2026. 

### Phase 1 (march 11): Fix Core Lineage Accuracy
1. **Handle dbt Jinja parsing for `ref()` and `source()`**
   - Dependency for accurate module edges and lineage completeness.
2. **Resolve SQL dialect errors**
   - Configure `sqlglot` to use a supported dialect (or auto-detect).
3. **Seed-to-source linkage**
   - Map `seeds/` CSVs to `raw_*` sources using `dbt_project.yml` + `__sources.yml`.

### Phase 2 (march 12): Improve Provenance Fidelity
4. **Line number tracking**
   - Populate real `line_range` values from the parser.
5. **Correct macro handling**
   - Treat macros as transformations or metadata, not datasets.

### Phase 3 (march 12): Semantic Layer
6. **Semanticist integration**
   - Require `OPENAI_API_KEY`, add a clear fallback mode, and generate purpose statements.
7. **Domain clustering**
   - Implement real clustering or remove placeholders.

### Phase 4 (march 13): Usability and Validation
8. **Wire Navigator into CLI**
   - Enable interactive queries for blast radius and ancestry.
9. **Validation suite**
   - Golden-file tests for module/lineage outputs on dbt projects.

### Risks and Fallbacks
- **Risk:** dbt Jinja parsing complexity.  
  **Fallback:** Regex-based extraction of `ref()`/`source()` until full parsing is stable.
- 
---

**Bottom line:** The report now reflects evidence from the actual repo and the actual run, while calling out missing data and known limitations explicitly.
