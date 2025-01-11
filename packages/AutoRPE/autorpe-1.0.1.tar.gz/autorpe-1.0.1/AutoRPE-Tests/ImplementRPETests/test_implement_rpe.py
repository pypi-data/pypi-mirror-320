import pytest
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import TemporaryDirectory
from AutoRPE.UtilsRPE.ImplementRPE import Implement_RPE
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
from AutoRPE.Shared.common_utils import compile_fortran_sources, CompilationError, setup_and_cleanup_rpe


# Define the base paths relative to this script
TEST_SCRIPT_PATH = Path(__file__).parent
SOURCES_PATH = TEST_SCRIPT_PATH / "sources"
RPE_PATH = TEST_SCRIPT_PATH / "rpe"
RPE_OBJECT_FILE = RPE_PATH / "src/rp_emulator.o"
RPE_MODULE_PATH = RPE_PATH / "modules"  # Path to rp_emulator.mod




# Helper function to apply the tool to a directory
def apply_tool(input_dir, output_dir, vault_path, namelist_path):
    if output_dir.exists():
        rmtree(output_dir)
    output_dir.mkdir(parents=True)
    VariablePrecision.set_working_precision('dp')
    preprocess_files_blacklist = []
    vault = Implement_RPE(str(input_dir), str(output_dir), preprocess_files_blacklist)
    vault.generate_namelist_precisions(str(namelist_path))
    vault.save(str(vault_path))


# Test each example
@pytest.mark.parametrize("example_folder", [f for f in SOURCES_PATH.iterdir() if f.is_dir()], ids=lambda folder: folder.name)
@pytest.mark.usefixtures("setup_and_cleanup_rpe")
def test_example_folder(example_folder):

    with TemporaryDirectory() as temp_dir:
        # Copy the test case folder to the temporary directory
        temp_test_folder = Path(temp_dir) / example_folder.name
        copytree(example_folder, temp_test_folder)

        output_executable_original = Path(temp_dir) / "original.out"
        output_executable_transformed = Path(temp_dir) / "transformed.out"
        output_sources = Path(temp_dir) / "output_sources"
        vault_path = Path(temp_dir) / "vault.pkl"
        namelist_path = Path(temp_dir) / "precision.namelist"

        # Step 1: Compile the original code
        try:
            compile_fortran_sources(temp_test_folder, str(output_executable_original))
        except CompilationError as err:
            raise CompilationError("First compilation: "+str(err))
        
        # Step 2: Apply the tool
        try:
            apply_tool(temp_test_folder, output_sources, vault_path, namelist_path)
        except Exception as err:
            raise AssertionError("ImplementRPE failed: "+str(err)) from err


        # Step 3: Compile the transformed code with the required object file and module directory
        try:
            compile_fortran_sources(
                output_sources,
                str(output_executable_transformed),
                include_dirs=[RPE_MODULE_PATH],
                additional_objects=[RPE_OBJECT_FILE]
            )
        except CompilationError as err:
            raise CompilationError("Second compilation: "+str(err))
        
