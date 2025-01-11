from __future__ import print_function
from os.path import dirname, abspath, isfile
import numpy as np


# Get all files contained in a source path (recursive)
def expand_sources(source_path: str):
    """
    Recursively gets all source files with a Fortran extension (.f, .F, .f90, .F90)
    from the specified directory.

    Parameters:
        source_path (str): The directory to search for source files.

    Returns:
        list: A sorted list of file paths matching the Fortran source file pattern.

    Raises:
        OSError: If there is an issue accessing the directory.
    """
    from os import walk
    from os.path import join
    import re
    pattern = r".*\.[fFh90]"
    files = [join(dp, f) for dp, dn, fn in walk(source_path) for f in fn]
    files = [f for f in files if re.search(pattern, f)]
    # Sorting the list to solve the random-like behaviour of walk
    files = list(sorted(files))
    return files


# Gets the file path of the corresponding module
def match_module_and_filename(module: str, filenames: list[str]):
    """
    Returns a list of filenames matching the module name with a Fortran extension.

    Parameters:
        module (str): The module name to search for.
        filenames (list[str]): A list of filenames to search through.

    Returns:
        list: A list of filenames that match the module name and Fortran extension.
    """
    import re
    pattern = r".*/%s\.[fFh90]" % module
    matches = [fn for fn in filenames if re.match(pattern, fn)]
    return matches


def load_intrinsics():
    """
    Loads the list of Fortran intrinsics from a hardcoded file.

    Returns:
        dict: A dictionary mapping the lowercase name of each intrinsic to its corresponding name.
    """
    package_directory = dirname(abspath(__file__))
    # Hardcoded path to file.
    with open(package_directory + "/../AdditionalFiles/fortran_intrinsics") as f:
        intrinsics = dict((intrinsic.split(',')[0].lower(), intrinsic.split(',')[1]) for intrinsic in f)

    return intrinsics


def load_variable_list(filename: str, vault: 'Vault', is_used: bool=False, precision: bool=False):
    """
    Loads and processes a list of banned variables from a file, with options to
    separate by usage or apply precision settings.

    Parameters:
        filename (str): The path to the file containing variable data.
        vault (object): The vault containing variable data to be matched.
        is_used (bool): If True, separates variables by whether they are used or not.
        precision (bool): If True, applies precision settings to variables.

    Returns:
        list: A list of variables (or two lists if `is_used` is True).
    """
    from numpy import genfromtxt
    if filename is None:
        return []
    # Firs column will be ids of variables, second a separator. Third column: variable name
    var_name = genfromtxt(filename, dtype='str', usecols=2)
    # Fourth column the variable subprogram
    var_procedure = genfromtxt(filename, dtype='str', usecols=3)
    # Fifth column: variable module
    var_module = genfromtxt(filename, dtype='str', usecols=4)

    # If there is just one banned variable in the file, we need to convert these to 1d arrays:
    if var_name.ndim == 0:
        var_name = np.atleast_1d(var_name)
        var_procedure = np.atleast_1d(var_procedure)
        var_module = np.atleast_1d(var_module)

    list_of_variables = []
    for v_name, v_procedure, v_module in zip(var_name, var_procedure, var_module):
        variable = vault.get_variable_by_info(v_name, v_procedure, v_module)
        list_of_variables.append(variable)

    if is_used:
        # On the last column there can be if the variables was used or not
        usage = genfromtxt(filename, dtype='str', usecols=5)
        # Separate the list between used or not
        return [[v for index, v in enumerate(list_of_variables) if usage[index] == 'T'],
                [v for index, v in enumerate(list_of_variables) if usage[index] == 'F']]
    elif precision:
        precision = genfromtxt(filename, dtype='int', usecols=5)
        # set the final precision
        for var, prec in zip(list_of_variables, precision):
            if prec == 10:
                var.type = 'hp'
            elif prec == 23:
                var.type = 'wp'
            else:
                var.type = 'dp'
        return list_of_variables
    else:
        # Simply return the list
        return list_of_variables


# Hardcoded list, this should be solved
list_of_intrinsics_2fix = ["max", "maxloc", "maxval", "min", "minloc", "minval", "epsilon",
                           "isnan", "count", "abs", "mod", "reshape",
                           "atanh", "sqrt", "log",
                           "sum",
                           "erfc",
                           "merge",
                           "dsqrt", "cmplx", "transfer",
                           "matmul", "dot_product"]

Fortran_builtins = ["dimension", "intent", "type",
                    "if", "elseif", "elsewhere", "while",
                    "allocate", "deallocate",
                    "write", "read", "open", "inquire", "close",
                    "where", "case", "character", "format", "flush", "rewind"]

list_of_key = ["dim", "mask", "kind", "back"]

comparison_operators = [">=", "<=", "==", "/=", ">", "<", ".not.", ".or.", ".and.", ".false.", ".true."]

allowed_externals = ['histwrite',
                     'NF90_GET_VAR',
                     'histbeg',
                     'xios_recv_field',
                     'NF90_PUT_VAR',
                     'wheneq'
                     ]
# List of all the intrinsic
list_of_intrinsics = load_intrinsics()


def load_list_of_files_to_keep_unmodified(filename: str=None):
    """
    Loads a list of files to keep unmodified from a specified file (defaults to a hardcoded path).
    Returns a list of file paths, excluding comments.

    Parameters:
        filename (str, optional): The path to the file containing the list of files. 
            Defaults to a hardcoded path.

    Returns:
        list: A list of file paths to keep unmodified.
    """
    if filename is None:
        package_directory = dirname(abspath(__file__))
        filename = package_directory + "/../AdditionalFiles/list_of_files_to_keep_unmodified.txt"
    # Hardcoded path to file.
    if isfile(filename):
        print("Loading list of exceptions from %s\n\n" % filename)
        with open(filename) as f:
            return [l.strip() for l in f if l.strip() and l.strip()[0] != "#"]
    else:
        return None
