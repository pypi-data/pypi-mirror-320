from tqdm import tqdm
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.CallManager as CallManager
import re


def clean_sources(input_file_list):
    """  Remove comments, empty lines and old style declaration"""
    for file in tqdm(input_file_list,  desc="Formatting file"):
        clean(file)


def clean(file):
    """Format file, so it can be parsed to generate a vault"""
    # Remove all comments
    remove_all_comments(file)

    # Remove \n char (can be found inside strings) to avoid problem with split lines function
    remove_newline_character(file)

    # Merges commands split on multiples lines
    merge_lines(file)

    # Split multi command lines into multiple lines
    split_lines(file)

    # Mask all the string with hashes
    mask_string(file)

    # Replace variable declarations that used the traditional style for declarations with ::
    replace_traditional_declaration(file)

    # Split lines with more than one declaration
    split_declarations(file)

    # Add dimension attribute if has been specified with variable name
    add_dimension_attribute(file)

    # Remove parameter assignation F77 style
    # _remove_F77_parameter_declaration(file)

    # Substitutes all multiple spaces with single spaces ( for some regex to work)
    remove_multiple_space(file)

    # # Split lbc_lnk function, with one variable for line, so to avoid cast and incompatibility
    # split_lbc_lnk_call(file)

    # Deletes all the empty lines
    remove_empty_lines(file)

    # Removes procedure attributes, such as 'elemental' or 'pure' (only the elemental is needed so far)
    remove_procedure_attribute(file)


    # Put text back together
    file.update_module_lines()


def split_lines(file):
    """Split into multiple lines multiple-command lines"""
    for index, line in enumerate(file.lines):
        if line.count(";"):
            n_of_spaces = BasicFunctions.count_initial_spaces(line)
            # Create a string where literals have been substituted with #
            mask = MaskCreator.mask_literal(line)
            # Substitutes semicolons with \n command
            match = re.finditer(r";", mask)
            semicolons = [m.start() for m in match]
            # Always substitute from the last match, to avoid changes in indexing
            for i_sem in semicolons[::-1]:
                line = line[:i_sem] + "\n" + " " * n_of_spaces + line[i_sem + 1:].strip()
            file.lines[index] = line
    # This will take care of translating \n command into different lines
    file.update_module_lines()


def remove_multiple_space(file):
    """Remove multiple spaces inside string, keeping indentation"""
    for index, line in enumerate(file.lines):
        # Count initial spaces
        n_of_spaces = BasicFunctions.count_initial_spaces(line)
        # Transform multiple spaces to single ones
        file.lines[index] = re.sub(r'\s\s+', ' ', line)
        # Try to keep original indentation
        file.lines[index] = " " * n_of_spaces + file.lines[index]


def split_declarations(file):
    import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
    # Split declarations of variables putting a single variable in each line
    for _index, _line in enumerate(file.lines):
        if _line.count("::") and not re.search(RegexPattern.string_array_initialization, _line) and not \
                re.search(RegexPattern.general_allocation, _line, re.I) and \
                len(re.findall(r"\buse\b", _line, re.I)) == 0:
            attributes, arguments = _line.split("::")
            arguments = CallManager.find_call_arguments("c(%s)" % arguments)
            if len(arguments) > 1:
                # Put a declaration for each line
                file.lines[_index] = "".join(["%s :: %s\n" % (attributes, arg) for arg in arguments])

    file.update_module_lines()


def add_dimension_attribute(file):
    import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
    # check the array has dimension specified after the name
    for _index, _line in enumerate(file.lines):
        if _line.count("::") and not re.search(RegexPattern.string_array_initialization, _line) and not \
                re.search(RegexPattern.general_allocation, _line, re.I):
            attributes, argument = _line.split("::")
            if argument.count("(") and not argument.count("="):
                var_name, dimension = argument.split("(", 1)
                # if dimension.count("*"):
                #     dimension = dimension.replace("*", ":")
                file.lines[_index] = attributes.replace("::", "") + ", DIMENSION(" + dimension + " :: " + var_name


# Split lbc_lnk function calls, with one variable for line, so to avoid cast and incompatibility
def split_lbc_lnk_call(file):
    import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
    from AutoRPE.UtilsRPE.NatureDeterminer import is_keyword_argument
    # Split declarations of variables putting a single variable in each line
    for _index, _line in enumerate(file.lines):
        if re.search(RegexPattern.call_to_function_name % 'lbc_lnk', _line):

            call, arguments = _line.split("CALL")
            arguments = CallManager.find_call_arguments(arguments)
            # Function name is the first argument
            function_name = arguments.pop(0)
            true_arg = []
            keyword_arg = []
            for a in arguments:
                if is_keyword_argument(a):
                    keyword_arg.append(a)
                else:
                    true_arg.append(a)
            n_calls = len(true_arg) / 3
            if int(n_calls) != n_calls:
                raise ValueError("Unexpected number of arguments found")
            new_line = ""
            for i in range(int(n_calls)):
                # Put a call for each line, adding function name, and keyword arguments
                new_line += call + \
                            "CALL lbc_lnk(" + function_name + ", " + \
                            ", ".join(arguments[i * 3: i * 3 + 3])
                if len(keyword_arg):
                    new_line += ", " + ", ".join(keyword_arg)

                new_line += ")\n"
            file.lines[_index] = new_line
    file.update_module_lines()


def remove_all_comments(file):
    # Remove comments from a file
    for _index, _line in enumerate(file.lines):
        file.lines[_index] = BasicFunctions.remove_comments(_line)

def replace_traditional_declaration(file):
    import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
        # Define a regex to match traditional declarations
    traditional_declaration_pattern = RegexPattern.traditional_declaration_pattern
    traditional_declaration_pattern = re.compile(traditional_declaration_pattern)

    def is_traditional_declaration(line: str) -> bool:
        """
        Determines if a line is a traditional Fortran declaration.

        Args:
            line (str): A single line of Fortran code.

        Returns:
            bool: True if the line is a traditional declaration, False otherwise.
        """
        # Ensure the line contains a type declaration and does NOT include "::"
        return traditional_declaration_pattern.match(line) and '::' not in line
    
    for _index, _line in enumerate(file.lines):
        match = traditional_declaration_pattern.match(_line)
        if match and is_traditional_declaration(_line):
            dtype = match.group(1)  # Data type (real, integer, etc.)
            kind_len = match.group(2) if match.group(2) else ''  # Kind or length specifier
            dimension = match.group(3) if match.group(3) else ''  # Dimension attribute
            variables = match.group(4)
            try:
                variables = variables.strip() # Variable names
            except Exception:
                print(variables)

            # Construct the modern declaration
            modern_declaration = f"{dtype}{kind_len}"
            if dimension:
                modern_declaration += f", {dimension}"
            modern_declaration += f" :: {variables}"
            file.lines[_index] = modern_declaration

def _remove_F77_parameter_declaration(file):
    import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
    # If parameter declaration is made in Fortran 77 style

    for line_index, line in enumerate(file.lines):

        # Search for lines with the 'PARAMETER' statement
        match = re.match(RegexPattern.parameter_77style_declaration, line, re.I)
        if match:
            # Remove last bracket so it does no enter in parameters val
            param_line = line.replace(")", "")

            # Store parameter names
            parameters_name = [parameter.split("=")[0].strip() for parameter in
                               param_line.split("(")[1].split(",")]

            # Store parameter values
            parameters_val = [parameter.split("=")[1].strip() for parameter in
                              param_line.split("(")[1].split(",")]

            for parameter_name, parameter_value in zip(parameters_name, parameters_val):

                # Search for each parameter declaration backward in the file
                for dec_line_index, dec_line in enumerate(reversed((file.lines[:line_index]))):
                    # parameter_pattern = '.*::\s*' + parameter_name + '$'
                    # parameter_pattern = RegexPattern.name_occurrence%s
                    param_declaration = re.search(RegexPattern.name_occurrence % parameter_name, dec_line, re.I)
                    if line_index == dec_line + 1:
                        raise AssertionError("declaration of parameter %s not found in file %s" % (
                            parameter_name, file.filename))
                    # Put back in place the parameter attribute and assign the parameter value
                    if param_declaration:
                        # Add param statement
                        piece_to_replace = dec_line.split('::')[0]
                        replacement = "%s, parameter " % piece_to_replace
                        dec_line = dec_line.replace(piece_to_replace, replacement)

                        # Add param assignation
                        dec_line = dec_line + "=" + parameter_value

                        # Substitute the line
                        file.lines[line_index - dec_line_index - 1] = dec_line

                        break

            # Delete parameter declaration
            file.lines[line_index] = ""


def merge_lines(file):
    """Given a file, puts back on the same line commands split with a &"""
    # List split lines index
    split_index = [i for i, l in enumerate(file.lines) if l.count("&")]
    for index in split_index:
        # If is an openmp directive, skip
        omp_dir = re.search(r"^\s*#", file.lines[index])
        if omp_dir:
            continue
        # Merge the split line on first line, nullify lines that have been merged in the first one
        BasicFunctions.merge_line_in_file(index, file)


def remove_newline_character(file):
    """Remove \n character. Output will be on single line, but avoid mess up with rebuild of modules"""
    newline_index = [i for i, l in enumerate(file.lines) if l.count("\\n")]
    for index in newline_index:
        file.lines[index] = file.lines[index].replace("\\n", "")


def remove_empty_lines(file):
    """
      Remove empty strings from list of strings
    """
    file.lines = [_l for _l in file.lines if _l.strip()]


def mask_string(file):
    for line_index, line in enumerate(file.lines):
        file.lines[line_index] = MaskCreator.mask_literal(line, dict_of_substitutions=file.dictionary_of_masked_string)


def remove_procedure_attribute(file, attribute_list=None):
    """
    Removes attributes like pure or elemental, in order to allow working with 'rpe_var' variables and
    modifying the 'variable_is_used' variable within the procedures.
    """
    if attribute_list is None:
        attribute_list = ['elemental', 'pure']

    pattern = r"\b(%s)\s\b"

    for line_index, line in enumerate(file.lines):
        found_matches = [f_  for attribute in attribute_list for f_ in re.findall(pattern % attribute, line, flags=re.I) ]
        for match in found_matches:
            file.lines[line_index] = re.sub(rf"\b{match}\s\b", "", line, flags=re.IGNORECASE)
