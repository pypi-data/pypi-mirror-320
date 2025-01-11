import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.SourceManager as SourceManager

import re


def is_function_declaration_statement(line: str):
    """
    Checks if the line contains a function declaration statement.
    
    Parameters:
        line (str): A line of source code to check for a function declaration.

    Returns:
        bool: True if the line matches the syntax of a function declaration, False otherwise.
    """
    # Remove matches inside write(*,*) statements
    # Check for function declaration syntax
    is_start = re.search(RegexPattern.function_declaration, line, re.MULTILINE | re.IGNORECASE)
    if is_start:
        return True
    return False


def is_end_function_statement(line: str):
    """
    Checks if the line contains an 'end function' statement.
    
    Parameters:
        line (str): A line of source code to check for an 'end function' statement.

    Returns:
    -   bool: True if the line matches the syntax of an 'end function' statement, False otherwise.
    """
    is_end = re.match(RegexPattern.end_function_declaration, line, re.I)
    if is_end:
        return True
    return False


def is_a_number(string):
    """
    Checks if a string is a valid number and return its type if applicable.

    Parameters:
        string (str): The string to be checked.

    Returns:
        str or bool: The type of the number (e.g., 'integer' or 'real'), or False if it's not a number.
    
    Raises:
        ValueError: If the string cannot be converted to a number and does not match valid formats.
    """

    # Check if is just white spaces
    if not string.strip():
        return False
    else:
        string = string.lower().strip()

    # Remove unary operator if present
    string = BasicFunctions.remove_unary_operator(string)

    if has_intrinsics(string):
        return False

    # Checks for number in exponential notation
    exp = re.match(RegexPattern.number_exp_DPE_notation, string)
    # Checks for number with precision specified
    real_with_precision = re.match("^" + RegexPattern.real_number_with_precision + "$", string)
    if real_with_precision:
        # In case the number is a hardcoded real with a type specification,
        # check the lookup table to know to which type it corresponds and return it
        new_type = VariablePrecision.lookup_table[real_with_precision.group(2)]
        return new_type

    if exp:
        return VariablePrecision.real_id['wp']

    integer_with_precision = re.match(RegexPattern.integer_number_with_precision, string)
    if integer_with_precision:
        return "integer"
    # Check for pure integer and real numbers
    try:
        float(string)
        if string.isdigit():
            return "integer"
        else:
            return VariablePrecision.real_id['wp']
    except ValueError:
        return False


def is_hardcoded_array(string, array=None):
    """
    Checks if the string represents a hardcoded array [form (/a, b/)] and optionally populate the
    array parameter.

    Parameters:
        string (str): The string to check if it represents a hardcoded array.
        array (list, optional): If provided, the array will be populated with the elements found in the array.

    Returns:
        bool: True if the string represents a hardcoded array, False otherwise.
    """
    import AutoRPE.UtilsRPE.CallManager as CallManager
    match = re.match(RegexPattern.hardcoded_array, string)
    if match:
        if array is not None:
            # remove_outer_brackets will remove parenthesis just if present
            content = "(" + BasicFunctions.remove_outer_brackets(match.group(2)) + ")"
            array.extend(CallManager.find_call_arguments(content))
        return True
    return False


def is_pointer_assignment(string: str):
    """
    Checks if the string represents a pointer assignment.

    Parameters:
        string (str): The string to check if it contains a pointer assignment.

    Returns:
        bool: True if the string represents a pointer assignment, False otherwise.
    """
    pattern = ".* => .*"
    if re.search(pattern, string, flags=re.I):
        return True
    return False


def is_logical_comparison(string: str):
    """
    Checks if the string contains a logical comparison operator.

    Parameters:
        string (str): The string to check for logical comparison operators.

    Returns:
        bool: True if the string contains a logical comparison operator, False otherwise.
    """
    for element in SourceManager.comparison_operators:
        if string.lower().count(element):
            return True
    return False


def is_keyword_argument(argument: str, key_arg=None):
    """
    Checks if the argument is a keyword argument and optionally store the key-value pair.

    Parameters:
        argument (str): The argument string to check.
        key_arg (list, optional): If provided, the list will be populated with the key and argument value.

    Returns:
        bool: True if the argument is a keyword argument, False otherwise.
    """
    if re.search(RegexPattern.key_word_argument, argument):
        if key_arg is not None:
            [key, argument] = argument.split("=", 1)
            key = key.strip()
            argument = argument.strip()
            key_arg.extend([key, argument])
        return True
    return False


def is_array(contents: str, check_sliced: bool=False):
    """
    Checks if the contents represent an array, optionally checking for slicing.

    Parameters:
        contents (str): The contents to check if they represent an array.
        check_sliced (bool, optional): If True, the function checks if the array is sliced.

    Returns:
        bool: True if the contents represent an array, False otherwise.
    """
    import AutoRPE.UtilsRPE.CallManager as CallManager
    # First does a first filter checking that the syntax is similar to a function call and afterwards
    # uses one of the two possible approaches, depending on having a vault available or not.

    # The syntax is be the same for vector and function (unless vector is sliced)
    m = re.match(RegexPattern.call_to_function, contents.strip(), re.I)
    if not m:
        return False

    if contents == BasicFunctions.close_brackets(contents):
        arguments = CallManager.find_call_arguments(contents)
        # No arguments: it is a function or a single variable
        if arguments:
            if not check_sliced:
                return True
            else:
                # check if an argument is a slice
                for arg in arguments:
                    if re.match(r"\w*:\w*", arg) or arg == ":":
                        return True
                return False
    return False


def has_operations(string: str, operand=None):
    """
    Checks if the string contains mathematical operations and optionally splits the operands.

    Parameters:
        string (str): The string to check for operations.
        operand (list, optional): If provided, the operands will be split and stored in the list.

    Returns:
        bool: True if the string contains mathematical operations, False otherwise.
    """
    operations = ["+", "-", "*", "/"]
    # Exclude key arguments
    if is_keyword_argument(string):
        return False
    # Check if string is just white spaces
    if not string.strip():
        return False
    else:
        string = string.replace(" ", "")

    if is_array(string):
        return False

    if operand is not None:
        # If we want to split the argument by operand, store the masked element in a dictionary
        dictionary_of_replacements = {}
        string = MaskCreator.mask_string_for_check_operation(string, dictionary_of_replacements)
    else:
        string = MaskCreator.mask_string_for_check_operation(string)

    # Now that all offenders have been masked, split the elements
    for op in operations:
        # Substitute all operators with a placeholder
        string = string.replace(op, "#")
    # The string does not contains operations
    if not string.count("#"):
        return False
    else:
        # Fill the passed vector
        if operand is not None:
            # A  void unitary operators to be considered operators ( rn_Dt * (-10_wp)) => rn_Dt * -10_wp )
            string = re.sub(r"#\s*#", r"#", string)
            # Remove unary operators at the beginning of the string
            string = re.sub(r"^\s*#", "", string)

            # Split by placeholder
            arguments = string.split("#")
            # Strip from spaces due to substitutions
            arguments = [a.strip() for a in arguments]
            operand.extend(MaskCreator.unmask_from_dict(arguments, dictionary_of_replacements))
            # Substitute back all entities that were masked
        return True


def has_intrinsics(string: str):
    """
    Checks if the string contains any intrinsic function calls.

    Parameters:
        string (str): The string to check for intrinsic function calls.

    Returns:
        str or None: The name of the intrinsic function if found, None otherwise.
    """
    for key in SourceManager.list_of_key:
        if string.lower().count(key):
            key_match = r"\s*[ ,(+-]%s *= *\w" % key
            string = re.sub(key_match, "", string, re.I)

    # Split parenthesis opening
    if not string.count("("):
        return False

    possible_intrinsics = re.findall(r'\s*\b\w+\b\s*\(', string, re.I)

    for name in possible_intrinsics:
        # Remove last parenthesis and leading spaces
        name = name[:-1].strip()
        try:
            SourceManager.list_of_intrinsics[name.lower()]
            return name
        except KeyError:
            continue
    return None

def is_struct_element(contents: str) -> bool:
    """
    Checks if the contents represent a structure element (derived type).

    Parameters:
        contents (str): The contents to check for structure element notation (e.g., 'struct%element').

    Returns:
        bool: True if the contents represent a structure element, False otherwise.
    """
    if contents.count("%"):
        return True
    return False
    ...