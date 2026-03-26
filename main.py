#   main.py
#   Entry point to run different workflows or launch web interface

# ----- Imports -----
import argparse
from workflows import run_webpage_workflow, run_coding_workflow
from utils.logging_utils import setup_logging

# ----- Main -----
def main() :
    setup_logging()
    parser = argparse.ArgumentParser(description="Run AG2 workflows or web interface")
    parser.add_argument("mode", nargs="?", choices=["webpage", "coding", "web"], 
                        default="web", help="Mode: workflow name or 'web' for web interface")
    parser.add_argument("--task", type=str, help="Task description (optional for workflows)")
    args = parser.parse_args()
    
    if args.mode == "web":
        # Launch web server
        from web.app import create_app
        app = create_app()
        app.run(debug=True, host="127.0.0.1", port=5001)
    elif args.mode == "webpage" :
        run_webpage_workflow(args.task)
    elif args.mode == "coding" :
        if not args.task :
            args.task = input("Enter coding task: ")
        run_coding_workflow(args.task)

if __name__ == "__main__" :
    main()