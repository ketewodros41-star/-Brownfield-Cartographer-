import os
import datetime
import json
from typing import List, Dict, Any

class Archivist:
    def __init__(self, output_dir: str = ".cartography"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.trace_file = os.path.join(self.output_dir, "cartography_trace.jsonl")

    def log_action(self, agent: str, operation: str, evidence: str, confidence: float):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent,
            "operation": operation,
            "evidence": evidence,
            "confidence": confidence
        }
        with open(self.trace_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def generate_codebase_md(self, context: Dict[str, Any]):
        path = os.path.join(self.output_dir, "CODEBASE.md")
        with open(path, "w") as f:
            f.write("# CODEBASE.md\n\n")
            f.write("## Architecture Overview\n")
            f.write(context.get("overview", "N/A") + "\n\n")
            
            f.write("## Critical Path (Top Modules by PageRank)\n")
            for mod in context.get("critical_modules", []):
                f.write(f"- {mod}\n")
            f.write("\n")

            f.write("## Data Sources and Sinks\n")
            f.write("### Sources\n")
            for s in context.get("sources", []): f.write(f"- {s}\n")
            f.write("### Sinks\n")
            for s in context.get("sinks", []): f.write(f"- {s}\n")
            f.write("\n")

            f.write("## Known Technical Debt\n")
            for debt in context.get("tech_debt", []):
                f.write(f"- {debt}\n")
            f.write("\n")

    def generate_onboarding_brief(self, answers: str):
        path = os.path.join(self.output_dir, "onboarding_brief.md")
        with open(path, "w") as f:
            f.write("# Onboarding Brief\n\n")
            f.write(answers)
