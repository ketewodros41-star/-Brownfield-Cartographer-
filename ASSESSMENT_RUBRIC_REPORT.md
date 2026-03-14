# Brownfield Cartographer — Rubric Assessment Report

**Date:** 2026-03-14  
**Assessed by:** Automated Code Review (Antigravity)  
**Repository:** `brownfield-cartographer`

---

## Summary Scorecard

| Criterion | Score | Label |
|---|---|---|
| Hydrologist Agent — Data Lineage Construction | **5 / 5** | Mastered |
| Semanticist Agent — LLM-Powered Analysis | **5 / 5** | Mastered |
| Archivist Agent — Artifact Generation Code | **4 / 5** | Mastered (minor gap) |
| Navigator Agent — Query Interface | **5 / 5** | Mastered |
| CLI & Orchestration Pipeline | **5 / 5** | Mastered |
| **TOTAL** | **24 / 25** | |

---

## 1. Hydrologist Agent — Data Lineage Construction

**Score: 5 / 5 — Mastered**

### Evidence

#### SQL Parsing (`src/analyzers/sql_lineage.py`)
- `sqlglot` is imported and used for real parse-tree traversal — **not** trivial regex.
- `_parse_with_dialects()` cycles through `["postgres", "bigquery", "snowflake", "duckdb", "spark", "mysql", "sqlite", "ansi"]` — **8 dialects supported**, well above the 2-dialect Mastered threshold.
- Auto-detection logic: when `dialect == "auto"` it tries each dialect in order and falls back to default.
- JOIN/CTE/subquery support: `exp.CTE` nodes are explicitly found, aliases are collected, and then **removed from the source set** — correctly treating CTEs as internal transforms, not external sources (lines 46–52).
- Sink extraction covers `exp.Insert`, `exp.Create`, `exp.Update`, `exp.Delete` — all major write patterns handled.
- Jinja stripping (`_strip_jinja`) allows parsing of dbt SQL that contains `{{ }}` and `{% %}` blocks.

#### DAG Config Parsing (`src/analyzers/dag_config_parser.py`)
- `parse_dbt_schema()` uses `yaml.safe_load` to parse `schema.yml` files and extracts model names, column lists, and `depends_on` relationships.
- `parse_airflow_dag()` uses regex-based `>>` / `<<` operator detection to reconstruct Airflow task dependencies, including list-style chaining (`[task1, task2] >> task3`), capturing `line_range` per edge.
- Both parsers are wired into `Hydrologist._analyze_yaml_file()` and `Hydrologist._analyze_python_file()` respectively.

#### Python Data Flow (`src/analyzers/python_data_flow.py`)
- Uses **tree-sitter** (not regex) for AST-accurate call detection.
- Detects **pandas** (`read_csv`, `read_parquet`, `read_sql`, `to_csv`, `to_parquet`, `to_sql`, etc.).
- Detects **PySpark** (`spark.read.csv`, `df.write.parquet`, `saveAsTable`, etc.).
- Detects **SQLAlchemy** `execute()` calls and classifies them as read or write by inspecting the SQL verb of the first string argument.
- Dynamic references that cannot be resolved to a literal path are logged as `unresolved` dicts with `call`, `line_range`, and `reason` fields (line 65–69) — satisfying the "logging dynamic references it cannot resolve" requirement.

#### Graph Construction (`src/agents/hydrologist.py`)
- Uses `KnowledgeGraph` (backed by NetworkX DiGraph) with typed `DatasetNode` and `TransformationNode` entries.
- All three analyzers merge into the **same** `self.lineage_kg` graph.
- Every edge carries `transformation_type`, `source_file`, and `line_range` (see lines 73–74, 105–106, 158–163).
- `blast_radius()` uses `nx.descendants()` (BFS/DFS downstream traversal); with `return_paths=True` returns all simple paths.
- `find_sources()` returns nodes with `in_degree == 0`; `find_sinks()` returns nodes with `out_degree == 0`.

### Minor Observations
- The YAML parsing of Airflow DAGs is regex-based (not tree-sitter), so complex, multi-line Python DAG code may be partially missed. Acceptable for Mastered level per rubric language ("Airflow DAGs **or** dbt schema.yml").
- `dialect_used` is recorded on edges as metadata — adds traceable provenance.

---

## 2. Semanticist Agent — LLM-Powered Analysis

**Score: 5 / 5 — Mastered**

### Evidence

#### Purpose Statements (`src/agents/semanticist.py`)
- `generate_purpose_statement()` calls `_strip_docstrings()` **before** sending code to the LLM (line 85), using `ast.NodeTransformer` to scrub module, function, async-function, and class docstrings from the parse tree.
- The system prompt explicitly instructs: *"Ignore all docstrings and comments. Derive the business purpose from implementation details only."* (lines 86–89).
- This satisfies both the code-grounding requirement and the explicit instruction to ignore docstrings.

#### Model Tiering & Token Budget (`ContextWindowBudget`)
- Two distinct model parameters: `model_bulk` (default `gpt-4o-mini`) for per-module purpose statements and `model_synth` (default `gpt-4o`) for synthesis/drift/Day-One answers.
- When Groq is configured, `GROQ_MODEL_BULK` (`llama-3.1-8b-instant`) vs `GROQ_MODEL_SYNTH` (`llama-3.1-70b-versatile`) — tiering is preserved across providers.
- `ContextWindowBudget` tracks `usage` (tokens) and `cost_usd` cumulatively, exposes `can_afford()` to gate all LLM calls, and enforces limits by raising `RuntimeError("Token budget exceeded.")` (line 228).
- `_estimate_tokens()` heuristic (1 token ≈ 4 chars) keeps cost tracking fast.

#### Documentation Drift Detection
- `detect_docstring_drift()` compares LLM-generated purpose against the extracted docstring.
- Returns **structured output**: `{ severity: none|low|medium|high, contradictions: [list of strings], summary }` (line 126–128).
- Uses the `model_synth` (expensive) model for this nuanced comparison.
- Fallback path when no LLM client is available still returns structured output with a `note` field.

#### Domain Clustering
- `cluster_into_domains()` gets embeddings for purpose statements (not hardcoded labels).
- k is inferred as `max(2, int(sqrt(n)))` — not arbitrary fixed k.
- Cluster labels are derived from top-3 TF-IDF terms per cluster: `"domain:term1-term2-term3"` — meaningful, data-driven domain names.
- Labels are written back to `module_kg.graph.nodes[mod.path]["domain_cluster"]`.

#### Day-One Questions
- `answer_day_one_questions()` sends a synthesis prompt that explicitly instructs: *"Cite each claim with file path and line range. Include analysis method tag (static|llm)."* (lines 191–193).
- The context dict passed in (`_build_day_one_context()` in `orchestrator.py`) carries `annotated` strings already formatted as `{module_path} (evidence: {file}:{L1}-{L2}, method: static)` for every critical path entry, source, and sink.
- `_ensure_citations()` appends an Evidence appendix if the LLM response doesn't already contain `"evidence:"`, listing file paths, line ranges, and method tags.

### Minor Observations
- Embeddings for clustering still require OpenAI (`embed_client`) — Ollama/Groq embedding path not yet implemented. Falls back gracefully to TF-IDF within `cluster_into_domains()`, so clustering still works without embeddings, but with lower quality vectors.

---

## 3. Archivist Agent — Artifact Generation Code

**Score: 4 / 5 — Mastered (one structural gap)**

### Evidence

#### CODEBASE.md Generation (`src/agents/archivist.py`)
- `generate_codebase_md()` produces a structured markdown file with **all six required sections**:
  1. Architecture Overview
  2. Critical Path (Top Modules by PageRank)
  3. Data Sources & Sinks
  4. Known Technical Debt
  5. High-Velocity Files
  6. Module Purpose Index
- Each section includes an item count and a confidence badge (`low` / `medium` / `high`).
- A **Change Summary table** comparing previous vs. current item counts by section is written when a prior `CODEBASE.md` exists — delta tracking per run.
- Generation timestamp is embedded at the top.

#### Onboarding Brief
- `generate_onboarding_brief()` produces `onboarding_brief.md` with a **Quick Reference summary table** (Q# / Question / Status) followed by five clearly demarcated `## Q{i}: {question}` sections.
- `_parse_day_one_answers()` is a robust parser handling both `Q1:` and `Q1.` formats with a paragraph-splitting fallback.

#### Trace Logging
- `log_action()` appends structured JSONL to `cartography_trace.jsonl` with: `timestamp`, `agent`, `operation`, `evidence`, `confidence`, `method`, `source_files`, and `details`.
- The orchestrator calls `log_action` for **every agent separately** (Orchestrator start/finish, Surveyor, Hydrologist, Semanticist, Archivist) with rich `details` dicts including node/edge counts, token budgets, etc.

#### Upstream Integration
- Archivist receives pre-computed output from all three upstream agents via the `context` dict — it does **not** perform its own analysis.

### Gap: Why 4 instead of 5
- The rubric's Mastered level states criteria but the Mastered/Competent/Developing/Unsatisfactory levels for Archivist are **left blank in the rubric as provided** (all four bullet bodies are empty). Based on the evidence checks alone, all four evidence checks pass. The deduction of 1 point is applied conservatively for the following **real code gap**:
  - The onboarding brief's `_parse_day_one_answers()` relies entirely on regex splitting of the LLM's free-text output. When the LLM returns answers that don't start with `Q1:` / `Q1.`, the fallback splits on blank lines — which can misalign questions and answers, producing a brief with mislabeled sections. A more robust structured-output approach (e.g., JSON schema from the LLM) would be more reliable.

---

## 4. Navigator Agent — Query Interface

**Score: 5 / 5 — Mastered**

### Evidence

#### Four Tools (`src/agents/navigator.py`)
All four specified tools are implemented:

| Tool | Implementation |
|---|---|
| `find_implementation(concept)` | Lines 24–72 |
| `trace_lineage(dataset, direction)` | Lines 74–86 |
| `blast_radius(module_path)` | Lines 88–108 |
| `explain_module(path)` | Lines 110–114 |

#### Graph Grounding
- `trace_lineage` and `blast_radius` use `nx.ancestors()` / `nx.descendants()` on the real `lineage_kg` NetworkX graph — not LLM calls.
- `explain_module` fetches data directly from `module_kg.graph.nodes`.
- `find_implementation` uses TF-IDF cosine similarity over the module purpose index (or real embeddings if OpenAI key is present) — not string matching.

#### Agent Framework (LangGraph)
- `_build_graph()` constructs a `StateGraph` with a `router` node and 6 execution nodes.
- Conditional edges route to: `find`, `lineage`, `blast`, `explain`, `chain_lineage_explain`, `chain_find_explain`.
- **Multi-step chaining** is supported:
  - `chain_lineage_explain`: traces lineage then explains each discovered dataset's source modules.
  - `chain_find_explain`: finds implementations then explains each found module.

#### Evidence Citations
- `_with_evidence()` appends an `evidence` dict to every result containing `file`, `line_range`, `method`, and `analysis_method` (static vs llm).
- `_edge_evidence_between()` walks the shortest path in the lineage graph and returns per-hop edge metadata including `source_file`, `line_range`, and `analysis_method`.

#### Error Handling
- All four tools return `{"error": "...", "message": "..."}` structs for missing nodes rather than raising exceptions (lines 79, 103, 114).

### Minor Observations
- The query router uses keyword matching (not an LLM router), so ambiguous natural language queries may route incorrectly. This is acceptable per rubric — LangGraph orchestrates tool selection even if routing uses keywords rather than an embedded LLM.
- `_extract_dataset_from_query()` and `_extract_path_from_query()` are naive heuristics (last token / extension matching). Production reliability would benefit from NER or an LLM slot-filler.

---

## 5. CLI & Orchestration Pipeline

**Score: 5 / 5 — Mastered**

### Evidence

#### Subcommands (`src/cli.py`)
- `analyze` and `query` subcommands are both registered via `argparse.add_subparsers()`.
- `analyze` accepts a `repo_path` positional argument and an `--incremental` flag.

#### GitHub URL Support
- `_looks_like_git_url()` checks for `http://`, `https://`, `git@` prefixes or `.git` suffix.
- `_clone_repo()` runs `git clone <url> <target_dir>` via `subprocess.run`, storing cloned repos in `.cartography/repos/`. If the target directory already exists it skips re-cloning.

#### Pipeline Wiring (`src/orchestrator.py`)
- Sequential: Surveyor → Hydrologist → Semanticist → Archivist.
- Intermediate output serialization: after each agent, graphs are saved to `.cartography/module_graph.json` and `.cartography/lineage_graph.json`.
- If Semanticist fails, Archivist still runs because semantic results are in-memory in `module_kg` (which was already saved after Surveyor). Partial graphs are preserved.

#### Incremental Updates
- When `--incremental` is set, `git diff --name-only <last_commit> HEAD` identifies changed files.
- Changed files are pruned from the previously saved graphs before re-analysis.
- The new HEAD commit is written to `.cartography/last_run_commit` after a successful incremental run.
- Falls back to full re-analysis gracefully if git commands fail.

#### Query Mode
- `query` subcommand loads serialized graphs from `.cartography/` and hands them to `Navigator`, then enters a REPL loop (`input("> ")`), passing user input to `navigator.query()` until `exit` or EOF.

---

## Overall Assessment

The repository demonstrates **strong Mastered-level implementation** across all five rubric categories. The code is not cosmetic — the analyzers use real parse trees (tree-sitter, sqlglot ASTs), the graph is a real NetworkX DiGraph with typed nodes and rich edge metadata, and the LLM layer has genuine model tiering, token budgeting, docstring stripping, and structured drift output.

**Honest deductions:**
- Archivist gets a conservative 4/5 solely due to the fragile free-text parsing of Day-One answers into the onboarding brief. All evidence checks technically pass.
- Navigator's query routing is keyword-based rather than LLM-powered — not penalized per rubric language, but worth noting for production hardening.
- Embeddings for domain clustering fall back to TF-IDF when no OpenAI key is present — still functional but lower quality.

**Total: 24 / 25**
