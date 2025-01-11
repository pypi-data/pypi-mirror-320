import AutoRPE.UtilsRPE.Classes.Procedure as Procedure
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.Getter as Getter
import warnings
import re

from os.path import join, isfile


def insert_use_rp_emulator_in_function(func_name: str, module: 'Module'):
    """
    Inserts a 'USE rp_emulator' statement after the function declaration in the module.

    Parameters:
        func_name (str): The name of the function to search for.
        module (Module): The module to modify.
    """
    for idx, line in enumerate(module.lines):
        if re.search(RegexPattern.subprogram_name_declaration % func_name, line, flags=re.IGNORECASE):
            module.lines.insert(idx + 1, "USE rp_emulator")
            return


def insert_use_statement(vault: 'Vault'):
    """
    Adds 'USE rp_emulator' and 'USE read_precisions' to all modules and abstract interfaces
    that contain a variable of type 'rpe_var'.

    Parameters:
        vault (Vault): The vault containing the modules and interfaces to modify.
    """
    # Adding module rp_emulator (in theory adding this to par_kind.f90 should be enough,
    # but theory fails and compiler complains so I'll add it everywhere
    for module in vault.modules.values():
        module.lines.insert(1, "\nUSE rp_emulator\nUSE read_precisions\n")
        module.update_module_lines()

    # Add USE rp_emulator to the abstract interfaces with rpe_var
    for interface in vault.interfaces_dictionary.values():
        if interface.is_abstract:
            # Check the different subprograms and variables
            for subprogram in interface.subprogram:
                for v in subprogram.variables:
                    if v.type == 'rpe_var':
                        # Add the statement
                        insert_use_rp_emulator_in_function(subprogram.name, interface.module)
                        interface.module.update_module_lines()
                        break


def create_read_precisions_module(path_to_sources: str, vault: 'Vault'):
    """
    Generates a Fortran module to read precision namelist and writes it to a file.

    Parameters:
        path_to_sources (str): The directory path where the module should be saved.
        vault (Vault): The vault containing the variables to be processed.
    """
    from os.path import dirname, abspath
    print("\n\nCreating module to read precision namelist...")

    # Get the number of rpe variables
    rpe_vars = [var for var in vault.variables if var.id is not None]
    rpe_vars.sort(key=lambda x: x.id)
    rpe_vars_number = len(rpe_vars)
    # Store information to be printed in used variables
    variables_info = ["\tvariable_info( % i) = \"!\t%s\t%s\t%s\"" %
                      (v.id, v.name, v.procedure.name, v.module.name) for v in rpe_vars]

    # Path to template is hardcoded
    package_directory = dirname(abspath(__file__))
    filename = package_directory + "/../AdditionalFiles/read_precisions_template"

    with open(filename, "r") as input_file:
        template = input_file.read()
    module = template.replace("%NUMBER_OF_RPE_VARS%", str(rpe_vars_number))
    module = module.replace("%VARIABLES_INFO%", "\n".join(variables_info))
    with open(join(path_to_sources, "read_precisions.f90"), "w") as output_file:
        output_file.write(module)


def add_sbits_to_rpe_variables(vault: 'Vault'):
    """
    Assigns significant bits to RPE variables, truncating them based on their attributes.

    Parameters:
        vault (Vault): The vault containing the variables to be processed and truncated.
    """
    print("\n\nAssigning significant bits...")

    def condition(v):
        return v.type == "rpe_var" and not v.is_parameter

    # List rpe variables
    rpe_variables = [var for var in vault.variables if condition(var)]
    # Split between allocatable and non allocatable, since they have to be truncate in different places
    allocatable, non_allocatable = split_vars_by_allocatable(rpe_variables)

    # # List types with allocatable members
    # type_with_allocatable_member = list(set([a.is_member_of.lower() for a in allocatable if a.is_member_of]))
    #
    # # List variables with allocatable members
    # var_with_rpe_allocatable_member = [var for var in vault.variables if
    #                                    var.type.lower() in type_with_allocatable_member]
    # Remove allocatable members from the list of allocatable
    allocatable = [a for a in allocatable if not a.is_member_of]

    # List non allocatable that appear in a namelist
    na_in_namelist, na_not_in_namelist = split_by_appearance_in_namelist(non_allocatable)
    # Truncate variables with allocatable rpe members
    # for variable in var_with_rpe_allocatable_member:
    #     insert_variable_precision_specification_to_allocatable_member(variable, var_counter, vault)

    # List var not declared as global, and divide between simple var and derived type with rpe member
    not_main_rpe_member, not_main, main = split_vars_by_main(na_not_in_namelist, vault)

    # List of all rpe var
    var_to_truncate = allocatable + na_in_namelist + not_main + main

    # Sort the list alphabetically so that namelist ordering won't depend on the platform
    var_to_truncate.sort(key=lambda x: x.name + x.procedure.name + x.module.name)

    # Assign a progressive id
    for index_var, var in enumerate(var_to_truncate):
        var.id = index_var
    # Now that id have been assigned, fill dictionary ids
    vault.index_variables()
    # Insert truncation statement

    # Truncate allocatable
    for variable in allocatable:
        insert_variable_precision_specification_to_allocatable(variable)

    # Truncate non allocatable that appear in a namelist
    for variable in na_in_namelist:
        insert_variable_precision_specification_to_namelist_parameter(variable, vault)

    # # Truncate variable of custom data type with rpe member
    # for variable in not_main_rpe_member:
    #     if not isinstance(variable.procedure, BasicStructures.DerivedType) and variable.intent != "in":
    #         insert_variable_precision_to_output_dummy_with_rpe_member(variable, var_counter, vault)

    # Truncate subroutine dummies with intent out (cut just after declaration)
    for variable in not_main:
        if not isinstance(variable.procedure, Procedure.DerivedType) and variable.intent != "in":
            insert_variable_precision_to_output_dummy(variable)

    # Truncate after subroutine calls for actual arguments with intent out
    insert_variable_precision_after_subroutine_call(vault)

    # Insert a function for each module, where module variables will be assigned and id and a precision
    insert_variable_precision_to_main_variable(main, vault)


def _insert_check(if_condition, module_line, var_id, check=True):
    """Once all the unused variables are set to 3 bits,
    this will stop if encounters once such variable, since it means it ended up in the analysis by mistake"""
    # This function is intended for debug only, usually we don't want these lines to be in the code
    if not check:
        module_line
    # If an if condition is present, add the check to this
    if if_condition.strip():
        # Remove the last parenthesis
        if_condition = if_condition.strip()[:-1]
        # Complete if statement and add print
        if_condition += " .and. emulator_variable_precisions(%i) == 3)" % var_id
    else:
        # Create if condition
        if_condition = "    IF(emulator_variable_precisions(%i) == 3)" % var_id

    # Insert conditional check and print
    module_line += "\n" + if_condition + " ERROR STOP %i" % var_id
    return module_line


def _add_argument_truncation(subprogram_call):
    # Check the intent and type of the arguments
    variables_to_truncate = []
    for arg, dummy_a in zip(subprogram_call.arguments, subprogram_call.dummy_arguments):
        # Do not check non real variables or var that correspond to an intent in dummy
        if arg.type != 'rpe_var' or dummy_a.intent == 'in':
            continue
        # The var can not be None: since the intent is out, must be a single var
        # TODO remove this check, it has been substituted by the check_argument_consistency
        if arg.variable is None:
            raise Error.IntentOutError("The dummy argument %s of procedure %s has intent %s but is used"
                                       "like %s " % (dummy_a.name, dummy_a.procedure.name, dummy_a.intent, arg.name))
        # If id is not yet assigned at this point, it means it does not enter the analysis, skip
        if arg.variable.id is not None:
            variables_to_truncate.append([arg.variable, arg.variable.is_pointer])

    call_to_subroutine = subprogram_call.line_info.line
    for var, is_pointer in variables_to_truncate:
        # if is_pointer:
        #     # Remove indexing to avoid
        #     # error #7835: Record fields or array elements or sections of pointers are not themselves pointers.
        #     if var.count("%"):
        #         indexed_member = var.split("%")[-1]
        #         member_name = BasicFunctions.remove_indexing(indexed_member)
        #         deindexed_var = var.replace(indexed_member, member_name)
        #     else:
        #         deindexed_var = BasicFunctions.remove_indexing(var)
        # call_to_subroutine += "if(associated(%s)) then\n" % deindexed_var
        call_to_subroutine = insert_variable_precision_specification(var,
                                                                     call_to_subroutine,
                                                                     subprogram_call.line_info.if_condition,
                                                                     apply_truncation=True)
        # if is_pointer:
        #     call_to_subroutine += "\nend if"

    return call_to_subroutine


def insert_variable_precision_specification(variable: 'Variable', module_line: str,
                                            if_condition: str="",
                                            member_name: str=None,
                                            apply_truncation: bool=False):
    """
    Adds variable precision specification to a module line, with optional truncation and condition checks.

    Parameters:
        variable (Variable): The variable whose precision is to be specified.
        module_line (str): The module line to which the specification is added.
        if_condition (str, optional): A condition to be applied before the specification (default is "").
        member_name (str, optional): The name of the member to use, if the variable is part of a structure (default is None).
        apply_truncation (bool, optional): Whether to apply truncation to the variable (default is False).

    Returns:
        str: The updated module line with the precision specification.
    """
    # Set the variable to mutable
    variable.is_mutable = True
    # Get name of variable, or of member if specified
    var_name = member_name if member_name else variable.name
    var_id = variable.id
    # if variable.is_pointer and not variable.is_allocatable:
    #     module.lines[insertion_line] += "\nif(associated(%s)) then" % var_name

    # Add variable usage specification
    module_line += "\n" + if_condition + "    variable_is_used(%i) = .true." % var_id

    # Add sbits
    module_line += "\n" + if_condition + "    %s%%sbits = emulator_variable_precisions(%i)" % (var_name, var_id)
    # Insert a check, that ensures that all the truncated variables have been assigned a precision
    # module_line = _insert_check(if_condition, module_line, var_id)

    # Add apply_truncation if is variable declaration or allocation
    if apply_truncation:
        module_line += "\n" + if_condition + "    CALL apply_truncation(%s)" % var_name

    # if variable.is_pointer and not variable.is_allocatable:
    #     module.lines[insertion_line] += "\nend if"
    return module_line


def _get_member_name(arg, module, line_index, vault, variable):
    # Remove leading spaces
    arg = arg.replace(" ", "").strip()

    # Get variable name without indexing (foo(n)%var --> foo%var)
    clean_contents = BasicFunctions.remove_indexing(arg)
    member_type = Getter.get_type_of_contents(clean_contents, module.line_info[line_index].block, vault)

    # Get the variable
    if clean_contents.count("%"):
        var = Getter.get_structure_member(clean_contents, module.line_info[line_index].block, vault)
    else:
        var = vault.get_variable_by_name(clean_contents, module.line_info[line_index].block)

    # Fix only if it's an rpe_var and it's the "same" variable
    if member_type != 'rpe_var' or not variable.is_equal_to(var):
        return None

    return arg.split(variable.name)[0] + variable.name


def insert_variable_precision_specification_to_allocatable(variable: 'Variable'):
    """
    Searches for the allocation of a variable and applies truncation afterward.

    Parameters:
        variable (Variable): The allocatable variable for which precision specification is to be inserted.

    Returns:
        None
    """

    def find_variable(var, li, l, m):
        if re.search(RegexPattern.allocation_variable_name % var.name, l, re.I):
            # Check that we did not match a member with the same name: a_i will also match %a_i
            if re.search(RegexPattern.allocation_member_name % var.name, l.replace(" ", ""), re.I):
                return False

            m.lines[li] = insert_variable_precision_specification(var, m.lines[line_index], apply_truncation=True)
            m.update_lineinfo()
            return True

    if variable.procedure.name == 'main':
        # Search in all modules
        for module in [variable.module] + variable.procedure.module.used_by:
            for line_index, line in enumerate(module.lines):
                # Variables can be allocated just inside subprograms
                if not module.line_info[line_index].block.name == 'main':
                    if find_variable(variable, line_index, line, module):
                        return
    else:
        # Just search where the variable is defined
        module = variable.module
        lines = [[i, l.unconditional_line] for i, l in enumerate(module.line_info)
                 if l.block.name == variable.procedure.name]
        for line_index, line in lines:
            if find_variable(variable, line_index, line, module):
                return


def _find_member_allocation(_module_lines, _var_name, _member_name):
    for index, line in enumerate(_module_lines):
        if re.search(RegexPattern.allocation_variable_name % _var_name, line, re.I):
            # Get the arguments from ALLOCATE, avoiding any possible extra call or IF statement inline
            arguments = CallManager.find_call_arguments(BasicFunctions.remove_if_condition(line))
            for arg in arguments:
                cleaned_arg = BasicFunctions.remove_indexing(arg)
                if re.search(RegexPattern.name_occurrence % _member_name, cleaned_arg, re.I):
                    # Return line and allocation removing index of the member
                    return index, arg.split(_member_name)[0] + _member_name
    return None, None


def insert_variable_precision_specification_to_allocatable_member(variable: 'Variable', counter_object, vault: 'Vault'):
    """
    Searches for allocatable members of a variable's type and applies precision truncation to them.

    Parameters:
        variable (Variable): The variable whose allocatable members will be processed.
        counter_object: The counter for assigning unique IDs to members.
        vault (Vault): The vault containing the variables and modules.

    Returns:
        None
    """
    def _condition(var, structure):
        # Is an rpe member of the encompassing structure with the pointer or allocatable attribute
        if var.type == 'rpe_var':
            if var.is_member_of and var.is_member_of.lower() == structure and (var.is_allocatable or var.is_pointer):
                return True
        return False

    allocatable_members = [var for var in vault.variables if _condition(var, variable.type.lower())]
    for member in allocatable_members:
        for module in [variable.module] + variable.procedure.module.used_by:
            line_index, member_allocation = _find_member_allocation(module.lines, variable.name, member.name)
            if line_index:
                # Set member id if it was not set yet
                if member.id is None:
                    member.id = counter_object.count
                    counter_object.up()
                # Cut member precision
                module.lines[line_index] = insert_variable_precision_specification(member, module.lines[line_index],
                                                                                   member_name=member_allocation,
                                                                                   apply_truncation=True)
                module.update_lineinfo()
                # Search for next member allocation
                break


def insert_variable_precision_specification_to_namelist_parameter(variable: 'Variable', vault: 'Vault'):
    """
    Inserts variable precision specification to a namelist parameter in the corresponding module.

    Parameters:
        variable (Variable): The variable to be processed.
        vault (Vault): The vault containing the modules and variables.

    Returns:
        None
    """
    module = vault.modules[variable.appears_in_namelist[0]]
    for index, line in enumerate(module.lines):
        pattern3 = r"read *\(.*\b%s\b" % variable.appears_in_namelist[1]
        if re.search(pattern3, line, re.I):
            break
    module.lines[index] = insert_variable_precision_specification(variable, module.lines[index], apply_truncation=True)
    module.update_lineinfo()


def _find_name_to_cut(line, variable, member):
    # Case in which a variable was inside a do loop or a where statement
    if variable.dimension == 0 or not line.count(variable.name):
        return variable.name + "%" + member.name
    # Try to find de exact variable call
    start_of_name = re.search(RegexPattern.name_occurrence % variable.name, line)
    if start_of_name:
        start_of_name = start_of_name.start()
    else:
        raise Error.ExceptionNotManaged("Name should be here")

    var_name = line[start_of_name:].split(member.name)[0]
    return var_name + member.name


def insert_variable_precision_to_output_dummy_with_rpe_member(variable, counter_object, vault):
    """
    Inserts variable precision specification for an rpe member in the output dummy.

    Parameters:
        variable (Variable): The variable to be processed.
        counter_object: The counter for assigning ids.
        vault (Vault): The vault containing the variables and modules.

    Returns:
        None
    """
    def _condition(var, struct):
        # Is an rpe member of the encompassing struct with the pointer or allocatable attribute
        if var.type == 'rpe_var':
            if var.is_member_of and var.is_member_of.lower() == struct and not (var.is_allocatable or var.is_pointer):
                return True
        return False

    rpe_members = [var for var in vault.variables if _condition(var, variable.type.lower())]
    for member in rpe_members:
        module, insert_line, condition = find_first_use_of_member(variable, member)
        if module:
            # Check that this member was not assigned when used in another variable
            if member.id is None:
                member.id = counter_object.count
                counter_object.up()
            first_use_line = module.lines[insert_line + 1]
            member_name = _find_name_to_cut(first_use_line, variable, member)
            # Cut member precision
            module.lines[insert_line] = insert_variable_precision_specification(member, module.lines[insert_line],
                                                                                condition,
                                                                                member_name=member_name,
                                                                                apply_truncation=True)
            module.update_lineinfo()
        else:
            warnings.warn("Variable %s not found %s in routine %s" % (
                variable.name, variable.procedure.module.name, variable.procedure.name))


def insert_variable_precision_after_subroutine_call(vault: 'Vault'):
    """
    Inserts truncation statements after each subroutine call for variables with intent 'out'.

    Parameters:
        vault (Vault): The vault containing the subprogram calls.

    Returns:
        None
    """
    for subprogram_call in vault.dictionary_of_calls.values():
        # No need to check function, inputs are ~copied, and sbits member will stay constant
        if isinstance(subprogram_call[0].subprogram, Subprogram.Function):
            continue
        for call in subprogram_call:
            module = call.block.module
            line_number = call.line_info.line_number
            # Update calls
            line_plus_truncation = _add_argument_truncation(call)
            if line_plus_truncation is not None:
                module.lines[line_number] = line_plus_truncation


def add_val_to_argument(argument: str, string: str):
    """
    Replaces occurrences of the argument with its '%val' version in the string.

    Parameters:
        argument (str): The argument to be replaced.
        string (str): The string where the replacement occurs.

    Returns:
        str: The string with the replaced argument.
    """
    string = replace_variable_exact_match(argument, argument + "%val", string)
    return string


def add_rpe_real_member_to_argument(argument: str, string: str):
    """
    Replaces occurrences of the argument with its '%val' version in the string, handling hardcoded arrays.

    Parameters:
        argument (str): The argument to be replaced.
        string (str): The string where the replacement occurs.

    Returns:
        str: The string with the replaced argument.
    """
    hardcoded_array = []
    if NatureDeterminer.is_hardcoded_array(argument, hardcoded_array):
        for arg in hardcoded_array:
            string = replace_variable_exact_match(arg, arg + "%val", string)
        return string
    return replace_variable_exact_match(argument, argument + "%val", string)


def add_rpe_to_argument(argument: str, string: str, is_pointer: bool=False):
    """
    Adds an 'rpe' or 'rpe_ptr' cast to the argument in the string if not already cast.

    Parameters:
        argument (str): The argument to be cast.
        string (str): The string where the replacement occurs.
        is_pointer (bool, optional): Whether to use 'rpe_ptr' for pointer types. Defaults to False.

    Returns:
        str: The string with the casted argument.
    """
    if is_pointer:
        cast_rpe = 'rpe_ptr(%s)'
    else:
        cast_rpe = 'rpe(%s)'
    # Check we are not casting more than once
    if not string.count(cast_rpe % argument) == string.count(argument):
        if NatureDeterminer.is_hardcoded_array(argument):
            string = string.replace(argument, add_rpe_to_array_arguments(argument))
        else:
            string = replace_variable_exact_match(argument, cast_rpe % argument, string)
    return string


# Transforms a number in an rpe variables =>  1.0 in rpe( 52, 1.0). Used to fix parameters assignation
def add_rpe_type_constructor(argument: str, string: str):
    """
    Adds an 'rpe' constructor to the argument in the string, handling reshapes and arrays.

    Parameters:
        argument (str): The argument to be cast.
        string (str): The string where the replacement occurs.

    Returns:
        str: The string with the rpe constructor applied.
    """
    # Deal with cases of array or reshape functions
    if argument.count("RESHAPE") or re.search(r"= *\[.*\]", argument):
        # List the arguments inside the RESHAPE function and avoid adding the cast to dimensions
        argument = CallManager.find_call_arguments(argument)[0]
        return replace_variable_exact_match(argument, add_rpe_to_array_arguments(argument), string)
    if argument.count("(/"):
        # Add rpe constructor to all numbers inside the array
        return replace_variable_exact_match(argument, add_rpe_to_array_arguments(argument), string)

    return replace_variable_exact_match(argument, "rpe_var( 52, " + argument + ")", string)


def add_real_to_argument(argument: str, string: str, precision: str=VariablePrecision.real_id["wp"]):
    """
    Adds 'real' type casting with specified precision to the argument in the string if not already cast.

    Parameters:
        argument (str): The argument to be cast.
        string (str): The string where the replacement occurs.
        precision (str, optional): The precision to apply. Defaults to VariablePrecision.real_id["wp"].

    Returns:
        str: The string with the real-cast argument.
    """
    # Check we are not casting more than once or fixing an arg already fixed
    precision = ", " + precision
    if string.count("real(" + argument + precision + ")") == string.count(argument):
        return string

    # # Avoid add real to all array element if is an array with a loop
    # if NatureDeterminer.is_an_hardcoded_array(argument) and \
    #         not NatureDeterminer.is_an_hardcoded_array_with_loop(argument):
    #     new_arg = add_real_to_array_arguments(argument)
    #
    # else:
    new_arg = "real(" + argument + precision + ")"

    string = replace_variable_exact_match(argument, new_arg, string)
    return string


def add_real_to_array_arguments(argument: str):
    """
    Casts each element of the array argument to 'real' with 'wp' precision.

    Parameters:
        argument (str): The array argument to be cast.

    Returns:
        str: The array argument with each element cast to 'real(wp)'.
    """
    simple_array = argument.replace("(/", "")
    simple_array = simple_array.replace("/)", "")
    clean_numbers = CallManager.find_call_arguments("(" + simple_array + ")")
    # Open the array
    ret_val = "(/"
    for number in clean_numbers:
        # Cast all array numbers
        ret_val += "real(" + number + " , wp), "
    # Remove last comma and closes array
    ret_val = ret_val[:-2] + "/)"
    return ret_val


def add_rpe_to_array_arguments(argument: str):
    """
    Casts each element of the array argument to 'rpe_var( 52, ... )'.

    Parameters:
        argument (str): The array argument to be cast.

    Returns:
        str: The array argument with each element cast to 'rpe_var( 52, ... )'.
    """
    if re.search(RegexPattern.hardcoded_array_parenthesis, argument): arg1, arg2 = "(/", "/)"
    if re.search(RegexPattern.hardcoded_array_brackets, argument): arg1, arg2 = "[", "]"

    simple_array = argument.replace(arg1, "")
    simple_array = simple_array.replace(arg2, "")
    clean_numbers = CallManager.find_call_arguments("(" + simple_array + ")")
    # Open the array
    ret_val = arg1
    for number in clean_numbers:
        # Cast all array numbers
        ret_val += "rpe_var( 52, " + number + " ), "
    # Remove last comma and closes array
    ret_val = ret_val[:-2] + arg2
    return ret_val


def replace_variable_exact_match(piece_to_replace: str, replacement: str, string: str):
    """
    Replaces exact occurrences of a variable in the string, ensuring no internal replacements occur.

    Parameters:
        piece_to_replace (str): The variable to be replaced.
        replacement (str): The replacement for the variable.
        string (str): The string where the substitution occurs.

    Returns:
        str: The string with the exact replacement applied.
    """
    # Before performing the substitution mask strings to avoid substitution inside them
    dict_of_substitutions = {}
    string = MaskCreator.mask_literal(string, dict_of_substitutions)

    # Mask the keyword if the argument is passed with the same name as the keyword
    string = MaskCreator.mask_keyword(string, piece_to_replace, dict_of_substitutions)
    # Perform substitution, escaping the string
    string = re.sub(RegexPattern.escape_string(piece_to_replace), replacement, string)
    # Substitute back masked objects
    string = MaskCreator.unmask_from_dict(string, dict_of_substitutions)

    if not string.count(replacement):
        pass
        # raise Error.ExceptionNotManaged("Impossible substitution: %s in line %s" % (replacement, piece_to_replace))

    return string


def find_subprogram_lines(subprogram: Subprogram, module: 'Module'=None):
    """
    Finds the lines in a module corresponding to the start and end of a subprogram.

    Parameters:
        subprogram (Subprogram): The subprogram whose lines are to be found.
        module (Module, optional): The module to search in. Defaults to None, in which case the subprogram's module is used.

    Returns:
        tuple: A tuple containing the module and a list with the start and end line indices of the subprogram.

    Raises:
        Error.ProcedureNotFound: If the subprogram is not found in the module or its header files.
    """
    indices = []

    if module is None:
        module = subprogram.module
    begin_pattern = RegexPattern.subprogram_name_declaration % subprogram.name
    end_pattern = RegexPattern.subprogram_name_end_declaration % subprogram.name
    # First find the subprogram body inside the module
    for index, line in enumerate(module.lines):
        # If it's the start or end of the subprogram
        line = BasicFunctions.remove_comments(line)
        if re.search(begin_pattern, line, re.I):
            indices.append(index)
            # End of the program was hit
            if re.search(end_pattern, line, re.I):
                break
    if not len(indices):
        for h in module.header_files:
            try:
                return find_subprogram_lines(subprogram, h)
            except Error.ProcedureNotFound:
                continue
        raise Error.ProcedureNotFound(" Procedure %s not found" % subprogram.name)
    # In case more than one start/end index was found:
    #
    #   #if defined key_agrif
    #      RECURSIVE SUBROUTINE stp_MLF( )
    #         INTEGER             ::   kstp   ! ocean time-step index
    #   #else
    #      SUBROUTINE stp_MLF( kstp )
    #         INTEGER, INTENT(in) ::   kstp   ! ocean time-step index
    #   #endif
    #
    # return the broader range
    return module, [indices[0], indices[-1]]


## PRIVATE

def insert_variable_precision_to_main_variable(in_main: list['Variable'], vault: 'Vault'):
    """
    Inserts truncation for all global variables with no first use tracking.

    For each module that contains global variables, it creates a subroutine to assign 
    precision truncation and adds a call to this subroutine in the main program.

    Parameters:
        in_main (list): List of global variables in the main program.
        vault (Vault): The vault containing all modules and variables.
    
    Updates:
        Modifies the lines of relevant modules to include truncation subroutines 
        and appropriate calls to these subroutines in the main program.

    Note:
        This function handles the insertion of the `assign_sbits` subroutine and 
        ensures that necessary `USE` statements and `CALL` statements are added.
    """
    subroutine_calls = ""
    used_module = ""
    for module in vault.modules.values():
        module_variables = [v for v in in_main if v.module == module]
        # There are no rpe global variable in this module: skip
        if not module_variables:
            continue
        # Update line info, not updated after insert truncation to sbr
        module.update_lineinfo()
        # Name of the subroutine must be different for each module
        subroutine_name = "assign_sbits_" + module.name
        subroutine_text = "\n    implicit none"
        for var in module_variables:
            # Add the assignation in the subroutine call
            subroutine_text += insert_variable_precision_specification(var, "", apply_truncation=True)

        subroutine = "SUBROUTINE " + subroutine_name + "".join(subroutine_text) + "\nEND SUBROUTINE " + subroutine_name
        contain_index = len(module.lines)
        for line_index, line in enumerate(module.lines):
            # Insert the subroutine as first subprogram of the module
            if re.search(RegexPattern.name_occurrence % "contains", line, re.I):
                contain_index = line_index
                module.lines[contain_index+1] = subroutine + "\n" + module.lines[contain_index+1]
                break
        # If the module just contains variables declaration add contain statement before the module ends
        if contain_index == len(module.lines):
            contain_index = -1
            module.lines[contain_index] = "CONTAINS\n" + subroutine + "\n" + module.lines[contain_index]

        # executable_part_index = module.main.executable_part()
        # Just before the contains statement include the declaration of function as public
        module.lines[contain_index] = "PUBLIC " + subroutine_name + "\n" + module.lines[contain_index]
        # module.lines[executable_part_index] = "PUBLIC " + subroutine_name + "\n" + module.lines[contain_index]
        module.update_module_lines()
        # Store all subroutine names that will be call in nemogcm
        subroutine_calls += "CALL " + subroutine_name + "\n"
        # Store modules names, they will be added to the use statement of nemogcm
        used_module += "USE " + module.name + "\n"
    # insert_module = vault.modules['nemogcm']
    #Trying to find the main module:
    unused_modules = [mod for mod in vault.modules.values() if not mod.used_by]
    if len(unused_modules) == 1:
        insert_module = unused_modules[0]
    #TODO: Find a better non hardcoded way of solving this with NEMO.
    elif [m for m in unused_modules if m.name == "nemogcm"]:
        insert_module = vault.modules['nemogcm']
    # If the preprocessed files include the main program nemo, then nemogcm is not unused anymore. Adding it here just to be safe.
    elif [m for m in unused_modules if m.name == "nemo"]:
        insert_module = vault.modules['nemo']
    else:
        insert_module = vault.modules['dummy_module']
    
    
    # Here, we try to find the proper place to insert the calls to asign sbits
    # This should happen after all variable declarations
    
    declaration_lines = [i for i, l in enumerate(insert_module.lines) if re.search(RegexPattern.variable_declaration , l, re.I)]

    if declaration_lines:
        line_index = declaration_lines[-1]
    else:
        line_index = 1
    # implicit_nones = [i for i, l in enumerate(insert_module.lines) if l.lower().count("implicit none")]
    # if implicit_nones:
    #     line_index = implicit_nones[0]
    # else:
    #     line_index = 1
    subroutine_calls = "CALL read_variable_precisions\n" + subroutine_calls
    insert_module.lines[line_index] += "\n" + subroutine_calls
    # Find first use statement (no need to rebuild text, this is before all the calls)
    line_index = [i for i, l in enumerate(insert_module.lines) if l.count("USE ")][0]
    insert_module.lines[line_index] += "\n" + used_module
    
    # TODO: Is this necessary?
    implicit_nones = [i for i, l in enumerate(insert_module.lines) if l.lower().count("implicit none")]
    if implicit_nones:
        line_index = implicit_nones[0]
    else:
        line_index = 1

    # insert_module.lines[line_index] += "\n" + used_module
    # TODO: this it does not take into account the new sbr, so after this call all lineinfo will be wrong,
    # here info lines should be recreated,
    # but this is very expensive, and we are not going to use it anymore at this point
    insert_module.update_module_lines()


def insert_variable_precision_to_output_dummy(variable: 'Variable'):
    """
    Inserts truncation for dummy arguments in the output, searching for the first line of code after variable declarations.
    Adds truncation logic to the first line of code in the subprogram where no variables are declared, handling optional variables
    with a conditional check for their presence.

    Parameters:
        variable (Variable): The variable for which truncation is to be added.

    Returns:
        None
    """
    module = variable.procedure.module
    lines = [[i, l.unconditional_line] for i, l in enumerate(module.line_info)
             if l.block.name == variable.procedure.name]
    # Insert the use statement just after variables declaration
    line_number, insertion_line = [[i, l] for i, l in lines if l.count("::")][-1]
    if variable.is_optional:
        condition = "IF ( PRESENT(%s) )" % variable.name
    else:
        condition = ""
    module.lines[line_number] = insert_variable_precision_specification(variable, module.lines[line_number], condition,
                                                                        apply_truncation=True)
    module.update_lineinfo()


def find_first_use_of_member(variable: 'Variable', member: 'Variable'):
    """
    Finds the first use of a member variable in a subprogram, skipping declarations, implicit statements, and use statements.

    Searches through the subprogram lines after the declaration to find the first occurrence of the member variable,
    considering loops and where statements to avoid incorrect matches.

    Parameters:
        variable (Variable): The parent variable whose member's usage is being tracked.
        member (Variable): The member variable to search for.

    Returns:
        tuple: The module and line index where the member is first used, along with any condition string if present.
    """
    # Is it possible that var.module != subprogram.module?!
    subprogram = variable.procedure
    module = subprogram.module

    # pattern = '(^|\W+)%s(\W+|$)' % variable.name
    loop_level = 0
    loop_start = None
    where_level = 0
    where_statement_start = None

    # Find start and end of subprogram declaration
    module, indices = find_subprogram_lines(subprogram)

    # Search for first use, avoiding subprogram declaration and end lines
    # We will need to add indices[0] - 1 to the line_index return value since that's our starting index
    for line_index, line in enumerate(module.lines[indices[0] + 1:indices[1]]):
        # Skip all declarations to avoids false positive that will block compilation.
        if line.count("::") or line.lower().count("implicit none") or line.find("use ") == 0:
            continue

        # Scroll subprogram's lines searching for the first use
        if re.search(RegexPattern.name_occurrence % variable.name, line, re.I):
            # # Check the variable is not mentioned in a ".NOT.PRESENT" or in a =PRESENT(var) statement
            # if _check_if_condition(line, variable.name):
            #     continue
            if re.search(RegexPattern.name_occurrence % member.name, line, re.I):
                # Avoid lines in which de var is used to select a case
                if re.search(r"SELECT CASE", line, re.I):
                    continue
                if re.search(r'^\s*if\s*\(', line, re.I):
                    condition = BasicFunctions.close_brackets(line)
                else:
                    condition = ""
                # The variable is found: : return line -1, because it will be inserted at the end of that line
                if where_level > 0:
                    # Inside a where statement, return line before where statement starts
                    return module, indices[0] + where_statement_start, condition
                else:
                    # In a (nested) loop, return the line before loop starts
                    if loop_level > 0:
                        return module, indices[0] + loop_start, condition
                    # On a normal line
                    else:
                        return module, indices[0] + line_index, condition
        # Whenever a 'do loop' starts increment nesting index
        elif re.search(RegexPattern.do_loop, line, re.IGNORECASE):
            if loop_level == 0:
                loop_start = line_index
            loop_level += 1
        # Whenever a 'do loop' ends decrement nesting index
        # This way match bot the expression 'end do' and 'enddo' but excludes matches like 'enddo loop_name'
        elif re.search(RegexPattern.end_do_loop, line, re.IGNORECASE):
            loop_level -= 1
        # Do the same for where statement
        elif line.lower().strip().find("where") == 0:
            if where_level == 0:
                where_statement_start = line_index
            where_level += 1
        elif line.lower().strip().find("end where") == 0:
            where_level -= 1
    # The variable was not found in the subroutine
    return None, None, None


def _check_if_condition(line, var_name):
    condition, line = BasicFunctions.split_if_condition(line)
    if condition:
        arg = CallManager.find_call_arguments(condition)
        for i_arg in arg:
            if re.search(r"\.NOT\.\s*PRESENT\s*\(\s*%s" % var_name, i_arg, re.I):
                return True
    if re.search(r'=\s*PRESENT\s*\(\s*%s\s*\)' % var_name, line, re.I):
        return True
    return False


def _in_which_type_definition(_line, type_def):
    _line = _line.strip().lower()
    _line = MaskCreator.remove_literals(_line)
    _pattern_type = "^ *type[^(].*::(.*)"
    _pattern_type_alt = "^ *type[^(](.*)"
    _pattern_type_end = "^ *end *type"

    # We are changing block
    if type_def is None:
        m = re.match(_pattern_type, _line, re.I)
        if m:
            type_name = m.group(1).strip()
            return type_name
        n = re.match(_pattern_type_alt, _line, re.I)
        if n:
            type_name = n.group(1).strip()
            return type_name
    else:
        m = re.search(_pattern_type_end, _line, re.I)
        if m:
            return None
    return type_def


def split_vars_by_allocatable(variables: list['Variable']):
    """
    Splits the variables into two lists: one with allocatable or pointer variables, and the other
    with the remaining variables.

    Parameters:
        variables (list[Variable]): List of variables to split.

    Returns:
        tuple: Two lists, the first containing allocatable or pointer variables, and the second containing the rest.
    """
    allocatables = [var for var in variables if (var.is_allocatable or var.is_pointer)]
    return allocatables, list(set(variables) - set(allocatables))


def split_by_appearance_in_namelist(variables: list['Variable']):
    """
    Splits the variables into two lists: one with variables that appear in a namelist and the other with those that do not.

    Parameters:
        variables (list[Variable]): List of variables to split.

    Returns:
        tuple: Two lists, the first containing variables in a namelist, and the second containing those not in a namelist.
    """
    in_namelist = [var for var in variables if var.appears_in_namelist]
    not_in_namelist = [var for var in variables if not var.appears_in_namelist]
    return in_namelist, not_in_namelist


def split_vars_by_main(variables: list['Variable'], vault: 'Vault'):
    """
    Splits variables based on whether they are in the 'main' procedure or not, and further categorizes non-main variables by 
    their association with derived types that contain RPE members.

    Parameters:
        variables (list[Variable]): List of variables to split.
        vault (Vault): Object containing the global variables.

    Returns:
        tuple: Three lists, the first containing non-main variables with RPE members, 
               the second containing non-main variables without RPE members, 
               and the third containing variables in the main procedure.
    """
    import AutoRPE.UtilsRPE.Classes.Procedure as Procedure
    # Get all variables not declared global
    not_in_main = [var for var in variables if var.procedure.name != "main"]
    # At this point all variables in main with allocatable or namelist have been excluded
    in_main = [var for var in variables if var.procedure.name == "main"]
    # Get all the structures not declared in main, that has a rpe member
    type_with_rpe_member = list(set([a.is_member_of.lower() for a in not_in_main if a.is_member_of]))
    # Get all the variables, non global, that has such a type
    not_in_main_rpe_member = [var for var in vault.variables if var.type.lower() in type_with_rpe_member
                              and not var.procedure.name == 'main']
    # Remove members from non global variables
    not_in_main = [v for v in not_in_main if not v.is_member_of and
                   v.intent != "in" and
                   not isinstance(v.procedure, Procedure.DerivedType)]

    return not_in_main_rpe_member, not_in_main, in_main
