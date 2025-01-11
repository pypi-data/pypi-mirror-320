############################################
# Takes as input preprocessed sources and substitutes all real declaration with RPE variables.
# Fixes all incoherence that can arise from these changes
# Produces a vault with the info on these new sources produced.
############################################
from AutoRPE.UtilsRPE.ImplementRPE import Implement_RPE
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision

from os import mkdir
from os.path import isdir
from shutil import rmtree
import random

import argparse


def load_list_of_files_to_keep_unmodified(filename):
    from os.path import isfile
    if isfile(filename):
        print("Loading list of exceptions from %s\n\n" % filename)
        with open(filename) as f:
            return [l.strip() for l in f if l.strip() and l.strip()[0] != "#"]
    else:
        return None


def load_list_of_real_to_keep_unmodified(filename):
    from os.path import isfile
    import AutoRPE.UtilsRPE.Error as Error
    list_to_return = []
    if isfile(filename):
        print("Loading list of exceptions from %s\n\n" % filename)
        with open(filename) as f:
            for l in f:
                if l.strip() and l.strip()[0] != "#":
                    data = l.strip().split(";")
                    list_to_return.append({
                        "var_name": data[0],
                        "module": data[1],
                        "derived_type": data[2]
                    })
        return list_to_return
    else:
        raise Error.ExceptionNotManaged("No black list file found")


def get_parser() -> argparse.ArgumentParser:
    from AutoRPE.UtilsRPE.Error import PathType
    from os.path import isfile, abspath, dirname

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-sources", required=True, type=PathType(exists=True, type='dir'),
                        help="Path to a folder that contains the preprocessed code source.")
    parser.add_argument("-o", "--output-sources", default="SourcesWithRPE",
                        help="Path to the folder that will contain the AutoRPE implementation.")
    parser.add_argument("--database-name", default="vault.pkl",
                        help="Filename of the output database.")
    parser.add_argument("--black-list-file",
                        default=dirname(abspath(__file__)) + "/../AdditionalFiles/list_of_files_to_keep_unmodified.txt",
                        help="Name of files that should maintain REAL variables declarations.")
    parser.add_argument("--namelist-path", default="namelist_precisions",
                        help="Path to the output namelist that will specify all variables' precision.")

    return parser


def get_command_line_arguments():
    parser = get_parser()
    return parser.parse_args()



def main():
    seed_value = 0
    print(f"Set seed to {seed_value}.\n")
    random.seed(seed_value)
    args = get_command_line_arguments()

    path_to_input_sources = args.input_sources
    path_to_output_sources = args.output_sources
    output_vault = args.database_name
    namelist_path = args.namelist_path
    black_list_file = args.black_list_file
    # Set working precision
    VariablePrecision.set_working_precision('dp')
    # Paths to source folders
    if isdir(path_to_output_sources):
        rmtree(path_to_output_sources)
    mkdir(path_to_output_sources)

    print("Starting the implementation of the reduced precision emulator in:\n   %s\n\n" % path_to_input_sources)

    # List of files that should not be processed, as red from "list_of_files_to_keep_unmodified.txt"
    preprocess_files_blacklist = load_list_of_files_to_keep_unmodified(black_list_file)

    # Format text + replace real declarations with type(rpe_var)
    vault = Implement_RPE(path_to_input_sources, path_to_output_sources, preprocess_files_blacklist)

    # Generate the namelist
    vault.generate_namelist_precisions(namelist_path)

    vault.save(output_vault)


if __name__ == "__main__":
    main()
