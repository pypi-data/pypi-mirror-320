
from AutoRPE.UtilsRPE.logger import logger, clean_line
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.CallManager as CallManager
import re


def parse_attributes(attributes: str, variables: list):
    """
    Parses a string of attributes to extract variable characteristics.

    Parameters:
        attributes (str): The attribute string to parse.
        variables (list): List of variables to use for parsing.

    Returns:
        tuple: A tuple containing the parsed variable type, dimension, intent, optionality, allocatable status,
               pointer status, and parameter status.
    """
    # Transform the string in a list of attributes
    attributes = CallManager.find_call_arguments("(%s)" % attributes)
    var_type = attribute_type(attributes, variables)
    dimension = attribute_dimension(attributes, variables)
    intent = attribute_intent(attributes)
    optional = attribute_is_optional(attributes)
    allocatable = attribute_is_allocatable(attributes)
    pointer = attribute_is_pointer(attributes, variables)
    parameter = attribute_is_parameter(attributes)
    return var_type, dimension, intent, optional, allocatable, pointer, parameter


def attribute_type(attributes: list[str], variable: str=None):
    """
    Determines the type of a variable from its attribute string.

    Parameters:
        attributes (list): A list of attributes.
        variable (str, optional): A variable object for additional context, default is None.

    Returns:
        str | None: The variable type as a string, or None if the type cannot be determined.
    """
    possible_types = ["real", "integer", "type", "class", "char", "logical", "complex", "double precision",
                      "procedure",
                      "useintrinsic",
                      "public"]
    # Type specification is always the first attribute
    t0 = attributes[0]

    var_type = None
    for ty in possible_types:
        if t0.lower().find(ty) == 0:
            var_type = ty
            break
    if not var_type:
        return None

    if var_type in ["type", "class"]:
        # It may be the case in which it is a type declaration instead of a variable declaration of a type
        # This workaround is to discard this cases.
        if not t0.count("("):
            return None
        var_type = t0[t0.find("(") + 1:-1].strip()
    elif var_type == "public":
        return None
    elif var_type == "real":
        type_specifier = re.search(RegexPattern.precision_of_real_declaration, t0, re.I)
        if type_specifier:
            specifier_name = type_specifier.group(3).lower()
            try:
                return VariablePrecision.lookup_table[type_specifier.group(3).lower()]
            except KeyError:
                VariablePrecision.lookup_table[specifier_name] = VariablePrecision.UndefinedPrecision(specifier_name)
                return VariablePrecision.UndefinedPrecision(specifier_name)
                raise Error.ExceptionNotManaged("Pleas add this type specifier into VariablePrecision.lookup_table: %s"
                                                % type_specifier)
        else:
            # Delete current output line for a clean output
            clean_line()
            # Use logging
            logger.warn("Type specifier not found in real variable " + variable + " declaration")
            return VariablePrecision.real_id['wp']
    else:
        pass
    return var_type.lower()



def parse_dimension_attribute(dimension_attribute: str) -> int:
    """
    Parses a dimension attribute string and returns the number of dimensions.

    Parameters:
        dimension_attribute (str): The dimension attribute string to parse.

    Returns:
        int: The number of dimensions, or 0 if invalid.
    """
    # Remove leading and trailing whitespaces
    declaration = dimension_attribute.replace(" ", "").strip()

    # Check if it starts with 'DIMENSION(' and ends with ')'
    if declaration.startswith('DIMENSION(') and declaration.endswith(')'):
        # Extract the part inside the parentheses
        inside = declaration[len('DIMENSION('):-1].strip()
    else:
        # Not a valid DIMENSION declaration
        return 0

    # Initialize counters
    paren_count = 0
    dimension_count = 1  # Start with 1 dimension by default

    for char in inside:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char == ',' and paren_count == 0:
            dimension_count += 1

    return dimension_count


def attribute_dimension(attributes: list[str], variable: str):
    """
    Returns the dimension of the variable from a list of attributes.

    Parameters:
        attributes (list[str]): A list of attribute strings.
        variable (str): The variable string to analyze for dimensions.

    Returns:
        int: The number of dimensions of the variable.
    """
    dim = 0
    for att in attributes:
        # In case the dimension is defined as a * set dim=None
        if re.search(r"dimension\s*\(\*\)", att, re.I):
            dim = None
            break
        # In case it is a dimension attribute parse it
        if att.lower().count("dimension"):
            dim = parse_dimension_attribute(att)
            break
    if dim == 0:
        dim = variable.count(":")
    
    # TODO: Probably not the most robust solution to find the dimension
    if variable.count("="):
        variable = variable.split("=")[0].strip()
    if dim == 0 and variable.count("("):
        dim = variable.count(",") + 1

    return dim


def attribute_intent(attributes: list[str]):
    """
    Returns the intent of a variable from its attributes. Defaults to 'inout'.

    Parameters:
        attributes (list[str]): A list of attribute strings.

    Returns:
        str: The intent of the variable (e.g., 'in', 'out', 'inout').
    """
    # Default value
    intent = ""
    for att in attributes:
        if att.lower().count("intent"):
            intent = att[att.find("(") + 1:-1].strip().lower()
            break
    if not intent:
        intent = "inout"
    return intent


def attribute_is_optional(attributes: list[str]):
    """
    Returns whether a variable is marked as optional in its attributes.

    Parameters:
        attributes (list[str]): A list of attribute strings.

    Returns:
        bool: True if the variable is optional, False otherwise.
    """
    optional = False
    for att in attributes:
        if att.lower().count("optional"):
            optional = True
            break
    return optional


def attribute_is_parameter(attributes: list[str]):
    """
    Returns whether a variable is a constant parameter in its attributes.

    Parameters:
        attributes (list[str]): A list of attribute strings.

    Returns:
        bool: True if the variable is a parameter, False otherwise.
    """
    for att in attributes:
        if att.lower().count("parameter"):
            return True
    return False


def attribute_is_allocatable(attributes: list[str]):
    """
    Returns whether a variable is allocatable in its attributes.

    Parameters:
        attributes (list[str]): A list of attribute strings.

    Returns:
        bool: True if the variable is allocatable, False otherwise.
    """
    for att in attributes:
        if att.lower().count("allocatable"):
            return True
    return False


def attribute_is_pointer(attributes: list[str], variables: list[str]):
    """
    Checks if a variable is a pointer and returns the pointed object.

    Parameters:
        attributes (list[str]): A list of attribute strings.
        variables (list[str]): A list of variable declarations.

    Returns:
        str | bool: The pointed object name if the variable is a pointer, False otherwise.
    """
    if "POINTER" in (a.upper() for a in attributes):
        pointed_object = attributes[0]
        if pointed_object.count("procedure"):
            pointed_object = pointed_object.replace("procedure", "")
            pointed_object = BasicFunctions.remove_outer_brackets(pointed_object)
        return pointed_object
    if variables.count("=>"):
        pointed_object = variables.split("=>")[1]
        return pointed_object.strip()
    return False


def get_variable_name_parsed(string: str):
    """
    Removes assignment or indexing from a variable declaration and returns the variable name.

    Parameters:
        string (str): The variable declaration string.

    Returns:
        str: The parsed variable name.
    """
    # In case is an assignment, remove the assigned value
    name = string.split("=")[0]
    # In case in an array, remove indexing
    name = name.split("(")[0]
    return name.strip()


def get_variable_name(string: str, original_file=False):
    """
    Returns the variable name(s) from a declaration string, handling both single and multiple declarations.

    Parameters:
        string (str): The variable declaration string.
        original_file (bool): Flag indicating whether the file is parsed (default is False).

    Returns:
        str | list[str]: The variable name(s).
    """
    if not original_file:
        return get_variable_name_parsed(string)
    else:
        # Divide various declaration
        string = BasicFunctions.remove_hardcoded_array_assign(string)
        declarations = string.split(",")
        name_list = []
        for name in declarations:
            # get the names, one by one
            name_list.append(get_variable_name_parsed(name))
        return name_list

