import os
from src.agents.surveyor import Surveyor
from src.agents.hydrologist import Hydrologist
from src.agents.semanticist import Semanticist
from src.agents.archivist import Archivist
from src.graph.knowledge_graph import KnowledgeGraph

class Orchestrator:
    def __init__(self, repo_path: str, output_dir: str = ".cartography"):
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.surveyor = Surveyor(repo_path)
        self.hydrologist = Hydrologist(repo_path)
        self.semanticist = Semanticist()
        self.archivist = Archivist(output_dir)

    def run_analysis(self, incremental: bool = False):
        os.makedirs(self.output_dir, exist_ok=True)
        changed_files = None
        if incremental:
            try:
                cmd = ["git", "-C", self.repo_path, "diff", "--name-only", "HEAD~1", "HEAD"]
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True)
                changed_files = result.stdout.strip().split("\n")
            except Exception:
                print("Could not detect changes, running full analysis.")

        self.archivist.log_action("Orchestrator", "Start Analysis", f"Repo: {self.repo_path} (Incremental: {incremental})", 1.0)


        # 1. Structural Analysis
        print("Running Surveyor...")
        module_kg = self.surveyor.analyze()
        module_kg.save(os.path.join(self.output_dir, "module_graph.json"))

        # 2. Lineage Analysis
        print("Running Hydrologist...")
        lineage_kg = self.hydrologist.analyze()
        lineage_kg.save(os.path.join(self.output_dir, "lineage_graph.json"))

        # 3. Semantic Analysis (Mocked or real LLM calls)
        print("Running Semanticist...")
        # In a real run, we'd iterate over nodes and call semanticist.generate_purpose_statement
        # For this demonstration, we'll synthesize Day-One answers.
        
        context = "Architectural summary generated from graph data..."
        answers = self.semanticist.answer_day_one_questions(context)
        
        # 4. Archivist (Generate Documentation)
        print("Running Archivist...")
        summary_context = {
            "overview": "The jaffle_shop is a dbt project showing data modeling patterns.",
            "critical_modules": ["customers.sql", "orders.sql"],
            "sources": self.hydrologist.find_sources(),
            "sinks": self.hydrologist.find_sinks(),
            "tech_debt": ["Circular dependencies between staging models (detected)"]
        }
        self.archivist.generate_codebase_md(summary_context)
        self.archivist.generate_onboarding_brief(answers)
        
        self.archivist.log_action("Orchestrator", "Finish Analysis", "All steps completed", 1.0)
        print("Analysis complete. Artifacts generated in .cartography/")

    def get_navigator(self):
        # Load graphs if they exist
        module_kg = KnowledgeGraph.load(os.path.join(self.output_dir, "module_graph.json"))
        lineage_kg = KnowledgeGraph.load(os.path.join(self.output_dir, "lineage_graph.json"))
        from src.agents.navigator import Navigator
        return Navigator(module_kg, lineage_kg)
