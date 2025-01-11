# This module its only used to pass to the imported modules which is the working_precision.
# The working precision might differ in different scenarios:
# i.e. double precision when implementing the emulator, single precision when modifying the code.

class UndefinedPrecision:
    """
    A class to represent an undefined precision.

    Attributes:
        name (str): The name of the undefined precision type.
    """
    def __init__(self, name) -> None:
        self.name = name
    ...

# I'll keep double by default, so everything will work as before except in the places where we specifically change it
# Used in track dependency
type2precision = {"dp": 52, "sp": 23}
real_id = {'hp': 'hp', 'sp': 'sp', 'dp': 'dp', 'wp': 'wp'}
reduced_precision_id = {'hp': 'hp', 'sp': 'sp', 'wp': 'wp'}
lookup_table = {'default': 'wp',
                'wp': 'wp',
                'WP': 'wp',
                '8': 'dp',
                'dp': 'dp',
                'fbdp': 'dp',
                '4': 'sp',
                'sp': 'sp',
                'fbsp': 'sp',
                'wp_out': 'sp',
                'hp': 'hp',
                'jphook': 'dp',
                'scripdp': 'dp'
                }

# A string would not be updated correctly
value_of_working_precision = {'wp': 'dp'}

dictionary_of_possible_combination = {}
# RPE var combinations
dictionary_of_possible_combination[frozenset(["rpe_var", "complex"])] = "rpe_var"
dictionary_of_possible_combination[frozenset(["rpe_var", real_id["dp"]])] = "rpe_var"
dictionary_of_possible_combination[frozenset(["rpe_var", real_id["sp"]])] = "rpe_var"
dictionary_of_possible_combination[frozenset(["rpe_var", real_id["wp"]])] = "rpe_var"
dictionary_of_possible_combination[frozenset(["rpe_var", real_id["hp"]])] = "rpe_var"
dictionary_of_possible_combination[frozenset(["rpe_var", "integer"])] = "rpe_var"

# Complex combinations
dictionary_of_possible_combination[frozenset(["complex", real_id["dp"]])] = "complex"
dictionary_of_possible_combination[frozenset(["complex", real_id["sp"]])] = "complex"
dictionary_of_possible_combination[frozenset(["complex", real_id["wp"]])] = "complex"
dictionary_of_possible_combination[frozenset(["complex", real_id["hp"]])] = "complex"
dictionary_of_possible_combination[frozenset(["complex", "integer"])] = "complex"

# Working precision combinations
dictionary_of_possible_combination[frozenset([real_id["wp"], "integer"])] = real_id["wp"]
dictionary_of_possible_combination[frozenset([real_id["wp"], "dp"])] = real_id["dp"]
dictionary_of_possible_combination[frozenset([real_id["wp"], "sp"])] = real_id["wp"]
dictionary_of_possible_combination[frozenset([real_id["wp"], "hp"])] = real_id["wp"]

# Double precision combinations
dictionary_of_possible_combination[frozenset([real_id["dp"], real_id["sp"]])] = real_id["dp"]
dictionary_of_possible_combination[frozenset([real_id["dp"], real_id["hp"]])] = real_id["dp"]
dictionary_of_possible_combination[frozenset([real_id["dp"], "integer"])] = real_id["dp"]

# Single precision combinations
dictionary_of_possible_combination[frozenset([real_id["sp"], "integer"])] = real_id["sp"]

# Half precision combinations
dictionary_of_possible_combination[frozenset([real_id["hp"], "integer"])] = real_id["hp"]


# Char combinations used to modify strings:
dictionary_of_possible_combination[frozenset(["char", "integer"])] = "char"


def set_working_precision(working_precision: str):
    """
    Set the value of the working precision.

    Parameters:
        working_precision (str): The precision type to set (e.g., 'sp', 'dp', 'wp').
    """
    # Set the value of the working precision
    value_of_working_precision['wp'] = working_precision

def type_are_equivalent(type1: str, type2: str, working_precision: str=None):
    """
    Check if two types are equivalent, considering the working precision if needed.

    Parameters:
        type1 (str): The first type to compare.
        type2 (str): The second type to compare.
        working_precision (str, optional): The working precision to consider when one type is 'wp'.

    Returns:
        bool: True if the types are equivalent, False otherwise.
    """
    if working_precision is None:
        working_precision = value_of_working_precision['wp']
    type_set = set([type1, type2])
    if len(type_set) == 1:
        return True
    # In case a variable is wp, and the other has the actual precision specified
    if 'wp' in type_set:
        type_set.remove("wp")
        type_set.add(working_precision)
        if len(type_set) == 1:
            return True
    return False
