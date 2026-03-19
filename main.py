#   main.py
#   Entry point to run different workflows

# ----- Imports -----
import argparse
from workflows import run_webpage_workflow, run_coding_workflow
from utils.logging_utils import setup_logging

# ----- Main -----
def main() :
    setup_logging()
    parser = argparse.ArgumentParser(description="Run AG2 workflows")
    parser.add_argument("workflow", choices=["webpage", "coding"], help="Workflow to run")
    parser.add_argument("--task", type=str, help="Task description (optional)")
    args = parser.parse_args()
    
    if args.workflow == "webpage" :
        run_webpage_workflow(args.task)
    elif args.workflow == "coding" :
        if not args.task :
            args.task = input("Enter coding task: ")
        run_coding_workflow(args.task)

if __name__ == "__main__" :
    main()