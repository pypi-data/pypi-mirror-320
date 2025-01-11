############################################
# Purpose: This script can be used to take a namelist and adapt it once the code had the RPE implemented.
#
# Inputs:
#        -v , --vault  path to the vault generated when implementing the RPE.
#        namelists to modify, as arguments.
#        i.e. python AdaptNamelist.py -v vault.pkl namelist_cfg namelist_ref
#
#
############################################
from AutoRPE.UtilsRPE.Classes.Vault import load_vault
import re
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import argparse


def get_namelist_name(_line):
    """
    Return the namelist name if found
    """
    _line = _line.strip()
    if not _line:
        return False
    first_character = _line[0]
    if first_character == "&":
        if _line.count("!"):
            _line = _line[:_line.find("!")]
        return _line[1:].strip()
    return False


def line_is_assignation(_line):
    """
    Determine whether the string provided is a assignation.
    """
    _line = _line.strip()
    if not _line:
        return False
    first_character = _line[0]
    if first_character in ["!", "&"]:
        return False
    if _line.count("!"):
        _line = _line[:_line.find("!")]
    if _line.count("="):
        return True
    return False


def get_parser() -> argparse.ArgumentParser:

    help_text = """
    This script takes as arguments the path to the vault (-v/--vault) 
    created by SourcesWithRPE and a list of the namelist paths.
    """
    #parser = argparse.ArgumentParser(usage=help_text)
    parser = argparse.ArgumentParser()

    parser.add_argument('--database', required=True, type=Error.PathType(exists=True, type='file'),
                        help="Path to a database (vault) generated with MakeVault.")

    parser.add_argument('--namelist', required=True, type=Error.PathType(exists=True, type="file"), nargs='+',
                        help='List of namelist files.')

    return parser


def get_command_line_arguments():
    parser = get_parser()
    return parser.parse_args()



def main():
    args = get_command_line_arguments()
    vault_path = args.database
    namelists = args.namelist

    # Load vault
    vault = load_vault(vault_path)

    # Loop over all the namelists
    for namelist in namelists:
        # Open the file and read the content
        with open(namelist) as f:
            data = [line for line in f]
            # Loop over all the lines
            for index, _l in enumerate(data):
                # In case the line corresponds to an assignation
                _name = get_namelist_name(_l)
                if _name:
                    namelist_name = _name
                elif line_is_assignation(_l):
                    # Use regex to read the variable name and the assigned value
                    m = re.search(RegexPattern.assignation_val, _l)
                    var, value = m.groups()
                    # Use the vault to determine the type of the variable
                    try:
                        variable = vault.get_variable_from_namelist_by_name(var.strip(), namelist_name)
                    except Error.VariableNotFound:
                        # A namelist not read in the code has been hit ( probably excluded via preprocessor flag)
                        continue

                    # In case the variable is a rpe_var, add a %val suffix
                    if variable.type == "rpe_var":
                        var = "%s%%val" % var.strip()
                        data[index] = "%s = %s\n" % (var, value)
                    # In case the variable is a fld_n derived type, add a custom fix
                    elif variable.type == "fld_n":
                        split_value = value.split(",")
                        # Add -1 to the first position of the list
                        #value = value.replace(split_value[1], "-1, " + split_value[1]+ ",-1")
                        value = value.replace(split_value[1], "-1, " + split_value[1])
                        data[index] = "%s = %s" % (var, value)
                else:
                    continue

            # Join all the lines
            text = "".join(data)
        # Overwrite the namelist with the fixes
        with open(namelist, "w") as f:
            f.write(text)

if __name__ == "__main__":
    main()
