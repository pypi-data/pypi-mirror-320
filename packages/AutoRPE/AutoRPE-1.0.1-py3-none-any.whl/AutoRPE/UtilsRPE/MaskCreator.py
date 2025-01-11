import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.Error as Error
import re


def _randStr(N):
    """Generates a random string with specified length"""
    import string
    import random
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(N))


def mask_literal(string, dict_of_substitutions=None):
    """
    Looks for open and close of different apex and mask what is in between.

    Parameters:
        string (str): String to be masked.
        dict_of_substitutions (dict): Dictionary that contains the masked-unmasked strings to substitute.

    Returns:
        str: Masked string.
    """
    if dict_of_substitutions is None:
        dict_of_substitutions = {}
    # Before checking for apex, check for apex with escapes
    escaped_string = re.finditer(r'\bb\'.*\'', string)
    for e_s in escaped_string:
        string = _mask(string, e_s.start(),  e_s.start() + len(e_s.group()), dict_of_substitutions)

    apex = [i for i in ["\"", "\\'", "\'"] if string.count(i)]
    # Need to check for the fist that appears to avoid masking things already masked '(A,".nc")'
    apex.sort(key=lambda x: string.index(x))
    for i in apex:
        apex = re.finditer(i, string)
        apex = [a.start() for a in apex]
        for i_open, i_close in zip(apex[0::2], apex[1::2]):
            string = _mask(string, i_open, i_close + 1, dict_of_substitutions)
    return string


def _mask(string, start, end, dict_of_sbs, placeholder=False):
    """ Generate hash and substitutes them in the specified place"""
    if not placeholder:
        # Generate a unique hash
        dict_key = _key_gen(string[start:end], dict_of_sbs)

        # Add the entry in the dictionary with hash as key and literal as value
        dict_of_sbs[dict_key] = string[start: end]
        # Substitute the hash into the original string
        string = string[:start] + dict_key + string[end:]
    else:
        # Here we just substitute with a safe string, the string will never be unmasked
        # Generate a unique hash
        dict_key = "A" * (end - start)

        # Add the entry in the dictionary with hash as key and literal as value
        dict_of_sbs[dict_key] = string[start: end]
        # Substitute the hash into the original string
        string = string[:start] + dict_key + string[end:]
    return string


def _get_key_from_dictionary(dictionary, string_value):
    for key, val in dictionary.items():
        if val == string_value:
            return key
    raise ValueError(f"Value '{string_value}' not found in the dictionary.")


def _key_gen(string, dict_of_sbs):
    """The hash can't be confused with name of function or var since they always contain a @"""
    # We first check whether this same string has already been masked, this way we have a key for
    # each different string
    if string in dict_of_sbs.values():
        dict_key = _get_key_from_dictionary(dictionary=dict_of_sbs, string_value=string)
        return dict_key

    # Generate a hash as long as the literal -1 to leave space for the "@"
    len_string = len(str(string))
    if len_string == 2:
        if string == "''":
            dict_key = "0@"
        else:
            dict_key = "1@"
    else:
        dict_key = _randStr(len_string - 1)
        # Insert "@" as second char so we can still use the \bkey_dict\b regex
        dict_key = dict_key[:1] + '@' + dict_key[1:]

    # When key is short (3 or 2 char) it is possible that already exists, recreate until a new key is generated
    if dict_key in dict_of_sbs:
        return _key_gen(string, dict_of_sbs)
    else:
        return dict_key


def mask_keyword(line: str, key: str, dictionary_of_substitutions: dict):
    """
    Masks occurrences of a specific keyword in a line by replacing them with unique placeholders.

    This function identifies occurrences of a keyword assignment (e.g., `key = value`) and substitutes
    the keyword with a placeholder, while updating a dictionary to store the original values.

    Parameters:
        line (str): The line of code in which to mask the keyword.
        key (str): The keyword to search for and mask.
        dictionary_of_substitutions (dict): A dictionary to store mappings between placeholders and the original values.

    Returns:
        str: The line with the specified keyword occurrences masked.
    """
    import re
    key = RegexPattern.escape_string(key)
    match = re.finditer(r'(%s)\s*=\s*%s' % (key, key), line, re.I)
    match = [[m.start(1), m.end(1)] for m in match]
    for start, end in match:
        # Substitute the match with the unique placeholder
        line = _mask(line,  start, end, dictionary_of_substitutions)
    return line


def remove_literals(string: str, dict_of_literal_sub: dict=None):
    """
    Removes literal values from a string, replacing them with spaces while maintaining the original string length.

    This function masks literal values (e.g., strings in quotes) using `mask_literal`, then substitutes
    the masked literals with spaces while preserving the length of the original string.

    Parameters:
        string (str): The input string from which literals should be removed.
        dict_of_literal_sub (dict, optional): A dictionary to store mappings of masked literals and their original values.
                                              If not provided, a new dictionary will be created.

    Returns:
        str: The modified string with literals replaced by spaces.
    """
    if dict_of_literal_sub is None:
        dict_of_literal_sub = {}
    string = mask_literal(string, dict_of_literal_sub)
    # Substitute literals with space, maintaining length
    for key, val in zip(dict_of_literal_sub.keys(), dict_of_literal_sub.values()):
        string = re.sub(RegexPattern.escape_string(key), "\'" + " "*(len(val)-2) + "\'", string)
    return string


def mask_string_for_check_operation(string: str, dictionary_of_replacements: dict=None):
    """
    Masks various components of a string to prepare it for safe operation checks.

    This function applies several masking steps to handle components like exponents, arrays, structures,
    and function calls. It replaces these components with placeholders, allowing for safe processing of 
    operations without interference from complex structures.

    Parameters:
        string (str): The input string to be masked.
        dictionary_of_replacements (dict, optional): A dictionary to store mappings between placeholders 
                                                     and the original components. If not provided, a new
                                                     dictionary will be created.

    Returns:
        str: The masked string with brackets removed and placeholders for complex components.
    """
    import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
    # Remove exponent in the form of d**N: it will mess up with normal operators. It will not be substituted back
    string = remove_pow(string)
    string = BasicFunctions.remove_unary_operator(string)
    # Dict to store all entities that will need a mask
    if dictionary_of_replacements is None:
        dictionary_of_replacements = {}
    # Mask the exponential form of numbers/variables (may contain operations in the exponent)
    string = mask_exponential(string, dictionary_of_replacements)

    # Mask all arrays and structures (may contain operation in indexing)
    string = mask_arrays_and_structures(string, dictionary_of_replacements=dictionary_of_replacements)

    # Mask all functions call (may contain operation in arguments)
    string = mask_functions(string, dictionary_of_replacements)

    # Now is safe to remove brackets
    string = string.replace("(", "")
    string = string.replace(")", "")
    return string


def mask_arrays_and_structures(string: str, only_structures: bool=False, dictionary_of_replacements: dict=None):
    """
    Masks arrays and structures within a string by replacing them with randomly generated strings 
    or placeholders, and creates a dictionary of the substitutions.

    Parameters:
        string (str): The input string containing arrays and structures to be masked.
        only_structures (bool, optional): If True, only structure patterns are masked. Defaults to False.
        dictionary_of_replacements (dict, optional): A dictionary to store the replacements. If None, a temporary dictionary is used.

    Returns:
        str: The modified string with arrays and structures masked.
    """
    import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer

    placeholder = False
    # In case we do not want to store the replacement: create a tmp dict
    if dictionary_of_replacements is None:
        dictionary_of_replacements = {}
        # In this case the masking can be done in a simpler way
        placeholder = True

    # Check if the entire string is an array
    if NatureDeterminer.is_array(string) and not only_structures:
        dict_key = _randStr(len(string))
        dictionary_of_replacements[dict_key] = string
        return dict_key

    array_replacement = {}
    # Checks for all array pattern, and substitute with randomly generated string of the same length
    start = True
    while start:
        start = False
        array_match = re.finditer(RegexPattern.array, string)
        for a_m in array_match:
            start = True
            string = _mask(string, a_m.start(), a_m.end(), array_replacement)

        # Substitute structures with string
        struct_match = re.finditer(RegexPattern.structure, string)
        for s_m in struct_match:
            start = True
            string = _mask(string, s_m.start(), s_m.end(), dictionary_of_replacements, placeholder)

    if only_structures:
        # Keep structure masked
        string = unmask_from_dict(string, array_replacement)
    else:
        # Save array dictionary for further use
        dictionary_of_replacements.update(array_replacement)
    return string


def remove_pow(string: str):
    """
    Removes exponential notation (e.g., power operations) from a string.

    This function searches for instances of exponentiation (using '**' or raised powers) 
    in the input string and removes them. It handles both simple power operations and 
    exponentiation inside parentheses.

    Parameters:
        string (str): The input string from which exponential notations are to be removed.

    Returns:
        str: The modified string with exponential notations removed.
    """
    import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
    exponentials_var = re.finditer(RegexPattern.number_exponentiation, string)
    # When the var is elevate to simple power, remove power
    start_end = [[a.start(), a.end()] for a in exponentials_var]
    for match_start, match_end in start_end[::-1]:
        string = string[:match_start] + string[match_end:]
    # Exp elevated to some operation in brackets, remove all in brackets
    exponentials_var = re.finditer(r"\*\*\s*\(", string)
    start = [a.start() for a in exponentials_var]
    for match_start in start[::-1]:
        match_end = match_start + len(BasicFunctions.close_brackets(string[match_start:]))
        string = string[:match_start] + string[match_end:]
    return string


def mask_functions(string: str, dictionary_of_replacements: dict=None):
    """
    Masks function calls within the given string. Identifies and replaces all function calls in the
    input string with a masked placeholder.

    Parameters:
        string (str): The input string containing function calls to be masked.
        dictionary_of_replacements (dict, optional): A dictionary to store the replacements. If None, a new dictionary is created.

    Returns:
        str: The modified string with function calls masked.
    """
    import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions

    if dictionary_of_replacements is None:
        dictionary_of_replacements = {}

    # Transform the (eventual) callable iterator into a list to iterate backward
    functions = [f for f in re.finditer(RegexPattern.call_to_function, string)]
    # The regular pattern used for finding function calls does not identify
    # functions/calls correctly when the name of the call is masked and the first
    # symbol(s) after the @ are numbers, so we add a second search for these cases:
    if "@" in string:
        # We use a different Regex pattern to identify these calls
        found_matches = [f.group(1) for f in functions]
        masked_functions = [f for f in re.finditer(RegexPattern.call_to_function_masked, string)
                            if f.group(1) not in found_matches]
        functions += masked_functions

    for f in functions[::-1]:
        # Find call
        function_call = BasicFunctions.close_brackets(string[f.start(1):])
        # Compute exact end of the function call
        f_end = f.start(1) + len(function_call)
        # Generate a placeholder with specified length
        string = _mask(string, f.start(1), f_end, dictionary_of_replacements)
    return string


def mask_exponential(string: str, dictionary_of_replacements: dict=None):
    """
    Masks exponential notations within the given string and creates a dictionary with the substitutions.

    Parameters:
        string (str): The input string containing exponential notations to be masked.
        dictionary_of_replacements (dict, optional): A dictionary to store the replacements. 
                                                  If None, a new dictionary is created.

    Returns:
        str: The modified string with exponential notations masked.
    """
    """ Replace all exponential creating a dictionary with the substitutions"""
    # If no dictionary is passed, create one
    if dictionary_of_replacements is None:
        dictionary_of_replacements = {}

    exponentials_DPE = re.finditer(RegexPattern.number_exp_DPE_notation, string, re.I)
    # Substitute match with string, group 1, which correspond to the actual exponential
    start_end = [[a.start(2), a.end(2)] for a in exponentials_DPE]
    for match_start, match_end in start_end[::-1]:
        # Generate a placeholder with specified length
        string = _mask(string, match_start, match_end, dictionary_of_replacements)
    return string


def mask_intrinsics(string: str):
    """
    Masks intrinsic function calls within the string by simplifying their arguments.

    Parameters:
        string (str): The input string containing intrinsic function calls to be masked.

    Returns:
        list: The simplified arguments or the modified string after masking.
    """
    import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
    import AutoRPE.UtilsRPE.CallManager as CallManager
    import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
    intrinsic = NatureDeterminer.has_intrinsics(string)

    while intrinsic:
        # Get the intrinsic call
        intrinsic_call = BasicFunctions.close_brackets(
            string[re.search(RegexPattern.name_occurrence % intrinsic, string, re.I).start():])
        called_arg = CallManager.find_call_arguments(intrinsic_call)
        arguments_to_remove = []
        if intrinsic.lower() in ['real', 'reshape']:
            # Remove loop index, or cast precision if present
            called_arg = called_arg[:1]
        for arg in called_arg:
            if arg.split("=")[0] in SourceManager.list_of_key:
                arguments_to_remove.append(arg)
        # Removed key specification
        for arg in arguments_to_remove:
            called_arg.remove(arg)
        # Rejoin pure arguments
        if len(called_arg) > 1:
            string = string.replace(intrinsic_call, "(" + ",".join(called_arg) + ")", re.I)
        else:
            string = string.replace(intrinsic_call, called_arg[0], re.I)
            string = BasicFunctions.remove_outer_brackets(string)
        # Check for further intrinsics
        intrinsic = NatureDeterminer.has_intrinsics(string)
    # Check if is a cast with precision and the precision was not specified via key
    called_arg = CallManager.find_call_arguments("(" + string + ")")
    if len(called_arg) == 2:
        if called_arg[1] in VariablePrecision.lookup_table:
            return [called_arg[0]]
        # It is the dimension ?
        if NatureDeterminer.is_a_number(called_arg[1]):
            return [called_arg[0]]
    if len(called_arg) > 1:
        raise Error.VariableNotFound("The string %s is not a variable" % string)
    return called_arg


def find_keys(string: str, dictionary_of_replacements: dict=None):
    """
    Finds all masked keys in the given string, including those with double masks.

    Parameters:
        string (str): The input string to search for masked keys.
        dictionary_of_replacements (dict, optional): A dictionary of replacements to filter the keys found.

    Returns:
        list: A list of masked keys found in the string, filtered by the dictionary of replacements if provided.
    """
    # all matches with double masks (both group 0 and 1)
    double_mask_pattern = r"\b\w@(\w@\w*\b)"
    double_mask = [match.group(1) for match in re.finditer(string=string, pattern=double_mask_pattern)]              # group 1
    double_mask_match_group0 = [match.group(0) for match in re.finditer(string=string, pattern=double_mask_pattern)] # group 0

    # all strings that match single masks (even those that are part of the double masks)
    single_mask_pattern = r"\b\w*@\w*"
    single_mask_match = re.findall(string=string, pattern=single_mask_pattern)
    # now we exclude those that are substrings of double masks
    single_mask = [match for match in single_mask_match if not any(match in str_ for str_ in double_mask_match_group0)]

    # Finally, we only take into account those that are found inside the dictionart of replacements, if provided
    full_list = double_mask+single_mask
    if dictionary_of_replacements:
        full_list = [key for key in full_list if key in dictionary_of_replacements.keys()]
    return full_list

def unmask_from_dict(string: str, dictionary_of_replacements: dict):
    """
    Unmasks a string using a dictionary of replacements, processing double-masked keys first (strings that
    have been masked twice, containing two '@').

    Parameters:
        string (str or list): The masked string (or list of strings) to be unmasked.
        dictionary_of_replacements (dict): A dictionary containing the masked keys and their replacements.

    Returns:
        str | list: The unmasked string (or list of strings) after applying the dictionary replacements.
    """

    if not (isinstance(string, list)):
        str_list = [string]
    else:
        str_list = string
    for _index, _s in enumerate(str_list):
        # Check that there is at least on element to substitute
        keys = find_keys(_s, dictionary_of_replacements)
        substitute = len(keys)
        while substitute:
            for k in keys:
                try:
                    val = dictionary_of_replacements[k]
                except KeyError:
                    # We hit a key from a different dictionary, avoid infinite loop
                    substitute = False
                    continue
                str_list[_index] = re.sub(RegexPattern.escape_string(k, strict=False), val, str_list[_index])
            # Update the matches
            keys = find_keys(str_list[_index])
            # Re-check if they are among dictionary keys
            substitute = any(k in keys for k in dictionary_of_replacements.keys())

    if not (isinstance(string, list)):
        return str_list[0]
    else:
        return str_list
