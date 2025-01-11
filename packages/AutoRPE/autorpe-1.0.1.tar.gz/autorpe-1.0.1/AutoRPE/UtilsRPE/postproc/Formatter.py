import subprocess
from pathlib import Path

def format_fortran_content(filepath: Path, indent_width: int = 4):
    """
    Reads Fortran file content, formats it using fprettify, and rewrites it.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if not filepath.exists() or filepath.suffix not in [".f90", ".f", ".f95", ".f08"]:
        print(f"Skipping unsupported or missing file: {filepath}")
        return
    
    try:
        # Run fprettify with input piped to subprocess
        result = subprocess.run(
            ["fprettify", f"-i{indent_width}", "-"],
            input=filepath.read_text(),
            text=True,
            capture_output=True,
            check=True,
        )
        # Write formatted output back to the file
        filepath.write_text(result.stdout)
        # print(f"Formatted: {filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error formatting {filepath}: {e}")
