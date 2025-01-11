import AutoRPE.UtilsRPE.Inserter as Inserter
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.Error as Error
import re


class FoundLines:
    def __init__(self, original_module):
        self.original_module = original_module
        self.lines = []


class Lines:
    def __init__(self, line_index, n_of_merged_lines):
        self.idx = line_index
        self.n_of_merged_lines = n_of_merged_lines


def find_included_files(original_module, modules):
    # The var can be declared in some .h90 included file
    additional_modules = []
    # Search for the include pattern and return the h90 file name
    additional_module_names = [re.search(r"^#\s*include\s+\"(\w+.h90)\"", l, re.I).group(1)
                               for l in original_module.lines if re.search(r"^#\s*include", l, re.I)]
    # If some h90 file is included, create a list with corresponding modules object
    if additional_module_names:
        additional_modules = [m for m in modules if m.filename in additional_module_names]
    return additional_modules


def previous_line_is_split(index, module_lines):
    """Check if last previous line that was not a comment was a split line"""
    index -= 1
    while not BasicFunctions.remove_comments(module_lines[index]).strip():
        index -= 1
    if module_lines[index].count("&"):
        return True
    return False


def rebuild_split_line(line_index, original_module):
    """Takes a line that can be either split upward or downward, rebuilt it and modify the original module text"""
    # The variable is declared on the first line, but the line is split downward
    if original_module.lines[line_index].count("::"):
        BasicFunctions.merge_line_in_file(line_index, original_module)
    # The variable is one or more lines down the declaration, go up until the declaration is found
    while not original_module.lines[line_index].count("::"):
        line_index -= 1
    # Now merge lines downwards
    BasicFunctions.merge_line_in_file(line_index, original_module)
    return line_index


def find_subprogram_declarations_index(subprogram, module):
    """Find start and end indexes of variables declaration in subprogram code """
    # Find start and end of subprogram declaration, can change module going to a header file
    module, indices = Inserter.find_subprogram_lines(subprogram)

    start = -1
    end = 0
    # The search for declaration
    for index, line in enumerate(module.lines[indices[0]:indices[1] + 1]):

        line = BasicFunctions.remove_comments(line)
        # Skip only comment lines
        if not line.strip():
            continue
        # Skip until first declaration is found
        if start < 0:
            if not line.count('::'):
                continue
        # First declaration found
        if start < 0:
            start = indices[0] + index
            continue
        # Skip possible preprocessor directives (cyclone introduces optional variables)
        if line.count('#'):
            continue
        # Excluding preprocessor directives there can be only comments among var declarations (but they can be split)
        # if it is not a declaration means the body of the function begun
        if not (line.count('::') or previous_line_is_split(indices[0] + index, module.lines)) and start > 0:
            end = indices[0] + index - 1
            # If last line was a preprocessor line, we need to remove it
            if module.lines[end].count('#'):
                end = end - 1
            break

    # Return variables declaration line indexes
    return module, [start, end]


def find_main_declarations_index(module):
    """Find start and end indexes of variables declaration in main """
    main_start = -1
    # In case in main there is no subprogram declaration, just variables
    main_end = len(module.lines) - 1
    for index, line in enumerate(module.lines):
        line = BasicFunctions.remove_comments(line)
        # Start of the declaration section
        if line.count("::") and main_start < 0:
            main_start = index
        # Subprogram declaration start
        if line.lower().count('contains'):
            main_end = index - 1
            break
    # If no variable declaration was found
    if main_start < 0:
        return [-1, -1]
    return [main_start, main_end]


def find_structure_declarations_index(structure, module):
    """Find start and end indexes of variables declaration of custom data type """
    start = -1

    begin_pattern = RegexPattern.type_name_begin % structure.name
    end_pattern = RegexPattern.end_type_statement
    for index, line in enumerate(module.lines):
        line = BasicFunctions.remove_comments(line)
        # Start of the declaration section, just if is has not been found yet (avoid match with the end pattern)
        if start < 0 and re.search(begin_pattern, line, re.I):
            start = index
        # Subprogram declaration start
        if start > 0 and re.search(end_pattern, line, re.I):
            end = index - 1
            break
    # Structure was not found
    if start < 0:
        return [-1, -1]
    return [start, end]


def find_function_type_specification(subprogram, module):
    module, indices = Inserter.find_subprogram_lines(subprogram)
    declaration_line = module.lines[indices[0]]
    if re.search(RegexPattern.function_precision_declaration, declaration_line, re.I):
        return module, indices[0]
    else:
        raise Error.LineNotFound("Failed to find return type of function %s" % subprogram.name)


def substitute_preprocessor_var(arguments, original_module):
    """Searches if the argument is the byproduct of some processor substitution"""
    if not original_module.dictionary_of_definition:
        return arguments
    new_argument = arguments[:]
    for ind, argument in enumerate(new_argument):
        if BasicFunctions.contain_literals(argument):
            continue
        # Remove indexing  to facilitate the regex match
        argument = BasicFunctions.remove_outer_brackets(argument)
        if NatureDeterminer.has_intrinsics(argument):
            argument = MaskCreator.mask_intrinsics(argument)
            if len(argument) == 1:
                argument = argument[0]
            else:
                Error.ExceptionNotManaged("Intrinsic not managed %s " % NatureDeterminer.has_intrinsics(argument))
        split_elements = []
        if NatureDeterminer.has_operations(argument, split_elements):
            for i, el in enumerate(split_elements):
                if el.count("("):
                    split_elements[i] = BasicFunctions.remove_indexing(el)
            argument = split_elements
        else:
            if argument.count("("):
                argument = BasicFunctions.remove_indexing(argument)
            argument = [argument]
        # Search for every key of the dictionary if the values matches the argument
        found = False
        for function in original_module.dictionary_of_definition:
            if found:
                break
            # Multiple entries: preprocessor directives depend on compilation key, and we are storing all definitions
            for definition in original_module.dictionary_of_definition[function]:
                # Remove index from the value to facilitate the match
                split_elements = []
                if NatureDeterminer.has_operations(definition, split_elements):
                    # Stop check if the len of the argument does not correspond: avoid checking DO loops definition,etc
                    if len(argument) != len(split_elements):
                        continue
                # Check if the arg is present in the value of dictionary
                found_arg = [arg for arg in argument if re.search(r'\b%s\(*' % arg, definition)]
                # The argument must be of same length of the key
                if len(found_arg) == len(argument):
                    # In case the argument was inside an intrinsic call, or parenthesis, or whatever
                    start_index = arguments[ind].index(found_arg[0]) - definition.index(found_arg[0])
                    # Substitute proper indexing
                    new_argument[ind] = substitute_preprocessor_index(function, definition, arguments[ind], start_index)
                    found = True
                    break
    return new_argument


def substitute_preprocessor_index(function, function_val, argument, start_index):
    # Function is the rhs of the definition, preproc_key the result of the substitution, i.e. what is found in the f90
    preproc_index = CallManager.find_call_arguments(function)
    original_key = function
    used_function_val = function_val
    index_shift = start_index
    for p_i in preproc_index:
        # No need to match all index on the lhs
        preproc_index_position = re.search(RegexPattern.name_occurrence % p_i, function_val).start()
        # Search length of original index
        preproc_index_position += index_shift
        partial_arg = argument[preproc_index_position:]
        index_bracket = partial_arg.index(")")
        if partial_arg.count(","):
            # If a comma is present check it is inside this array indexing
            index_comma = partial_arg.index(",")
            end_arg = min(preproc_index_position + index_comma, preproc_index_position + index_bracket)
        else:
            # It is the last index of the array
            end_arg = preproc_index_position + index_bracket

        # Get the name
        real_index_name = argument[preproc_index_position:end_arg]
        if len(real_index_name) != len(p_i):
            index_shift += len(real_index_name) - len(p_i)
        original_key = re.sub(RegexPattern.name_occurrence % p_i, real_index_name, original_key)
        used_function_val = re.sub(RegexPattern.name_occurrence % p_i, real_index_name, used_function_val)
    return argument.replace(used_function_val, original_key)


def find_subprogram_call(subprogram_call, original_modules, substitute_preproc=True):
    # Get the original module
    original_module = [om for om in original_modules if om.module_name == subprogram_call.block.module.name][0]

    # Find start and end of subprogram block where the fix is due
    original_module, indices = Inserter.find_subprogram_lines(subprogram_call.block, original_module)

    # Name of the function to be searched
    subprogram_name = subprogram_call.name

    # Patter to search for
    if isinstance(subprogram_call.subprogram, Subprogram.Function):
        subprogram_pattern = RegexPattern.call_to_function_name
    elif isinstance(subprogram_call.subprogram, Subprogram.SubRoutine):
        subprogram_pattern = RegexPattern.call_to_subroutine_name
    else:
        raise Error.ExceptionNotManaged("Something unexpected ended up here!")

    # Initialize the object to be filled within the loop
    found_lines = FoundLines(original_module)
    # Search for all the calls with this program name and argument inside the subprogram body
    for index, line in enumerate(original_module.lines[indices[0]:indices[1] + 1]):
        # Return merged line if the line is split
        line = BasicFunctions.merge_line_range(original_module.lines, indices[0] + index)
        # Remove comments, char and if condition to avoid false positive
        line = BasicFunctions.remove_comments(line)
        line = BasicFunctions.clean_if_else_condition(line, subprogram_name)
        dict_of_literal_sub = {}
        line = MaskCreator.mask_literal(line, dict_of_literal_sub)
        # Remove spaces to avoid differences with match name
        line = BasicFunctions.remove_spaces(line)

        if re.search(subprogram_pattern % subprogram_name, line, re.I):
            # There can be operation with the function
            if isinstance(subprogram_call.subprogram, Subprogram.Function):
                # Avoid matching when the variable is on one side of the equation and the function on the other
                assignation = re.search(RegexPattern.assignation, line, re.I)
                if assignation:
                    line = assignation.group(3)
                # Keep the function call, there can be more than one on one line
                start_index = [i.start() for i in re.finditer(RegexPattern.name_occurrence % subprogram_call.name, line,
                                                              re.I)]
                call = [BasicFunctions.close_brackets(line[si:]) for si in start_index]

            else:
                # Here there will be just one
                call = [re.sub(RegexPattern.name_occurrence % "CALL", "", line, re.IGNORECASE)]
            for c in call:
                # Check if the call corresponds
                c = MaskCreator.unmask_from_dict(c, dict_of_literal_sub)
                if subprogram_call.call == c.strip():
                    line_obj = Lines(indices[0] + index, BasicFunctions.merge_line_range.number)
                    found_lines.lines.append(line_obj)
                    continue

        # if line was split, jump the merged indices
        for i in range(BasicFunctions.merge_line_range.number - 1):
            continue

    if not found_lines.lines and substitute_preproc:
        # Try to substitute preprocessor variables if they have not been updated yet
        argument_names = [arg.name for arg in subprogram_call.arguments]
        argument_names_new = substitute_preprocessor_var(argument_names, original_module)
        if argument_names_new != argument_names:
            for arg_ind, (an, an_new) in enumerate(zip(argument_names, argument_names_new)):
                subprogram_call.call = subprogram_call.call.replace(an, an_new)
                subprogram_call.arguments[arg_ind].name = an_new
            found_lines = find_subprogram_call(subprogram_call, original_modules, substitute_preproc=False)
        if not found_lines.lines:
            raise Error.LineNotFound("Call %s not found in module %s", subprogram_call.call,
                                     original_module.module_name)
    return found_lines


def add_include_clause(module):
    contains_marker = [index for index, l in enumerate(module.lines) if l.lower().count("contains")]
    if not contains_marker:
        # Header files may not contain include, but just function, hope it is included in main file
        return
    contains_marker = contains_marker[0]
    include_lines = [index for index, l in enumerate(module.lines[:contains_marker]) if re.search(r"#\s+include ", l)]
    already_present = [idx for idx in include_lines if re.search("single_precision_substitute.h90", module.lines[idx])]
    if already_present:
        return
    if include_lines:
        include_lines = include_lines[-1]
    else:
        include_lines = contains_marker
    module.lines[include_lines] = "#  include \"single_precision_substitute.h90\"" + "\n" + module.lines[include_lines]


def cast_variable(var_name, precision, original_module, original_line):
    if precision == "hp":
        cast = "CASTHP(%s)"
    elif precision == "wp":
        cast = "CASTSP(%s)"
    elif precision == "dp":
        cast = "CASTDP(%s)"
    else:
        raise Error.ExceptionNotManaged("Wrong input precision")
    check_line = original_module.lines[original_line.idx: original_line.idx + original_line.n_of_merged_lines]
    found = [l for l in check_line if l.count(var_name)]
    if not found:
        check_line = [BasicFunctions.remove_comments(c).replace("&", "") for c in check_line]
        full_line = " ".join(check_line)
        full_line = BasicFunctions.remove_spaces(full_line)
        var_name = BasicFunctions.remove_spaces(var_name)
        if full_line.count(var_name):
            original_module.lines[original_line.idx] = full_line
            original_module.lines[original_line.idx + 1: original_line.idx + original_line.n_of_merged_lines] = ""
            check_line = original_module.lines[original_line.idx: original_line.idx + original_line.n_of_merged_lines]
        else:
            raise Error.LineNotFound()
    for index, line in enumerate(check_line):
        # Avoid casting more than once but check if on another split line the variable is present
        if line.count(cast % var_name):
            purged_line = MaskCreator.remove_literals(line)
            name_occurrence = [i for i in re.findall(RegexPattern.escape_string(var_name), purged_line)]
            cast_occurrence = [i for i in re.findall(RegexPattern.escape_string(cast % var_name), purged_line)]
            if len(cast_occurrence) != len(name_occurrence):
                raise Error.ExceptionNotManaged("Line was not fixed properly: check")
            continue
        if line.count(var_name):
            assignation = re.search(RegexPattern.assignation, line, re.I)
            if assignation:
                new_line = Inserter.replace_variable_exact_match(var_name, cast % var_name, assignation.group(3))
                new_line = assignation.group(1) + new_line
            else:
                try:
                    new_line = Inserter.replace_variable_exact_match(var_name, cast % var_name, line)
                except Error.ExceptionNotManaged:
                    raise Error.ExceptionNotManaged
            return index + original_line.idx, new_line
    return index + original_line.idx, line


