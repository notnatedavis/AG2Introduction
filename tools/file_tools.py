#   tools/file_tools.py
#   File system operations and browser opening

# ----- Imports -----
import os
import webbrowser

# ----- Helper Functions -----
def write_file(content: str, filename: str) -> str :
    # write content to a file and return the absolute path
    with open(filename, "w") as f :
        f.write(content)
    return os.path.abspath(filename)

def write_html_file(content: str, filename: str = "index.html") -> str :
    # write HTML content to a file and open it in the browser
    abs_path = write_file(content, filename)
    webbrowser.open(f"file://{abs_path}")
    return f"File {filename} has been created and opened in your browser."