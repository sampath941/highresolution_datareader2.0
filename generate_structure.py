import os

def generate_structure(start_path, ignore=None, indent=''):
    if ignore is None:
        ignore = {'__pycache__', '.git', 'temporary_files', '.vscode', 'event_codes.json'}

    for root, dirs, files in os.walk(start_path):
        # Modify dirs to filter out unwanted names and any directory containing "venv"
        dirs[:] = [d for d in dirs if d not in ignore and 'venv' not in d]

        # Modify files to filter out unwanted file extensions
        files = [f for f in files if not (f.endswith('.pyc') or f.endswith('.pyo'))]

        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

# Use the function and write output to a file
output_file = "project_structure.txt"
with open(output_file, 'w') as f:
    # Redirect print to file
    original_stdout = os.sys.stdout
    os.sys.stdout = f
    generate_structure('.')
    os.sys.stdout = original_stdout

print(f"Project structure saved to {output_file}")