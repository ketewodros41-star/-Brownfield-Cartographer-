import sys
import os
import traceback
from dotenv import load_dotenv
from src.orchestrator import Orchestrator

load_dotenv()

repo_path = r"C:\Users\Davea\Downloads\jaffle-shop-main\jaffle-shop-main"
try:
    orchestrator = Orchestrator(repo_path)
    orchestrator.run_analysis(incremental=False)
    print("Analysis finished successfully!")
except Exception as e:
    print("--- TRACEBACK START ---")
    traceback.print_exc()
    print("--- TRACEBACK END ---")
    sys.exit(1)
