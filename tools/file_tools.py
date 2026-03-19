#   tools/file_tools.py
#   File system operations and browser opening

# ----- Imports -----
import os
import fnmatch
from pathlib import Path
from config.settings import WORK_DIR
import webbrowser

# ----- Helper Functions -----
def write_html_file(content: str, filename: str = "index.html") -> str :
    # write HTML content to a file and open it in the browser
    abs_path = write_file(content, filename)
    webbrowser.open(f"file://{abs_path}")
    return f"File {filename} has been created and opened in your browser."

def _safe_path(relative_path: str) -> str :
    # Convert a relative path to an absolute path inside WORK_DIR
    # Prevent directory traversal attacks
    full = os.path.abspath(os.path.join(WORK_DIR, relative_path))
    if not full.startswith(WORK_DIR):
        raise ValueError("Access outside workspace is forbidden")
    return full

def list_files(path: str = ".") -> str :
    # List files and directories in the given workspace subpath
    target = _safe_path(path)
    if not os.path.exists(target):
        return f"Path '{path}' does not exist"
    items = os.listdir(target)
    return "\n".join(items)

def read_file(filepath: str) -> str :
    # Return the content of a file
    full = _safe_path(filepath)
    if not os.path.isfile(full):
        return f"File '{filepath}' not found"
    with open(full, 'r', encoding='utf-8') as f :
        return f.read()

def write_file(filepath: str, content: str) -> str :
    # Write content to a file (overwrites!)
    full = _safe_path(filepath)
    # Ensure directory exists
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"File '{filepath}' written successfully."

def search_files(pattern: str) -> str :
    # Find files matching a glob pattern (relative to workspace)
    matches = []
    for root, dirs, files in os.walk(WORK_DIR) :
        for f in files :
            if fnmatch.fnmatch(f, pattern) :
                rel = os.path.relpath(os.path.join(root, f), WORK_DIR)
                matches.append(rel)
    return "\n".join(matches) if matches else "No files found."

def grep(pattern: str, file_pattern: str = "*") -> str :
    # Search inside files for a pattern (simple grep)
    results = []
    for root, dirs, files in os.walk(WORK_DIR) :
        for f in files :
            if fnmatch.fnmatch(f, file_pattern) :
                full = os.path.join(root, f)
                try :
                    with open(full, 'r', encoding='utf-8') as fp :
                        for i, line in enumerate(fp, 1) : 
                            if pattern in line :
                                rel = os.path.relpath(full, WORK_DIR)
                                results.append(f"{rel}:{i}: {line.strip()}")
                except :
                    continue
    return "\n".join(results) if results else "No matches."

def get_project_structure() -> str :
    # Return a tree-like view of the workspace
    # Simple implementation using `tree` command if available, else fallback
    try :
        import subprocess
        result = subprocess.run(['tree', WORK_DIR], capture_output=True, text=True, timeout=5)
        return result.stdout
    except :
        # Fallback: list recursively
        lines = []
        for root, dirs, files in os.walk(WORK_DIR) :
            level = root.replace(WORK_DIR, '').count(os.sep)
            indent = ' ' * 2 * level
            lines.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 2 * (level + 1)
            for f in files:
                lines.append(f"{sub_indent}{f}")
        return "\n".join(lines)