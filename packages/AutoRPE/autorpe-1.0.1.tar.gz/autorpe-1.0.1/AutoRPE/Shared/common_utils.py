import inspect
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from shutil import copytree, rmtree
from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass
import logging


import pytest


# Check for FC90 in the environment; fallback to 'gfortran' if not defined
COMPILER = os.environ.get("FC90", "gfortran")


def get_importing_script_path():
    """
    Retrieve the path of the script that imported the current module.

    This function inspects the call stack, filters out internal/builtin modules,
    removes duplicates while preserving order, and returns the directory of the 
    first valid user-defined script that imported this module.

    Returns:
        Path: The parent directory of the script that imported the module.
    """
    seen = set()
    files = [
        Path(frame.filename).resolve()
        for frame in inspect.stack()
        if "importlib" not in frame.filename and "<frozen" not in frame.filename
        and not (frame.filename in seen or seen.add(frame.filename))
    ]
    
    # files[0] is this file; files[1] is the script that imported this module
    return files[1].parent if len(files) > 1 else Path(__file__).resolve().parent



class CompilationError(Exception):
    """Error to handle compilation errors."""

def compile_fortran_sources(
    directory: Path,
    output_executable: str,
    include_dirs: Optional[List[Path]] = None,
    additional_objects: Optional[List[Path]] = None
) -> None:
    """
    Compiles Fortran source files in a given directory, respecting module dependencies,
    and links them to create an executable.

    Args:
        directory (Path): The directory containing Fortran source files.
        output_executable (str): The path to the output executable file.
        include_dirs (Optional[List[Path]]): List of directories to include during compilation.
        additional_objects (Optional[List[Path]]): List of additional object files to include during linking.

    Returns:
        subprocess.CompletedProcess: The result of the final linking subprocess call.

    Raises:
        FileNotFoundError: If no Fortran source files are found in the directory.
        RuntimeError: If compilation or linking fails.
    """
    print(f"Using compiler: {COMPILER}")
    directory = Path(directory)
    # Find all Fortran source files (*.f90) in the directory
    sources: List[Path] = sorted(directory.glob("*.f90"))
    if not sources:
        raise FileNotFoundError(f"No Fortran sources found in {directory}")

    # Prepare include flags for the compiler
    include_flags: List[str] = []
    if include_dirs:
        include_flags = [f"-I{str(inc_dir)}" for inc_dir in include_dirs]

    # Build dictionaries to store module definitions and usages
    module_defs: Dict[str, Path] = {}  # Maps module names to source files where they're defined
    module_uses: Dict[Path, Set[str]] = defaultdict(set)  # Maps source files to modules they use

    # Regular expressions to match module definitions and usage
    module_def_regex = re.compile(r'^\s*module\s+(\w+)', re.IGNORECASE)
    use_module_regex = re.compile(r'^\s*use\s*(?:,.*::\s*)?(\w+)', re.IGNORECASE)

    # Parse each source file to find module definitions and usages
    for source in sources:
        with open(source, 'r') as f:
            for line in f:
                # Check for module definitions (exclude submodules and interfaces)
                match_def = module_def_regex.match(line)
                if match_def and 'procedure' not in line.lower():
                    module_name = match_def.group(1).lower()
                    module_defs[module_name] = source
                # Check for module usage
                match_use = use_module_regex.match(line)
                if match_use:
                    used_module = match_use.group(1).lower()
                    module_uses[source].add(used_module)

    # Build a dependency graph mapping each source file to its dependencies
    dependencies: Dict[Path, Set[Path]] = defaultdict(set)  # source_file -> set of source_files it depends on
    for src, used_modules in module_uses.items():
        for mod in used_modules:
            if mod in module_defs:
                dependencies[src].add(module_defs[mod])

    # Perform a topological sort to determine the correct compilation order
    temp_mark: Set[Path] = set()
    perm_mark: Set[Path] = set()
    ordered_sources: List[Path] = []

    def visit(node: Path):
        """
        Recursive helper function for topological sort.

        Args:
            node (Path): The source file to visit.

        Raises:
            RuntimeError: If a circular dependency is detected.
        """
        if node in perm_mark:
            return
        if node in temp_mark:
            raise CompilationError(f"Circular dependency detected at {node}")
        temp_mark.add(node)
        for dep in dependencies.get(node, []):
            visit(dep)
        temp_mark.remove(node)
        perm_mark.add(node)
        ordered_sources.append(node)

    # Visit all source files to perform the topological sort
    for src in sources:
        if src not in perm_mark:
            visit(src)

    # No need to reverse ordered_sources; the topological sort provides correct order
    # Compile each source file in the determined order
    object_files: List[Path] = []
    for source in ordered_sources:
        object_file = source.with_suffix(".o")
        # Command to compile the source file
        command = [COMPILER, "-ffree-line-length-none", "-v", "-c", str(source), "-J", str(directory), *include_flags, "-o", str(object_file)]
        print("Compiling:", " ".join(command))
        # Run the compilation command
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            # Compilation failed; print error and raise exception
            print(f"Error compiling {source}:\n{result.stderr}")
            raise CompilationError(f"Failed to compile {source}:\n{result.stderr}")
        object_files.append(object_file)

    # Link all object files and any additional objects to create the executable
    command = ["gfortran", *include_flags, *[str(obj) for obj in object_files]]
    if additional_objects:
        command.extend(map(str, additional_objects))
    command.extend(["-o", str(output_executable)])
    print("Linking:", " ".join(command))
    # Run the linking command
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        # Linking failed; print error and raise exception
        print(f"Error linking executable:\n{result.stderr}")
        raise CompilationError(f"Failed to link objects to create executable:\n{result.stderr}")


# Define paths
TEST_SCRIPT_PATH = get_importing_script_path()


RPE_PATH = TEST_SCRIPT_PATH / "rpe"
LOCAL_CACHE_DIR = Path.home() / ".local" / "rpe_repo_cache"


def clone_repository(repo_url: str, cache_dir: Path, dest_path: Path):
    """
    Clone the repository if not already cached locally, and copy it to the destination.
    """
    # Check if the repository is already cached
    if not cache_dir.exists():
        print(f"Repository not found in cache. Cloning to {cache_dir}...")
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        clone_command = ["git", "clone", repo_url, str(cache_dir)]
        result = subprocess.run(clone_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        print(f"Repository cloned successfully:\n{result.stdout}")
    else:
        print(f"Using cached repository from {cache_dir}.")

    # Copy the cached repository to the test directory
    if dest_path.exists():
        rmtree(dest_path)
    try:
        copytree(src=cache_dir, dst=dest_path)
        print(f"Copied repository from cache to {dest_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to copy repository from cache: {e}")


def build_tool(build_dir: Path, f90_compiler: str = "gfortran"):
    """
    Build the tool using Make in the specified directory.
    """
    build_command = "make"
    result = subprocess.run(
        build_command,
        cwd=build_dir,
        env={**os.environ, "F90": f90_compiler},
        capture_output=True,
        text=True,
        shell=True
    )
    print(f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    if result.returncode != 0:
        raise RuntimeError(
            f"Build failed:\n"
            f"Working directory: {build_dir}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    print(f"Build succeeded:\n{result.stdout}")


def cleanup_directory(path: Path):
    """
    Remove the specified directory if it exists.
    """
    if path.exists():
        rmtree(path)
        print(f"Cleaned up directory: {path}")


# Pytest fixture
@pytest.fixture(scope="session")
def setup_and_cleanup_rpe():
    """
    Fixture to set up the RPE tool and clean up after tests.
    """
    repo_url = "https://github.com/sparonuz/rpe.git"
    try:
        # Step 1: Clone the repository
        clone_repository(repo_url, cache_dir=LOCAL_CACHE_DIR, dest_path=RPE_PATH)

        # Step 2: Build the tool
        build_tool(RPE_PATH)

        # Yield control back to the tests
        yield
    finally:
        # Step 3: Cleanup
        cleanup_directory(RPE_PATH)


def setup_rpe():
    """
    Sets up the RPE tool.
    """
    repo_url = "https://github.com/sparonuz/rpe.git"
    print("Cloning repository...")
    clone_repository(repo_url, cache_dir=LOCAL_CACHE_DIR, dest_path=RPE_PATH)
    print("Building the tool...")
    build_tool(RPE_PATH)
    print("Setup completed.")
    return RPE_PATH


def cleanup_rpe():
    """
    Cleans up the RPE tool directory.
    """
    print("Cleaning up...")
    cleanup_directory(RPE_PATH)
    print("Cleanup completed.")


# Pytest fixture
@pytest.fixture(scope="session")
def setup_and_cleanup_rpe():
    """
    Pytest fixture to set up the RPE tool and clean up after tests.
    """
    setup_rpe()
    try:
        yield  # Yield control to the tests
    finally:
        cleanup_rpe()


# Some utilities to launch the compiled binaries
@dataclass
class Answer:
    return_code: int
    stdout: str
    stderr: str


class BinaryNotFound(Exception):
    ...


def launch_command(command: List[str]) -> Answer:
    """
    Launch a given command in bash and return an Answer object which includes the return code,
    the stdout and the stderr.
    :param command:
    :return:
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return Answer(process.returncode, stdout.decode(), stderr.decode())


class Executable:
    """
    Class to wrap a system executable and easily launch commands with it.
    """
    def __init__(self, binary_path: Union[Path, str]):
        if not isinstance(binary_path, Path):
            binary_path = Path(binary_path)
        self.name = binary_path.name
        self.binary_path = binary_path

    def __call__(self, *args) -> Answer:
        """
        Calls the binary with the provided arguments and returns an Answer object
        :param args:
        :return:
        """
        command = [self.binary_path, *args]
        answer = launch_command(command)
        if answer.stderr.strip():
            logging.warning(answer.stderr)
        return answer



if __name__ == "__main__":
    build_tool(RPE_PATH)