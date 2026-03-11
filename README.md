# The Brownfield Cartographer

A multi-agent codebase intelligence system for rapid onboarding into large production repositories.

## Installation

```bash
pip install -e .
```

Requires `tree-sitter` grammars for Python, SQL, and YAML.

## Usage

### Analyze a repository

```bash
python src/cli.py analyze /path/to/repo
```

This will generate a `.cartography` directory with:
- `module_graph.json`: Structural dependency graph.
- `lineage_graph.json`: Data flow lineage graph.
- `CODEBASE.md`: Architectural context.
- `onboarding_brief.md`: Day-One answers.
- `cartography_trace.jsonl`: Audit log.

### Query the knowledge graph

```bash
python src/cli.py query
```

## Project Structure

- `src/analyzers/`: AST and lineage extraction.
- `src/agents/`: Specialized analysis agents.
- `src/graph/`: Knowledge graph management.
- `src/models/`: Pydantic schemas.
