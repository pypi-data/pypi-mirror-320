import argparse

def create_output_folder(original_input_src, new_folder_name):
    from shutil import rmtree, copytree
    from os.path import isdir
    folder_list = []
    if isdir(new_folder_name):
        rmtree(new_folder_name)
    copytree(original_input_src, new_folder_name)
    return folder_list


def get_parser() -> argparse.ArgumentParser:
    from AutoRPE.UtilsRPE.Error import PathType

    parser = argparse.ArgumentParser()
    parser.add_argument("--preprocessed-input-files", required=True, type=PathType(exists=True, type="dir"),
                        help="Path to the preprocessed sources.")
    parser.add_argument("--output-folder", required=True, type=PathType(exists=True, type='dir'),
                        help="Path where the mixed-precision version of the sources will be stored.")
    parser.add_argument("--root-namelist", required=True, type=PathType(exists=True, type='file'),
                        help="Path to the configuration used to run the root node.")
    parser.add_argument("--vault", default=None, type=PathType(exists=True, type="file"),
                        help="Path to the database. For debug purposes, once it is created, it can be recycled for further runs.")
    parser.add_argument("--database-name", default="vault.pkl",
                        help="Filename of the output database.")
    return parser


def get_command_line_arguments():
    parser = get_parser()
    return parser.parse_args()


def main():
    import AutoRPE.UtilsRPE.postproc.AddCast as AddCast
    import AutoRPE.UtilsRPE.Classes.Vault as Vault
    import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
    import AutoRPE.UtilsRPE.postproc.UpdateVariablesPrecision as UpdateVariablesPrecision

    args = get_command_line_arguments()

    root_namelist = args.root_namelist
    preprocessed_input_files = args.preprocessed_input_files
    output_folder = args.output_folder
    vault = args.vault
    database_name = args.database_name

    # Set working precision to double, since it the way the code has been compiled
    VariablePrecision.set_working_precision('dp')
    if not vault:
        vault = Vault.create_database(preprocessed_input_files, extension=".f90")
    else:
        # This is useful when debugging and it is not needed to generate a vault at every run
        vault = Vault.load_vault(vault)

    # Propagate dependencies and add non analyzed variables
    banned_variables, single_precision_variables = UpdateVariablesPrecision.get_var_to_convert(root_namelist, vault)

    # Set working precision to single, so as to find the needed fixes
    VariablePrecision.set_working_precision('sp')

    # Generate a dictionary with the list of call to fix, and an additional list of variables to put to dp
    list_of_variables, dictionary_of_cast, reshape_fix = AddCast.get_cast_dictionary(vault)

    # Update the precision of variables in original files
    list_of_variables += single_precision_variables + banned_variables

    UpdateVariablesPrecision.update_variables_precision_preproc(vault, list_of_variables)

    # Add needed casts
    AddCast.new_add_casts(dictionary_of_cast)

    # Save fixed sources
    for module in vault.modules.values():
        module.save_file(output_folder)


if __name__ == "__main__":
    main()
