from typing import List, TYPE_CHECKING
import AutoRPE.UtilsRPE.Classes.Interface as Interface
from AutoRPE.UtilsRPE.Classes.Procedure import Procedure
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern

import re

# Add line to facilitate type checking without causing circular import
if TYPE_CHECKING:
    from AutoRPE.UtilsRPE.Classes.Vault import Vault


def get_variable(contents: str, procedure: Procedure=None, vault: 'Vault'=None, clean:bool =False):
    """
    Retrieves a variable based on its string representation, considering context.

    Parameters:
        contents (str): The string representation of the variable.
        procedure (Procedure, optional): The procedure context to search within.
        vault (Vault, optional): The vault containing metadata about the code.
        clean (bool): Whether to clean the string of operations and intrinsics.

    Returns:
        Variable: The variable object corresponding to the input string.

    Raises:
        VariableNotFound: If the variable is not found or the string does not represent a valid variable.
    """
    contents = contents.replace(" ", "").strip()

    contents = MaskCreator.remove_literals(contents)

    if clean:
        contents = BasicFunctions.remove_unary_operator(contents)
    if NatureDeterminer.has_intrinsics(contents):
        if clean:
            contents_no_intrinsic = MaskCreator.mask_intrinsics(contents)
            ret_val = []
            for c_no_i in contents_no_intrinsic:
                if not NatureDeterminer.is_a_number(c_no_i):
                    ret_val.append(get_variable(c_no_i, procedure, vault=vault))
            return ret_val
        else:
            raise Error.VariableNotFound("The string %s is not a variable" % contents)
    if NatureDeterminer.is_hardcoded_array(contents):
        raise Error.VariableNotFound("The string %s is not a variable" % contents)

    if NatureDeterminer.is_logical_comparison(contents):
        raise Error.VariableNotFound("The string %s is not a variable" % contents)

    split_elements = []
    if NatureDeterminer.has_operations(contents, split_elements):
        if clean:
            ret_val = []
            for el in split_elements:
                if not NatureDeterminer.is_a_number(el):
                    ret_val.append(get_variable(el, procedure, vault=vault))
            return ret_val
        else:
            raise Error.VariableNotFound("The string %s is not a variable" % contents)

    # Remove the indexing from array and DT:
    #   ght_abl <-- ght_abl(2:jpka)
    #   todelay%z1d <-- todelay(ji)%z1d(:)
    contents = BasicFunctions.remove_indexing(contents)

    if re.search(RegexPattern.variable, contents):
        try:
            return vault.get_variable_by_name(var_name=contents, procedure=procedure)
        except Error.VariableNotFound:
            raise Error.VariableNotFound

    if contents.count("%"):
        if contents.count("%val"):
            contents = contents.replace("%val", "")
            return get_variable(contents, procedure, vault)
        # Search for all others members
        try:
            return get_structure_member(contents, procedure, vault)
        except Error.MemberNotFound:
            raise Error.VariableNotFound

    if NatureDeterminer.is_keyword_argument(contents):
        # Removing before first =
        contents = contents[contents.find("=") + 1:].strip()
        return get_variable(contents, procedure, vault)

    raise Error.VariableNotFound("Variable %s: not found" % contents)


def get_pointer_assignment(line: str, vault: 'Vault', procedure: Procedure, var_type=VariablePrecision.real_id):
    """
    Finds pointer assignments in a line of code and retrieves the pointer variable and its target.

    Parameters:
        line (str): The line of code to analyze.
        vault (Vault): The vault containing metadata about the code.
        procedure (Procedure): The procedure context to search within.
        var_type (dict): A dictionary of valid types for the pointer.

    Returns:
        list[list]: A list containing the pointer and its target if found, or None.
    """

    if NatureDeterminer.is_pointer_assignment(line):
        ptr, target = _get_pointer_target(line, procedure, vault)
        if [ptr, target] != [None, None] and ptr.type in var_type:
            return [[ptr, target]]


def _get_pointer_target(line: str, procedure: Procedure, vault: 'Vault'):
    # Ignore the if condition. This is not an ideal solution, but the easier for the moment
    line = BasicFunctions.remove_if_condition(line)
    if line.count("::"):
        line = line.split("::")[1]
    pointer, target = line.strip().split("=>")
    pointer = pointer.strip()
    target = target.strip()

    # Sometimes indexing uses SIZE intrinsic than makes it impossible to find the variable pt4d(1:SIZE(ptab, dim=1))
    if NatureDeterminer.has_intrinsics(pointer):
        pointer = MaskCreator.mask_intrinsics(pointer)[0]

    if target.lower().replace(" ", "") == "null()":
        return [None, None]
    else:
        ptr = get_variable(pointer, procedure, vault)
        # Is a pointer to procedure
        # TODO this try except is outdated
        if ptr.type == 'procedure':
            try:
                target = vault.get_block_by_name(target.strip(), procedure.module.name)
                # It is a pointer to function, i.e. a variable is associated with it
                return ptr, target
            except Error.ProcedureNotFound:
                # It is a pointer to subroutine
                return [None, None]
        else:
            target = get_variable(target, procedure, vault)
    return ptr, target


def get_structure_member(contents: str, procedure: Procedure, vault: 'Vault'):
    """
    Retrieves the last member of a structure based on its string representation.

    Parameters:
        contents (str): The string representation of the structure.
        procedure (Procedure): The procedure context to search within.
        vault (Vault): The vault containing metadata about the code.

    Returns:
        Variable: The variable object corresponding to the last member of the structure.

    Raises:
        MemberNotFound: If the structure member is not found.
    """
    # The first part will be the root
    split_contents = contents.split("%", 1)

    # Find root variable
    root_variable = vault.get_variable_by_name(split_contents[0], procedure)

    # Search for root derived type definition
    root_dt = [dt for dt in vault.derived_types if dt.name.lower() == root_variable.type.lower()][0]
    if root_dt.is_external:
        return None

    # Iterate while it can be split by '%'
    while len(split_contents) > 1:
        # Check if it's a function call (procedure pointer)
        match = re.match(RegexPattern.call_to_function, split_contents[1])
        if match:
            member = match.group(1)
        else:
            split_contents = split_contents[1].split("%", 1)
            member = BasicFunctions.remove_indexing(split_contents[0])

        try:
            # Iterate the derived type variables and it's extension variables (type, extends(extended_t) :: my_t)
            search_array = root_dt.members + (root_dt.extension.members if root_dt.extension is not None else [])
            layer = [v for v in search_array if v.name.lower() == member.lower()][0]
        except IndexError:
            # We couldn't found the member
            raise Error.MemberNotFound

        # If type is procedure, we can return
        if layer.type == 'procedure':
            return layer

        try:
            # Search if the member is another dt
            root_dt = [dt for dt in vault.derived_types if dt.name.lower() == layer.type.lower()][0]
        except IndexError:
            # If split contents it's 1, it means that it's the final layer
            if len(split_contents) == 1 or layer.type == 'procedure':
                return layer
            else:
                raise Error.VariableNotFound("Variable %s not found", contents)

    return layer


def get_type_of_contents(contents: str, procedure: Procedure, vault: 'Vault'):
    """
    Determines the type of a given string of code.

    Parameters:
        contents (str): The string representation of the code.
        procedure (Procedure): The procedure context to analyze.
        vault (Vault): The vault containing metadata about the code.

    Returns:
        str: The type of the contents.

    Raises:
        TypeOfContent: If the type of the contents cannot be determined.
    """
    contents = contents.replace(" ", "").strip()

    # Try to facilitate checks
    contents = BasicFunctions.remove_unary_operator(contents)

    if contents.find("rpe_var(") == 0:
        return "rpe_var"

    # Check if is a call to function, including intrinsic
    if CallManager.is_call_to_function(contents, procedure, vault):
        return get_function_type(contents, procedure, vault)

    if BasicFunctions.contain_literals(contents, procedure.module.dictionary_of_masked_string):
        return "char"

    if NatureDeterminer.is_logical_comparison(contents):
        return "logical"

    # Check if is an hardcoded array, and return the content type
    hardcoded_array = []
    if NatureDeterminer.is_hardcoded_array(contents, hardcoded_array):
        contents = hardcoded_array[0]
        return get_type_of_contents(contents, procedure, vault)

    # After checking it is not an array we remove parenthesis
    contents = BasicFunctions.remove_outer_brackets(contents)

    split_elements = []
    if NatureDeterminer.has_operations(contents, split_elements):
        types = []
        for element in split_elements:
            types.append(get_type_of_contents(element, procedure, vault))

        # Remove any possible None
        types = set([t for t in types if (t is not None and t != "external")])
        if len(types) > 1:
            # Different types were used in the operation
            return BasicFunctions.combine_types(types)
        else:
            # Operands were all of the same type
            return types.pop()

    if NatureDeterminer.is_keyword_argument(contents):
        # Removing before first =
        contents = contents[contents.find("=") + 1:].strip()
        return get_type_of_contents(contents, procedure, vault)

    # Checks if it is a number
    num_type = NatureDeterminer.is_a_number(contents)
    if num_type:
        return num_type
    # # This function is vault agnostic, but the possibiliy of a function call
    # array = NatureDeterminer.is_an_array(contents)
    # if array:
    #     # Now the array will match with a simple variable
    #     contents = array

    # Remove the indexing from array and DT:
    #   ght_abl(2:jpka+b) --> ght_abl
    #   todelay(ji)%z1d(:) --> todelay%z1d
    clean_contents = BasicFunctions.remove_indexing(contents)

    # Remove exponentiation, so to identify variables :sla**(8.0_wp/3.0_wp) => sla
    clean_contents = MaskCreator.remove_pow(clean_contents)

    # Search if is a simple variable
    if re.search(RegexPattern.variable, clean_contents):
        var = vault.get_variable_by_name(clean_contents, procedure)
        return var.type

    # Check if is a derived data type
    if NatureDeterminer.is_struct_element(clean_contents):
        if clean_contents.split("%")[-1] == "val":
            return VariablePrecision.real_id['dp']
        member = get_structure_member(clean_contents, procedure, vault)
        if member:
            # If it's a procedure we need to make it recursive to get the function type
            if member.type == 'procedure':
                try:
                    # First it's a string
                    contents = member.is_pointer + contents.split(member.name, 1)[1]
                except TypeError:
                    # Later is a list of procedures
                    contents = member.is_pointer[0].name + contents.split(member.name, 1)[1]
                # Make it recursive for pointers to procedures
                return get_type_of_contents(contents, procedure, vault)
            else:
                return member.type
        else:
            # Case of an external data type
            return None
    raise Error.TypeOfContent(f"Type of content for the argument {contents!r}: not found")


def get_intrinsic_type(function_call: str, procedure: Procedure, vault: 'Vault'):
    """
    Determines the type of an intrinsic function call.

    Parameters:
        function_call (str): The string representation of the intrinsic function call.
        procedure (Procedure): The procedure context to analyze.
        vault (Vault): The vault containing metadata about the code.

    Returns:
        str: The type of the intrinsic function call.

    Raises:
        ValueError: If the intrinsic function type is not defined in the metadata.
    """
    function_name = CallManager.find_called_function(function_call)
    try:
        intrinsic_type = SourceManager.list_of_intrinsics[function_name.lower()]
    except KeyError:
        return None
    if intrinsic_type == 'content_type':
        if function_name.lower() == 'real':
            return get_type_of_real_cast(function_call)
        return get_type_of_contents(CallManager.find_call_arguments(function_call)[0], procedure, vault)
    elif intrinsic_type == 'wp':
        return VariablePrecision.real_id['wp']
    elif intrinsic_type in [None, 'None']:
        raise ValueError("Please add the type specification for this intrinsic: %s" % function_name)
    else:
        return intrinsic_type


def get_function_type(function_call, procedure: Procedure, vault: 'Vault'):
    """
    Determines the return type of a function call.

    Parameters:
        function_call (str): The string representation of the function call.
        procedure (Procedure): The procedure context to analyze.
        vault (Vault): The vault containing metadata about the code.

    Returns:
        str: The return type of the function.
    """
    # Check if is an intrinsic
    intrinsic = NatureDeterminer.has_intrinsics(function_call)
    # Avoid to match with function  that has intrinsic as argument: iom_axis(size(rd3,3)) is NOT an intrinsic
    if intrinsic == CallManager.find_called_function(function_call):
        return get_intrinsic_type(function_call, procedure, vault)
    else:
        # Must be a function stored in vault
        function_name = CallManager.find_called_function(function_call)
        function = vault.get_subprogram_by_name(function_name, block_type=['Function', 'Interface'])
        if isinstance(function, Interface.Interface):
            called_arguments = CallManager.find_call_arguments(function_call)
            function = get_interface(called_arguments, function, procedure, vault)
        return function.type


def get_dimension_of_contents(contents: str, block: Procedure, vault: 'Vault'):
    """
    Determines the dimensionality of a given variable or expression.

    Parameters:
        contents (str): The string representation of the variable or expression.
        block (Procedure): The procedure context to analyze.
        vault (Vault): The vault containing metadata about the code.

    Returns:
        int: The dimensionality of the contents.
    """
    # Matches arrays in the form of (/a,b,c/) or [a,b,c]
    if NatureDeterminer.is_hardcoded_array(contents):
        return 1
    # Remove outer brackets
    contents = BasicFunctions.remove_outer_brackets(contents)
    # Its a Char
    if BasicFunctions.contain_literals(contents, block.module.dictionary_of_masked_string):
        return 0
    # Its a Bool
    if contents.lower().count(".false.") or contents.lower().count(".true."):
        return 0

    if NatureDeterminer.is_keyword_argument(contents):
        # Split using only the  first equal
        _, argument = contents.split("=", 1)
        return get_dimension_of_contents(argument, block, vault)



    # Remove possible +/- before variables
    contents = BasicFunctions.remove_unary_operator(contents)

    # If a function is passed, check is an intrinsic
    if CallManager.is_call_to_function(contents, block, vault):
        fun = CallManager.find_called_function(contents)
        # These intrinsic ret val dimension, depends on the argument
        if fun.lower() in ["real", "rpe", "sqrt", "min", "max", "abs", "log", "aimag"]:
            return get_dimension_of_contents(CallManager.find_call_arguments(contents)[0], block, vault)
        # For these check if the dim keyword is passed
        elif fun.lower() in ['sum', 'maxval']:
            if contents.lower().count("dim="):
                dim = get_dimension_of_contents(CallManager.find_call_arguments(contents)[0], block, vault)
                if dim:
                    return dim - 1
                else:
                    return dim
            else:
                contents = CallManager.find_call_arguments(contents)[0]
        # COUNT returns a number
        elif fun.lower() in ["count", 'size']:
            return 0
        else:
            raise Error.ExceptionNotManaged("Something went wrong finding the dimension of %s" % contents)
    # Check if has operations
    split_elements = []
    if NatureDeterminer.has_operations(contents, split_elements):
        dimensions = [get_dimension_of_contents(el, block, vault) for el in split_elements]
        dimensions = [d for d in dimensions if d is not None]
        if not dimensions:
            dimensions = [0]
        return max(dimensions)
    # Simple number
    if NatureDeterminer.is_a_number(contents):
        return 0

    if NatureDeterminer.is_logical_comparison(contents):
        # Split the logical comparison and keep only the first element
        contents, _ = BasicFunctions.split_comparison(contents)
        return get_dimension_of_contents(contents=contents, block=block, vault=vault)

    # Must be a single variable
    var = get_variable(contents, procedure=block, vault=vault)

    # If is a sliced array, count how many slice are considered
    if contents.count(":"):
        if var.type == 'char':
            return var.dimension
        return contents.count(":")

    # If we have the var + index specification, like sdjf%fdta(2,2,1,2) or psgn(jf) then is a scalar
    if re.search(r"%s *\(.*\)" % var.name, contents):
        return 0
    return var.dimension


def get_interface(arguments: List[str], interface: Interface, block: Procedure, vault: 'Vault', uniform_intent=None):
    """
    Determines the specific interface subroutine that matches the given arguments.

    Parameters:
        arguments (list[str]): A list of arguments passed to the interface.
        interface (Interface): The interface object to search within.
        block (Procedure): The procedure context to analyze.
        vault (Vault): The vault containing metadata about the code.
        uniform_intent (str, optional): An intent to filter by (e.g., 'in', 'out').

    Returns:
        Subprogram: The subprogram within the interface that matches the arguments.

    Raises:
        InterfaceNotFound: If no matching routine is found.
    """
    optional_da = []
    for subprogram in interface.subprogram:
        for da in subprogram.dummy_arguments:
            if da.is_optional and da.name not in optional_da:
                optional_da.append(da.name)
    # Remove optional parameters specified by keyword
    keyword_arguments = [_x.split("=")[0].strip() if NatureDeterminer.is_keyword_argument(_x) else False for _x in
                         arguments]
    mandatory_arguments = []
    for index, kwa in enumerate(keyword_arguments):
        if kwa in optional_da:
            continue
        elif kwa in mandatory_arguments:
            new_index = [da.mandatory_position for da in interface.subprogram[0].mandatory_da if da.name == kwa][0]
            if len(mandatory_arguments) != new_index:
                raise Error.ExceptionNotManaged("The argument should be inserted in position new_index")
            else:
                mandatory_arguments.append(arguments[index])
        else:
            mandatory_arguments.append(arguments[index])
    argument_dimension = [get_dimension_of_contents(argument, block, vault) for argument in mandatory_arguments]
    argument_types = [get_type_of_contents(argument, block, vault) for argument in mandatory_arguments]

    return get_interface_from_mandatory_arguments(interface, argument_types, argument_dimension,
                                                  uniform_intent)


def get_interface_from_mandatory_arguments(interface: Interface, argument_types: List[str], argument_dimensions: List[int], uniform_intent):
    """
    Matches a specific subprogram in an interface based on mandatory arguments.

    Parameters:
        interface (Interface): The interface to analyze.
        argument_types (list[str]): The types of the mandatory arguments.
        argument_dimensions (list[int]): The dimensions of the mandatory arguments.
        uniform_intent (str, optional): An intent to filter by.

    Returns:
        Subprogram: The matching subprogram.

    Raises:
        InterfaceNotFound: If no matching subprogram is found.
    """
    # Sort the interface by number of mandatory arguments
    interface.subprogram.sort(key=lambda x: len(x.mandatory_da), reverse=True)
    # Search among those subroutines that have enough arguments to match
    subprogram = [s for s in interface.subprogram if len(argument_types) <= len(s.dummy_arguments)]
    for s in subprogram:
        len_arg = len(s.mandatory_da)
        # Exclude interface, that expects more arguments than the ones used
        if len_arg > len(argument_types):
            continue
        argument_intent = []
        if uniform_intent is not None:
            argument_intent = [da.intent for da in s.mandatory_da]
        # Some of the actual arguments, ca be optional not specified via keyword
        key = Interface.generate_dict_key(argument_types[:len_arg], argument_dimensions[:len_arg],
                                          argument_intent,
                                          uniform_intent)
        if uniform_intent is not None:
            if key in interface.agnostic_key[uniform_intent]:
                # Return the list of names
                key_list = interface.agnostic_key[uniform_intent][key]
                if len(key_list):
                    return interface[key_list[0]]
                else:
                    raise Error.InterfaceNotFound(
                        "More than a matching routine found for interface : %s" % interface.name)
        else:
            try:
                subprogram_name = interface.key[key]
            except KeyError:
                continue
            # Return corresponding subprogram
            return interface[subprogram_name]
    raise Error.InterfaceNotFound("No matching routine found for interface : %s" % interface.name)


def get_type_of_real_cast(string: str):
    """
    Determines the type of a real cast operation based on its arguments.

    Parameters:
        string (str): The string representation of the cast operation.

    Returns:
        str: The type of the real cast (e.g., 'sp', 'dp', etc.).
    """
    # Leave only the arguments
    arguments = CallManager.find_call_arguments(string)
    if len(arguments) == 1:
        return VariablePrecision.real_id['wp']
    elif len(arguments) == 2:
        _, arg_type = arguments
        # In case the type is specified along with keyword
        arg_type = re.sub(r'kind=', '', arg_type, flags=re.I)
        # TODO: Handling an edge case in NEMO 4.2.0 that was not present anymore in NEMO 4.2.2 or NEMO 5.
        # Must find a better solution but might be that is not necessary
        if arg_type == "2*wp":
            arg_type = "dp"
        return VariablePrecision.lookup_table[arg_type.lower()]
