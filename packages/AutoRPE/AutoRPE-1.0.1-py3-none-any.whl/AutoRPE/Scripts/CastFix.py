import AutoRPE.UtilsRPE.postproc.AddCast as AddCast
import AutoRPE.UtilsRPE.Classes.Vault as Vault
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.postproc.UpdateVariablesPrecision as UpdateVariablesPrecision
from os.path import isdir, isfile
from os import mkdir
from shutil import rmtree
from distutils.dir_util import copy_tree
import pickle
import sys
import argparse


def create_output_folder(original_input_src, new_folder_name):
    folder_list = []
    if isdir(new_folder_name):
        rmtree(new_folder_name)
    mkdir(new_folder_name)
    for folder in original_input_src:
        sub_folder_name = folder.split("/")[-1]
        folder_list.append(new_folder_name + "/" + sub_folder_name)
        copy_tree(folder, new_folder_name + "/" + sub_folder_name)
    return folder_list


def get_parser() -> argparse.ArgumentParser:
    from AutoRPE.UtilsRPE.Error import PathType

    parser = argparse.ArgumentParser()
    parser.add_argument("--preprocessed-input-files", required=True, type=PathType(exists=True, type="dir"), nargs='+',
                        help="Path to the preprocessed sources.")
    parser.add_argument("--original-input-files", required=True, type=PathType(exists=True, type="dir"), nargs='+',
                        help="Path to the non-preprocessed sources.")
    parser.add_argument("--output-folder", required=True,
                        help="Path where the mixed-precision version of the sources will be stored.")
    parser.add_argument("--root-namelist", required=True, type=PathType(exists=True, type='file'),
                        help="Path to the configuration used to run the root node.")
    parser.add_argument("--vault", default=None, type=PathType(exists=True, type="file"),
                        help="Path to the database. For debug purposes, once it is created, it can be recycled for further runs.")
    parser.add_argument("--database-name", default="vault.pkl",
                        help="Filename of the output database.")
    parser.add_argument("--dictionary_of_casts", default=None,
                        help="Dictionary containing all the necessary casts; it only needs to be created once.")

    return parser


def get_command_line_arguments():
    parser = get_parser()
    return parser.parse_args()


def main():
    from os.path import isdir
    from os import mkdir
    from shutil import rmtree
    from distutils.dir_util import copy_tree

    args = get_command_line_arguments()

    root_namelist = args.root_namelist
    vault_path = args.vault
    preprocessed_input_files = args.preprocessed_input_files
    original_input_files = args.original_input_files
    output_folder = args.output_folder
    vault = args.vault
    database_name = args.database_name
    dictionary_exists = args.dictionary_of_casts

    output_src = create_output_folder(original_input_files, output_folder)

    # Set working precision to double, since it the way the code has been compiled
    VariablePrecision.set_working_precision('dp')
    if not vault:
        vault = Vault.create_database(preprocessed_input_files, extension=".f90")
        vault.save("vault.pkl")
    else:
        # This is useful when debugging and it is not needed to generate a vault at every run
        vault = Vault.load_vault(vault)

    # Propagate dependencies and add non analyzed variables
    banned_variables, single_precision_variables = UpdateVariablesPrecision.get_var_to_convert(root_namelist, vault)

    # Set working precision to single, so as to find the needed fixes
    VariablePrecision.set_working_precision('sp')

    # Generate a dictionary with the list of call to fix, and an additional list of variables to put to dp
    if not dictionary_exists:
        list_of_variables, dictionary_of_cast, reshape_fix = AddCast.get_cast_dictionary(vault)
        file = open('dictionary.pkl', 'wb')
        sys.setrecursionlimit(10000)
        pickle.dump(list_of_variables, file)
        pickle.dump(dictionary_of_cast, file)
        file.close()
    else:
        file = open('dictionary.pkl', 'rb')
        list_of_variables = pickle.load(file)
        dictionary_of_cast = pickle.load(file)
        file.close()
    # Load files that will be modified
    original_modules = BasicFunctions.load_sources(output_src, extension=[".F90", ".h90", ".f90"])

    list_of_variables += single_precision_variables + banned_variables


    # Update the precision of variables in original files
    UpdateVariablesPrecision.update_variables_precision(original_modules, list_of_variables)

    # Remove preprocessors cast added in previous implementation
    UpdateVariablesPrecision.remove_CAST(original_modules)

    # Add needed casts
    fixed_modules = AddCast.add_casts(original_modules, dictionary_of_cast)

    # Save fixed sources
    for module in fixed_modules:
        module.save_file()


if __name__ == "__main__":
    main()
