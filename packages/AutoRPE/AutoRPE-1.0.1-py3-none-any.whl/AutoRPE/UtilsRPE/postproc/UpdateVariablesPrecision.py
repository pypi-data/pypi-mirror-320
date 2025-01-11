import AutoRPE.UtilsRPE.postproc.OriginalFilesManager as OriginalFilesManager
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.Classes.Procedure as Procedures
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.AttributeParser as AttributeParser
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.Error as Error
import re


def load_used_variables(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    used_variables = [l for l in lines]
    return [int(u.split()[0]) for u in used_variables]


def get_var_to_convert(root_namelist, vault):
    # Read the namelist, and set the proper precision to vault variables
    analyzed_variables = SourceManager.load_variable_list(root_namelist, vault, precision=True)

    # Set the final precision
    banned_variables = [v for v in analyzed_variables if v.type == 'dp']

    # Propagate dependencies of the variables using same_as property
    for n, var in enumerate(banned_variables):
        var.is_banned = True
        for additional_var_hash in var.same_as:
            # This loop could be simplified, but would cause a mem error
            additional_var = vault.get_variable_from_hash(additional_var_hash)
            if not additional_var.is_banned:
                additional_var.is_banned = True
                banned_variables.append(additional_var)
                additional_var.type = "dp"

    reduced_precision_variables = [a for a in analyzed_variables if a.type != 'dp']
    for var in reduced_precision_variables:
        for additional_var_hash in var.same_as:
            # This loop could be simplified, but would cause a mem error
            additional_var = vault.get_variable_from_hash(additional_var_hash)
            if additional_var not in reduced_precision_variables:
                if additional_var.is_banned:
                    raise Error.ExceptionNotManaged("Some problem with dependency")
                reduced_precision_variables.append(additional_var)
                additional_var.type = var.type
    single_precision_variables = list(set([b for b in reduced_precision_variables if b.original_type != b.type]))
    banned_variables = list(set([b for b in banned_variables if b.original_type in ['wp', 'sp']]))

    # Keep unique values of variables that really need to change precision
    return banned_variables, single_precision_variables


def update_variables_precision_preproc(vault, var_2be_changed_glo):
    """
    The purpose of this function is to modify the declarations of several variables in a source-code.

    - source_path: Path to a folder that contains the source files
    - var_to_be_changed: list of variables that will be modified in the code
    """
    for variable in var_2be_changed_glo:
        module = vault.modules[variable.procedure.module.name]
        procedure_name = variable.procedure.name
        declaration_line = [l for l in module.line_info if l.block.name == procedure_name][1:]
        for dl in declaration_line:
            m = re.search(RegexPattern.escape_string(variable.name), dl.unconditional_line)
            if m:
                declaration_line_without_comments, declaration_type, real_statement = \
                    check_declaration_precision(dl.unconditional_line)
                target_type = variable.type
                new_real_statement = real_statement.replace(declaration_type, target_type)
                module.lines[dl.line_number] = dl.line.replace(real_statement, new_real_statement)
                # Declaration has been updated, pass to next variable
                break


def update_variables_precision(original_modules, var_2be_changed_glo):
    """
    The purpose of this function is to modify the declarations of several variables in a source-code.

    - source_path: Path to a folder that contains the source files
    - var_to_be_changed: list of variables that will be modified in the code
    """

    # For every variable in the banned, searches declaration through source files and change declaration's precision
    already_changed_var = []
    for index, variable in enumerate(var_2be_changed_glo):
        # If we detect a line where more than a single var has to be changed, change all
        if variable not in already_changed_var:
            # This is the module where the variables appear declared once the code is preprocessed
            original_module = [m for m in original_modules if m.module_name == variable.module.name]

            if len(original_module) > 1 or not len(original_module):
                raise Error.ExceptionNotManaged

            original_module = original_module[0]
            # Skip variables in module example, that since is not really compiled contains errors
            if original_module.module_name == 'module_example':
                continue
            update_precision_declaration(variable, original_module, variable.type, var_2be_changed_glo,
                                         already_changed_var)
        # print("\rUpdated precision of var %i, %s " % (index, variable.name), end="")


def update_precision_declaration(variable, original_module, target_precision, var_2be_changed_glo, already_changed_var):
    """
    Find the file where a variable is declared and replace the declaration precision specification with target_precision
    """
    # Find the variable original module and line declaration, merge the line if is split
    try:
        original_module, index_to_modify = find_and_merge_variable_declaration_line(variable, original_module)
    except Error.ProcedureNotFound:
        # May happen with variables in subprograms generated by the preprocessor
        return

    line_to_modify = original_module.lines[index_to_modify]

    declaration_line_without_comments, comment = BasicFunctions.remove_comments(line_to_modify, return_comment=True)

    # Get the declaration precision, modify the line if precision was specified with a number
    declaration_line_without_comments, original_precision, real_statement = \
        check_declaration_precision(declaration_line_without_comments)

    # Avoid replacing variables whose precision was already of the correct type
    # TODO: these variables should not enter the analysis from the beginning
    if original_precision == target_precision:
        return

    # Check how many variables are declared on this line and which ones need changes
    if not NatureDeterminer.is_function_declaration_statement(declaration_line_without_comments):
        declared_var, var_2be_changed_inline = get_list_var2change(declaration_line_without_comments, variable,
                                                                   var_2be_changed_glo)
    else:
        # For function declaration just a var is declared and need change
        declared_var = [variable.name]
        var_2be_changed_inline = [variable]
    already_changed_var.extend(var_2be_changed_inline)
    # Will create a new line maintaining comment, spaces, old variables that do not need change in precision
    original_module.lines[index_to_modify] = replace_real_precision(var_2be_changed_inline,
                                                                    declared_var,
                                                                    declaration_line_without_comments,
                                                                    real_statement,
                                                                    original_precision, target_precision,
                                                                    comment,)
    original_module.update_module_lines()


def check_declaration_precision(line_to_modify):

    original_precision = re.search(RegexPattern.precision_of_real_declaration, line_to_modify, re.I)

    if original_precision:
        real_statement = original_precision.group()
        original_precision = original_precision.group(3)
    else:
        # Check the precision if precision is specified on numbers
        real_with_precision = re.search(RegexPattern.real_number_with_precision, line_to_modify, re.I)
        if real_with_precision:
            line_to_modify = line_to_modify.replace(real_with_precision.group(1), "")
        else:
            raise Error.ExceptionNotManaged("Precision was not found for this declaration")
        # Remove leading underscore
        original_precision = real_with_precision.group(2)
        # Add precision to the real declaration
        line_to_modify = re.sub(RegexPattern.name_occurrence % "REAL", "REAL(" + original_precision + ")",
                                line_to_modify)
        real_statement = "REAL(" + original_precision + ")"
    # Check the precision is correct
    try:
        VariablePrecision.lookup_table[original_precision]
    except KeyError:
        raise Error.ExceptionNotManaged("Something went wrong, %s is not a real precision" % original_precision)
    return line_to_modify, original_precision, real_statement


def get_list_var2change(declaration_line_without_comments, variable, var_2be_changed_glo):
    attributes, arguments = declaration_line_without_comments.split("::")
    variable_names = AttributeParser.get_variable_name(arguments, original_file=True)
    var_2be_changed_inline = [variable]
    declared_var_list = [variable.name]
    if len(variable_names) > 1:
        for name in variable_names:
            # Avoid adding the same variable twice
            if name != variable.name:
                # Generate the variable hash starting from the known attributes
                var_hash = BasicFunctions.hash_from_list([name, variable.procedure.name, variable.module.name])
                # Check if the variable is among the variables that need to change precision
                declared_var = [v for v in var_2be_changed_glo if v.hash_id == var_hash]
                if not declared_var:
                    declared_var_list.append(name)
                else:
                    declared_var_list.append(declared_var[0].name)
                # If a var was found, check the two variables have the same precision (this check may be unnecessary)
                if declared_var and declared_var[0].type == variable.type:
                    # Add to the list of var that will be changed
                    var_2be_changed_inline.append(declared_var[0])
    return declared_var_list, var_2be_changed_inline


def replace_real_precision(variable_list, declared_var, declaration_line, real_statement, original_precision,
                           target_precision, comment=""):
    """This function takes a declaration line (string) and updates it with the new type
    If the declaration contains more variables it keeps the other variables with the original attributes"""
    old_declaration_line = ""
    if len(declared_var) != len(variable_list):
        # These will be string, and not obj, since are not in the list of var to change we don't have their obj
        unchanged_var = [v for v in declared_var if v not in [v.name for v in variable_list]]
        var_to_change = [v.name for v in variable_list]
        # Create a line with old declaration, and variables thant need to retain original precision
        old_declaration_line = declaration_line.split("::")[0] + " :: " + ", ".join(unchanged_var) + comment + "\n"
        # Create new line with variables that need new precision
        declaration_line = declaration_line.split("::")[0] + " :: " + ", ".join(var_to_change)

    # Update precision in the new declaration
    new_real_statement = real_statement.replace(original_precision, target_precision)
    new_declaration_line = declaration_line.replace(real_statement, new_real_statement)
    new_declaration_line = declaration_line.replace(declaration_line, new_declaration_line) + comment

    return old_declaration_line + new_declaration_line


def find_and_merge_variable_declaration_line(variable, module):
    """
    Given a variable and a module:
              1) Search for the variable.subprogram declaration
              2) Among the declarations search the variable.name
              3) If the variable declaration is split, merge the line and update both the module and the index
    Returns the index
    """

    # The var is a global variable, declared at the beginning of a module
    if variable.procedure.name == "main":
        start, end = OriginalFilesManager.find_main_declarations_index(module)
    # The variable is member of a structure
    elif isinstance(variable.procedure, Procedures.DerivedType):
        start, end = OriginalFilesManager.find_structure_declarations_index(variable.procedure, module)
    # The variable is a private var of a subprogram
    else:
        module, [start, end] = OriginalFilesManager.find_subprogram_declarations_index(variable.procedure, module)

    declaration_index = None
    for index, line in enumerate(module.lines[start:end + 1]):
        # Skip lines that contains just comments
        line = BasicFunctions.remove_comments(line)
        if not line.strip():
            continue
        # The first match will be declaration, since we are checking only declaration lines
        if variable.dimension > 0:
            if re.search(RegexPattern.escape_string(variable.name), line) or re.search(RegexPattern.escape_string(variable.name+'('), line):
                # Check declaration is on the same line of precision specification
                declaration_index = start + index
                if not line.count('::') or line.count("&"):
                    # It rebuilds split line inside the module object and return merged line, and updated index
                    declaration_index = OriginalFilesManager.rebuild_split_line(declaration_index, module)
                break
        else:
            if re.search(RegexPattern.escape_string(variable.name), line):
                # Check declaration is on the same line of precision specification
                declaration_index = start + index
                if not line.count('::') or line.count("&"):
                    # It rebuilds split line inside the module object and return merged line, and updated index
                    declaration_index = OriginalFilesManager.rebuild_split_line(declaration_index, module)
                break


    if declaration_index is None:
        if variable.is_retval:
            return OriginalFilesManager.find_function_type_specification(variable.procedure, module)
        else:
            # The var can be declared in some .h90 included file
            for header in module.header_files:
                try:
                    return find_and_merge_variable_declaration_line(variable, header)
                except (Error.LineNotFound, Error.ProcedureNotFound) as e:
                    continue
        raise Error.LineNotFound("Line not found")

    # Return original module object  and index of the declaration
    return module, declaration_index


def remove_CAST(original_modules):
    for module in original_modules:
        for line_idx, line in enumerate(module.lines):
            if module.module_name == 'single_precision_substitute':
                continue
            cast = [c.start() for c in re.finditer(RegexPattern.CAST, line)]
            for i_cast in cast[::-1]:
                cast_call = BasicFunctions.close_brackets(line[i_cast:])
                cast_argument = CallManager.find_call_arguments(cast_call)
                if len(cast_argument) != 1:
                    raise Error.ExceptionNotManaged("CAST should have just one argument, check")
                cast_argument = cast_argument[0]
                module.lines[line_idx] = module.lines[line_idx].replace(cast_call, cast_argument)
