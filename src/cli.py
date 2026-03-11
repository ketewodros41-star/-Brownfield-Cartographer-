import argparse
import os
import subprocess
from src.orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(description="The Brownfield Cartographer CLI")
    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a repository")
    analyze_parser.add_argument("repo_path", help="Path to local repository or GitHub URL")
    analyze_parser.add_argument("--incremental", action="store_true", help="Only analyze changed files")


    # Query command
    query_parser = subparsers.add_parser("query", help="Query the codebase knowledge graph")

    args = parser.parse_args()

    if args.command == "analyze":
        repo_path = args.repo_path
        if _looks_like_git_url(repo_path):
            repo_path = _clone_repo(repo_path)
        orchestrator = Orchestrator(repo_path)
        orchestrator.run_analysis(incremental=args.incremental)

    elif args.command == "query":
        # For the demo, we'll implement a simple interactive loop or static query
        print("Query mode (Interactive loop not fully implemented in this demo)")
        # Example query result
        print("Try: 'What what breaks if I change customers.sql?'")
    else:
        parser.print_help()

def _looks_like_git_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "git@")) or value.endswith(".git")

def _clone_repo(url: str) -> str:
    base_dir = os.path.join(os.getcwd(), ".cartography", "repos")
    os.makedirs(base_dir, exist_ok=True)
    repo_name = os.path.splitext(os.path.basename(url.rstrip("/")))[0]
    target_dir = os.path.join(base_dir, repo_name)

    if not os.path.exists(target_dir):
        subprocess.run(["git", "clone", url, target_dir], check=False)
    return target_dir

if __name__ == "__main__":
    main()
