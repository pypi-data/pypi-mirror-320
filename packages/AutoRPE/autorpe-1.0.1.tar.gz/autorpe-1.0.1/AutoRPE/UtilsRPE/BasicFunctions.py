import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.Classes.Module as Module
import re


# def is_in_reals_blacklist(blacklist, line, module, dt=''):
#     for v in blacklist:
#         if module == v['module'] and \
#                 dt.lower() == v['derived_type'].lower() and \
#                 re.search(RegexPattern.real_variable_declaration_name % v['var_name'], line, re.IGNORECASE):
#             return True
#     return False


def load_source_file(_filename: str, extension: str, no_strip: bool=False):
    """
    Loads a Fortran source file and creates a `SourceFile` object.

    Parameters:
        _filename (str): The name of the source file to load.
        extension (str): The file extension (e.g., ".f90").
        no_strip (bool): If True, preserves extra whitespace and comments while reading the file.

    Returns:
        SourceFile: An object representing the source file, with its content loaded.
    """
    import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile
    # Create a SourceFile object
    file = SourceFile.SourceFile(_filename, extension)
    # Load the file text into the object
    file.read_file(_filename, no_strip)
    return file


def load_sources(input_path: str, extension: list[str]=[".f90"]):
    """
    Recursively loads Fortran source files from the specified input path(s).

    Parameters:
        input_path (str | list[str]): A single directory path or a list of paths to scan for source files.
        extension (list[str]): A list of allowed file extensions to load (default is [".f90"]).

    Returns:
        list: A list of `SourceFile` objects representing the loaded files.

    Raises:
        ValueError: If no files with the specified extensions are found in the input path.
    """
    from warnings import warn
    from os.path import join, abspath, splitext
    from os import walk
    file_list = []

    # If the passed argument is not a list, convert to avoid splitting a string
    if not isinstance(input_path, list):
        input_path = [input_path]

    # Reads files for top folder, and searches recursively in sub-folders
    for path in input_path:
        for dir_path, dir_name, file_name in walk(path):
            for f_name in file_name:
                # Include file with specified extensions and exclude hidden files (like .swp files)
                file_extension = splitext(f_name)[1]
                if file_extension in extension and f_name[0][0] != ".":
                    file_list.append(load_source_file(join(dir_path, f_name), file_extension, no_strip=True))

    if not len(file_list):
        raise ValueError(f"No files found in {abspath(input_path[0])} folder")
    # If h90 extension was specified then append included files to including modules
    if ".h90" in extension:
        for file in file_list:
            header_files = [l.lower().split("include")[1] for l in file.lines if
                            # remove comments and literals and search for the # include path
                            re.search(RegexPattern.name_occurrence % "include", remove_comments(MaskCreator.remove_literals(l)), re.I)]
            for h_90 in header_files:
                h_90 = h_90.replace("\"", "").strip()
                h_90 = h_90.replace("\'", "").strip()
                try:
                    h_90 = [f for f in file_list if f.filename.lower() == h_90.lower()][0]
                except IndexError:
                    warn("Header file %s not found among input files" % h_90)
                    continue
                file.header_files.append(h_90)
            file.preprocess_header_file()

    return file_list


def load_intrinsics():
    """
    Loads a dictionary of Fortran intrinsic functions and their corresponding types.

    Returns:
        dict: A dictionary where keys are intrinsic function names (lowercase) and values are their types.
    """
    from os.path import abspath, dirname
    package_directory = dirname(abspath(__file__))
    # Hardcoded path to file.
    with open(package_directory + "/../AdditionalFiles/fortran_intrinsics") as f:
        intrinsics = dict((intrinsic.split(',')[0].lower(), intrinsic.split(',')[1]) for intrinsic in f)

    return intrinsics


def remove_unary_operator(string: str):
    """
    Removes unary operators (e.g., `+` or `-`) from a string, if present.

    Parameters:
        string (str): The input string.

    Returns:
        str: The string with unary operators removed.
    """
    import re
    return re.sub(RegexPattern.unary_operator, "", string)


def close_brackets(string: str):
    """
    Trims a string to include only the portion up to the closing bracket of a function or array call.

    Parameters:
        string (str): The input string.

    Returns:
        str: The trimmed string ending at the first matched closing bracket.

    Raises:
        ExceptionNotManaged: If the brackets are unbalanced in the input string.
    """
    # Check is a call with arguments
    first_parenthesis = re.search(r'\(', string)
    if not first_parenthesis:
        return string

    first_parenthesis = first_parenthesis.start()

    # Index that mark if we are inside an array
    bracket_balance = -1
    # Start counting just after first bracket
    for char_index, c in enumerate(string[first_parenthesis + 1:]):
        if bracket_balance == 0:
            string = string[:char_index + first_parenthesis+1]
            break
        elif c in ["(", "["]:
            bracket_balance -= 1
        elif c in [")", "]"]:
            bracket_balance += 1
        else:
            continue
    if bracket_balance != 0:
        raise Error.ExceptionNotManaged("This should not happen, check arguments %s" % string)
    return string


def combine_types(list_of_types: list[str]):
    """
    Combines a list of variable types into a single resulting type, based on a predefined dictionary.

    Parameters:
        list_of_types (list): A list of variable types to combine.

    Returns:
        str: The resulting combined type.

    Raises:
        ExceptionNotManaged: If the type combination is not defined in the dictionary.
    """
    ret_val = list_of_types.pop()
    while list_of_types:
        next_type = list_of_types.pop()
        try:
            ret_val = VariablePrecision.dictionary_of_possible_combination[frozenset([ret_val, next_type])]
        except KeyError:
            raise Error.ExceptionNotManaged("Please add the combination" +
                                            "[" + str(ret_val) + "," + str(next_type) + "]" +
                                            " to dictionary_of_possible_combination ")
    return ret_val


def create_type_combinations(case_types: list):
    """
    Generates all possible combinations of casting real types for a list of variable types.

    Parameters:
        case_types (list): A list of variable types.

    Returns:
        list: A list of all possible variations of the input variable types.

    Raises:
        AssertionError: If the number of arguments exceeds 10, which can cause combinatorial issues.
    """
    # TODO: In some cases a big number of arguments can make this approach crash. Here we add a security check.
    if len(case_types) > 10:
        raise AssertionError("Too much arguments to use a combinatorial approach.")
    import itertools
    import itertools
    syn_types = ["real" if x in VariablePrecision.real_id else x for x in case_types]

    number_of_reals = syn_types.count("real")

    a = ["sp", "dp"] * number_of_reals
    combinations = list(set(itertools.permutations(a, number_of_reals)))

    new_types = []
    for comb in combinations:
        comb_types = syn_types[:]
        for i in range(number_of_reals):
            comb_types[comb_types.index("real")] = comb[i]
        new_types.append(comb_types)
    return new_types


def hash_from_list(string_list: list[str]):
    """
    Computes a hash value from a list of strings.

    Parameters:
        string_list (list[str]): A list of strings.

    Returns:
        str: The MD5 hash value of the concatenated strings.

    Raises:
        ExceptionNotManaged: If the input is not a list of strings.
    """
    import hashlib
    if not isinstance(string_list, list):
        raise Error.ExceptionNotManaged("This input should be a string list")
    string_to_hash = ""
    for i_str in string_list:
        string_to_hash += i_str

    hash_object = hashlib.md5(string_to_hash.encode())
    return hash_object.hexdigest()


def find_next_end(lines: list[str], _index: int, end_statement: str):
    """
    Finds the next occurrence of an end statement in a block of lines.

    Parameters:
        lines (list[str]): A list of source code lines.
        _index (int): The starting index to search from.
        end_statement (str): The end statement to search for (e.g., "end subroutine").

    Returns:
        int: The index of the next line containing the end statement.
    """
    _i = _index + 1
    begin_statement = end_statement.replace('end', '')
    nested_declaration = 0
    while _i < len(lines):
        _l = lines[_i]
        if re.match(r'^\s*(' + begin_statement + ')', _l, re.I):
            nested_declaration += 1
        if _l.lower().count(end_statement):
            if nested_declaration == 0:
                return _i
            else:
                nested_declaration -= 1
        _i += 1

    return len(lines)


def contain_literals(string: str, string_dictionary: dict=None):
    """
    Determines if a string contains literals (e.g., quotes, concatenation symbols, or masks).

    Parameters:
        string (str): The input string to check.
        string_dictionary (dict, optional): A dictionary of masked strings for additional checks.

    Returns:
        bool: True if the string contains literals or matches a masked string.
    """
    if string_dictionary is None:
        for i in ["'", "//", '"']:
            if string.lower().count(i):
                return True
    else:
        # Check if the string is a masked string
        if string.count('@') or string in string_dictionary.keys():
            return True
    if re.search(RegexPattern.name_occurrence % "trim", string, re.I):
        return True
    return False


def is_all_inside_parenthesis(string: str):
    """
    Checks if the entire string is enclosed in parentheses.

    Parameters:
        string (str): The input string to check.

    Returns:
        bool: True if the string is fully enclosed in parentheses, False otherwise.
    """
    if string.strip()[0] == "(":
        try:
            if "c%s" % string.strip() == close_brackets("c%s" % string.strip()):
                return True
            else:
                return False
        except ValueError:
            return False
    else:
        return False


def remove_comments(string: str, return_comment: bool=False):
    """
    Removes comments from a string, preserving OpenMP directives.

    Parameters:
        string (str): The input string.
        return_comment (bool): If True, returns the removed comment as well.

    Returns:
        str | tuple[str, str]: The string without comments, and optionally the removed comment.
    """
    comment = ""
    if string.count("!"):
        # Preserve OMP directives
        if string.count('$OMP'):
            return string
        # If not literal are present, it is safe to split by exclamation marks
        if not contain_literals(string):
            comment = string[string.find("!"):]
            string = string[:string.find("!")]
        # If literals are present, mask them  to avoid matching exclamation marks
        else:
            dict_of_substitution = {}
            string = MaskCreator.mask_literal(string, dict_of_substitution)
            if string.count("!"):
                comment = string[string.find("!"):]
                string = string[:string.index('!')]
            string = MaskCreator.unmask_from_dict(string, dict_of_substitution)
    if return_comment:
        return string, comment
    return string


def remove_if_condition(_line: str, return_if_condition: bool=False):
    """
    Removes an `if` condition from a line, preserving the remaining content.

    Parameters:
        _line (str): The input line.
        return_if_condition (bool): If True, also returns the removed condition.

    Returns:
        str | tuple[str, str]: The line without the `if` condition, and optionally the removed condition.
    """
    if _line.replace(" ", "").lower().strip().find("if(") == 0:
        condition = close_brackets(_line)
        _line = _line.replace(condition, "")
    else:
        condition = ""
    if not return_if_condition:
        return _line
    else:
        return [condition, _line]


def remove_else_condition(line: str):
    """
    Removes an `else` condition from a line, preserving the remaining content.

    Parameters:
        line (str): The input line.

    Returns:
        str: The line without the `else` condition.
    """
    import re
    if line.replace(" ", "").lower().strip().find("else") == 0:
        # This way we will also transform elseif condition in simple if
        line = re.sub(r"^\s*else\s*", "", line, flags=re.I)
    return line


def clean_if_else_condition(line: str, function_name: str):
    """
    Removes conditions from an `if` or `else` statement, returning the function call if present.

    Parameters:
        line (str): The input line of code.
        function_name (str): The name of the function to search for.

    Returns:
        str: The function call if found, otherwise the remaining code.
    """
    line = remove_else_condition(line)
    condition, call = split_if_condition(line)
    function_call = re.search(RegexPattern.name_occurrence % function_name, condition)
    if function_call:
        return close_brackets(condition[function_call.start():])
    else:
        return call


def remove_keywords(arguments: list[str]):
    """
    Removes keywords from a list of argument strings, returning only the values.

    Parameters:
        arguments (list[str]): A list of arguments, potentially containing keywords.

    Returns:
        list[str]: The list of arguments with keywords removed.
    """
    patt = "[a-zA-Z_0-9]* *=(.*)"
    for index, argument in enumerate(arguments):
        m = re.match(patt, argument.strip())
        if m:
            arguments[index] = m.group(1).strip()
    return arguments


def remove_hardcoded_array_assign(string: str):
    """
    Removes hardcoded array assignments from a string.

    Parameters:
        string (str): The input string containing the assignment.

    Returns:
        str: The string without hardcoded array assignments.
    """
    hardcoded_array_assign = r'='+RegexPattern.hardcoded_array
    m = re.search(hardcoded_array_assign, string)
    if m:
        string = string[:m.start()]
    return string


def split_if_condition(_line: str):
    """
    Splits a line into its `if` condition and the remaining content.

    Parameters:
        _line (str): The input line.

    Returns:
        tuple[str, str]: The `if` condition and the remaining content.
    """
    return remove_if_condition(_line, return_if_condition=True)


def remove_outer_brackets(string: str):
    """
    Removes the outermost parentheses from a string, if present.

    Parameters:
        string (str): The input string.

    Returns:
        str: The string without its outermost parentheses.
    """
    string = string.strip()
    if is_all_inside_parenthesis(string):
        return string[1:-1].strip()
    else:
        return string


def remove_spaces(string: str):
    """
    Removes extra spaces from a string.

    Parameters:
        string (str): The input string.

    Returns:
        str: The string with multiple spaces reduced to a single space.
    """
    return re.sub('\\s\\s+', r' ', string)


def count_initial_spaces(string: str):
    """
    Counts the number of leading spaces in a string.

    Parameters:
        string (str): The input string.

    Returns:
        int: The number of leading spaces.
    """
    m = re.search(r'\w', string, re.I)
    if m:
        return m.start()
    return 0


def remove_indexing(content: str):
    """
    Removes indexing (e.g., array brackets) from a variable or expression.

    Parameters:
        content (str): The input content string.

    Returns:
        str: The string without indexing or array brackets.
    """
    import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
    # If there are not brackets, there is no indexing
    if not content.count("("):
        # Case of a recursive call
        content = content.replace("XXX", "%")
        return content
    # If the variable is already a simple name
    if re.match(RegexPattern.variable, content):
        # Case of a recursive call
        content = content.replace("XXX", "%")
        return content
    # If is a simple array with indexing
    if NatureDeterminer.is_array(content):
        # Case of a recursive call
        return content[:content.index("(")].replace("XXX", "%")
    # Avoid problem with structure used as index
    content = content.replace("%", "XXX")
    # Used to avoid recursion error
    clean_content = content
    # Replace hardcoded array
    hard_code_array = re.search(RegexPattern.hardcoded_array, clean_content)
    if hard_code_array:
        clean_content = clean_content.replace(hard_code_array.group(), "")
        # Remove possible container of hardcoded array
        clean_content = clean_content.replace("()", "")
    match_array_brackets = re.findall(RegexPattern.match_array_brackets, clean_content)
    for brackets in match_array_brackets:
        clean_content = clean_content.replace(brackets, "")
    # Recursively remove brackets
    if not re.search(RegexPattern.variable, clean_content) and not re.search(RegexPattern.structure, clean_content):
        # This check avoid infinite recursion, if the function has not changed anything returns
        if clean_content != content:
            return remove_indexing(clean_content)

    # Reinsert structure markers
    clean_content = clean_content.replace("XXX", "%")
    return clean_content


def merge_line_range(lines: list[str], line_index: int):
    """
    Merges a multi-line statement into a single line by resolving line continuations.

    Parameters:
        lines (list[str]): The list of lines in the source file.
        line_index (int): The starting index of the line to merge.

    Returns:
        str: The merged line with all continuations resolved.
    """
    n_of_spaces = count_initial_spaces(lines[line_index])
    line = remove_comments(lines[line_index]).strip()

    merge_line_range.number = 1
    if line.count("&"):
        while line and line.strip()[-1] == "&":
            line1 = line
            while remove_comments(lines[line_index + merge_line_range.number]).strip() == "":
                merge_line_range.number = merge_line_range.number + 1
            line2 = remove_comments(lines[line_index + merge_line_range.number])
            line = line1.replace("&", "").rstrip() + line2
            merge_line_range.number += 1
        line = line.replace("&", "")
        # To split a print statement extra char are needed: remove them and join it into a single string
        line = re.sub(r'\"\s*//\s*\"', " ", line)
        line = re.sub(", +", ", ", line)
        line = re.sub(":  +", ":  ", line)
        line = line.strip() + "\n"

    return " " * n_of_spaces + line


def merge_line_in_file(line_index: int, module: Module):
    """
    Merges a split statement into a single line within a source file. Removes empty lines.

    Parameters:
        line_index (int): The index of the line to merge.
        module: The module object containing the lines of source code.
    """
    line = merge_line_range(module.lines, line_index)
    module.lines[line_index] = line
    # Nullify lines that have been merged
    for j in range(1, merge_line_range.number):
        module.lines[line_index + j] = ""


def split_comparison(content: str) -> tuple[str, str]:
    """
    Splits a string based on the first occurrence of a comparison operator.

    Parameters:
        content (str): The input string containing a comparison.

    Returns:
        tuple[str, str]: A tuple with the left-hand side and right-hand side of the comparison.
    """
    # Iterate through the string to find the first occurrence of any operator
    for operator in SourceManager.comparison_operators:
        if operator in content:
            # Split the string at the first occurrence of the operator
            parts = content.split(operator, 1)
            # Return the two parts as a tuple, stripping any leading or trailing whitespace
            return parts[0].strip(), parts[1].strip()
    
    # If no operator is found, return the original string as the first element and an empty string as the second element
    return content, ""
