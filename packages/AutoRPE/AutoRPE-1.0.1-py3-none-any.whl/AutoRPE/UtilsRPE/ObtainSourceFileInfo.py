from typing import List
from tqdm import tqdm
import AutoRPE.UtilsRPE.Classes.Variable as Variable
import AutoRPE.UtilsRPE.Classes.Module as Module
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.Classes.Interface as Interface
import AutoRPE.UtilsRPE.Classes.Procedure as Procedure
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.AttributeParser as AttributeParser
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.Error as Error
from AutoRPE.UtilsRPE.logger import clean_line, logger
import re


def parse_sources(file_list: list, vault: 'Vault', extension: str):
    """
    Parses a list of source files and extracts relevant information into a vault structure.

    This function processes subprograms, variables, derived types, and more from the given source files.
    It identifies subroutines, functions, and module variables, then stores them in the vault.

    Parameters:
        file_list (list): List of source files to be parsed.
        vault (Vault): The database to store extracted information from the code.
        extension (str): The file extension to be used during parsing.

    Returns:
        Vault: The updated vault containing parsed information.
    """
    import functools
    import operator
    # Parsing subprograms and storing info in Module structures.
    print("\n")
    for file in tqdm(file_list, desc="Parsing subprograms and variables"):
        module = Module.Module(file, extension)
        find_subroutines(module, vault)
        find_functions(module, vault)
        find_module_variables(module)
        vault.modules[module.name] = module
        # Add it after the main variables have been found, so as to add them to the variable dictionary as well
        vault.add_block(module.main)

    # Adding info on internal declaration of subroutines
    vault.add_scope_info()

    print("\nParsing Interfaces\n")
    # Parsing the interfaces and storing in Module.
    find_interfaces(vault)

    # Fill vault variable list, excluding interfaces which variables have already been added:
    block_list = vault.get_block_list(exclude_class=['Interface'])
    # Flatten the variable list before extending variables list
    vault.variables.extend(functools.reduce(operator.iconcat, [b.variables for b in block_list], []))

    # Trying to fix the types of real variables with custom types.
    find_undefined_type_parameters(vault)

    print("Parsing derived types\n")
    # Parsing the derived types
    for module in vault.modules.values():
        find_types(module, vault)

    # Fill blocks, and store used modules info
    for module in vault.modules.values():
        module.create_block(vault)
        # Find used module and store
        find_used_modules(module, vault)

    # After having all the used parsed, propagate the inheritance, and add public var to available vars
    print("Add variables and subprograms accessible through use statement\n")
    vault.add_inheritance()

    add_module_subprogram(vault)

    # Add info when a Func or a Sbr is using a use statement
    vault.fill_sbp_variables_dict()

    fill_alloc_info(vault)
    # Store info of derived types in vault procedures
    for dt in vault.derived_types:
        for var in dt.members:
            vault.variables.append(var)

    # Create an has table where variables identified by name + procedure + module
    vault.fill_hash_table()

    # Add to variables info about their belongings in namelist, to be used when inserting the %sbits info
    for module in vault.modules.values():
        find_namelist_variable(module, vault)

    # Now that vault.derived_types is full add extension to derived types if any
    vault.expand_derived_types()

    # Store the external used data types
    vault.store_external_data_structures()

    # Stores list of function/subroutines called on each lines, stores external procedures, add level info
    fill_line_info_call(vault)

    # Check that all external procedure are not just internal mispelled procedure
    check_external_function(vault)
    # Fill var info on used in external
    for list_of_call in vault.dictionary_of_calls.values():
        if list_of_call[0].subprogram.is_external:
            for call in list_of_call:
                for arg in call.arguments:
                    variable = arg.variable
                    if variable is not None:
                        variable.is_used_in_external = call.name

    # Passing to pointed objects the actual function/subroutine they points to
    process_pointers(vault)
    n_func = len(vault.block_dictionary['Function'])
    n_sbr = len(vault.block_dictionary['SubRoutine'].values())
    n_interfaces = len(vault.block_dictionary['Interface'].values())
    print("number of functions " + str(n_func) + "\n" +
          "number or subroutines " + str(n_sbr) + "\n" +
          "number or interfaces " + str(n_interfaces) + "\n" +
          "number or modules " + str(len(vault.modules)) + "\n" +
          "number of variables " + str(len(vault.variables)) + "\n" +
          "number or derived_types " + str(len(vault.derived_types)) + "\n")

    return vault


def add_module_subprogram(vault: 'Vault'):
    """
    Adds subprograms and associated information to each module in the vault.

    This function assigns subprograms (functions, subroutines, interfaces) to each module and
    stores information about accessible and indirectly accessible subprograms.

    Parameters:
        vault (Vault): The database containing modules and related information.
    """
    block_list = vault.get_block_list(only_class=['Function', 'SubRoutine', 'Interface'])
    for module in vault.modules.values():
        module.subprogram = [b for b in block_list if b.module == module]
        module.accessible_sbp = [b for b in block_list if b.module in module.accessible_mod]
        module.indirect_accessible_sbp = [b for b in block_list if b.module in module.indirect_accessible_mod]


def get_dummy_arguments(module: Module, index: int):
    """
    Retrieves the subroutine name and its dummy arguments from a specific line in the module.

    Given the line number in the module, this function extracts the subroutine name and any associated
    dummy arguments, handling special cases like function declarations with kind attributes.

    Parameters:
        module (Module): The module containing the source code.
        index (int): The line number to examine in the module.

    Returns:
        tuple: A tuple where the first element is the subroutine name (str) and the second element is
               a list of dummy arguments (list of str).
    """
    # Definition: Given a line number, returns the subroutine name and the dummy arguments (in case they exist)
    # Input: integer with line number
    # Output: tuple with routine name and list of dummy arguments
    line = module.lines[index]
    # Workaround to solve the problem that appears when there's a function declaration with (kind=...)
    if line.lower().count("function "):
        if line.find("(") < line.lower().find("function "):
            line = line[line.lower().find("function "):]

    # If the subroutine declaration does not have any parenthesis, this routine does not have any argument
    if not line.count("("):
        name = line.split()[1].strip()
        dummy_arguments = []
    # If otherwise it has dummy arguments, find them
    elif line.lower().count("result") or line.lower().count("bind("):
        name = line[:line.find("(")].split()[-1]
        dummy_arguments = []
        dummy_arguments += CallManager.find_call_arguments(BasicFunctions.close_brackets(line))
    else:
        name = line[:line.find("(")].split()[-1]
        dummy_arguments = CallManager.find_call_arguments(line)
    dummy_arguments = [x for x in dummy_arguments if x.strip()]
    return name, dummy_arguments


def find_subprogram_declaration(module: Module, _subprogram_start: int, _subprogram_end: int,
                                obj_to_find: str=RegexPattern.variable_declaration):
    """
    Finds and returns a list of variable declarations within a subprogram, given its start and end lines.

    Parameters:
        module (Module): The module containing the subprogram's source code.
        _subprogram_start (int): The starting line number of the subprogram.
        _subprogram_end (int): The ending line number of the subprogram.
        obj_to_find (Pattern): A regular expression pattern for identifying variable declarations..

    Returns:
        list: A list of strings containing variable declarations within the subprogram.
    """
    # Definition: Given the line numbers where a routine starts and ends,
    # return list of strings containing declarations
    # TODO: manage cases in which a routine contains other functions declarations.

    stop_index = [index
                  for index, line in enumerate(module.lines[_subprogram_start:_subprogram_end + 1])
                  if re.search(RegexPattern.name_occurrence % 'contains', line, re.I)
                  or re.search(RegexPattern.name_occurrence % 'interface', line, re.I)]
    # A declaration found stop the search there
    if stop_index:
        _subprogram_end = _subprogram_start - 1 + stop_index[0]

    # Lines inside the routine
    _subprogram_lines = module.lines[_subprogram_start:_subprogram_end + 1]

    # Lines that are variable declarations
    _all_declaration = [_l.strip() for _l in _subprogram_lines if
                        re.search(obj_to_find, _l, re.I) and not
                        (re.search(RegexPattern.general_allocation, _l, re.I) or
                         re.search(RegexPattern.string_array_initialization, _l, re.I))]

    return _all_declaration


def add_struct_members(file, structure):
    """
    Adds members of a structure to the main routine of the file. Given a structure, this method
    finds its members and adds them as variables to the 'main' routine of the provided file, if available.

    Parameters:
        file (File): The file object containing the structure and routines.
        structure (Structure): The structure object containing variables to be added to the main routine.

    Returns:
        None

    Raises:
        UnboundLocalError: If the 'main' routine is not found in the file.
    """
    # Definition: Given the routine name, the name of the dummy arguments and the lines containing declarations,
    # this method finds the attributes of each dummy arguments and adds all the information
    # into the object variable "routines".
    # Input:
    #       -routine_name: string with the routine name
    #       -dummy_arguments: list of strings with argument names
    #       -declarations: list of strings with variable declarations
    try:
        for obj in file.objects:
            if obj.name == "main":
                main = obj
                break
        for member in structure.variables:
            main.add_variable(member)

    except UnboundLocalError:
        print("Main not found for structure %s", structure.name)


def create_subprogram(module, header, routine_name, dummy_arguments, var_declarations, used_modules,
                      subprogram_type):
    """
    Creates a subprogram (function or subroutine) with its associated variables and attributes.

    This function creates a subprogram object (function or subroutine) by processing its header, dummy arguments,
    variable declarations, and used modules. It determines the return value for functions and assigns appropriate
    attributes to the variables, including type, dimension, intent, and optional status.

    Parameters:
        module (Module): The module containing the subprogram.
        header (str): The header string of the subprogram.
        routine_name (str): The name of the subprogram.
        dummy_arguments (list): A list of dummy arguments for the subprogram.
        var_declarations (list): A list of variable declarations within the subprogram.
        used_modules (list): A list of modules used by the subprogram.
        subprogram_type (Subprogram): The type of the subprogram (Function or SubRoutine).

    Returns:
        Subprogram: The created subprogram object with associated variables and attributes.

    Raises:
        ValueError: If the subprogram type is not recognized (i.e., not a Function or SubRoutine).
    """
    if subprogram_type == Subprogram.Function:
        # Retrieve the ret_val name
        ret_type, ret_val = find_function_type_from_header(header, var_declarations)
        if not ret_val:
            ret_val = routine_name
    elif subprogram_type == Subprogram.SubRoutine:
        ret_val = None
    else:
        raise ValueError("Header does not correspond to function or routine")

    subprogram = subprogram_type(routine_name, module)

    if len(used_modules):
        subprogram.use_only_variables = [m.lower().split("use")[1].strip() for m in used_modules]
    # Reverse approach
    dummy_arguments = [x for x in dummy_arguments]
    # Create a lowercase set
    dummy_arguments_lowercase_set = {arg.lower() for arg in dummy_arguments}

    for declaration in var_declarations:
        m = re.search(RegexPattern.variable_declaration, declaration)
        # In this case is not a variable declaration
        if declaration.count("contiguous"):
            continue
        _attributes, variable = m.groups()
        # Check if the dummy argument is inside the declaration arguments
        # If it is, take the type, dimension, intent and optional
        _var_type, _dimension, _intent, _optional, \
        _allocatable, is_pointer, is_parameter = AttributeParser.parse_attributes(_attributes, variable)

        variable_name = AttributeParser.get_variable_name(variable)

        _v = Variable.Variable(subprogram, variable_name, _var_type, _dimension, module, declaration)
        _v.is_allocatable = _allocatable
        _v.is_parameter = is_parameter

        # If the variable name is the same of the function or is return statement
        if ret_val is not None and _v.name.lower() == ret_val.lower():
            _v.is_retval = True
            subprogram.return_value = _v
            subprogram.type = _v.type
        _v.is_pointer = is_pointer
        
        # Check if the variable is a dummy argument in a case insensitive way.
        if variable_name.lower() in dummy_arguments_lowercase_set:
            _v.intent = _intent
            _v.is_optional = _optional
            _v.is_dummy_argument = True
            subprogram.dummy_arguments.append(_v)
        subprogram.add_variable(_v)

    # Save the position of the argument
    found_vars = [variable.name for variable in subprogram.variables]

    # Add position to dummy arguments
    for index, dummy_argument in enumerate(dummy_arguments):
        # Check that the dummy are all correctly spelled, otherwise match the proper variable in a case insensitive way.
        if dummy_argument not in found_vars:
            try:
                dummy_argument = handle_misspelled_variable(dummy_argument, found_vars)
            except Error.VariableNotFound:
                raise Error.VariableNotFound(f"The variable {dummy_argument} is misspelled in subprogram {routine_name} declaration in module {module.name} ")
        dummy_argument = subprogram.get_variable_by_name(dummy_argument)
        dummy_argument.position = index
        if not dummy_argument.is_optional:
            subprogram.mandatory_da.append(dummy_argument)
        for m_i, m_da in enumerate(subprogram.mandatory_da):
            m_da.mandatory_position = m_i
    # Order dummy_arguments by position
    subprogram.dummy_arguments.sort(key=lambda x: x.position)
    if subprogram_type == Subprogram.Function:
        # In case of function  declaration like INTEGER FUNCTION name() without return variable declaration
        if not [var for var in subprogram.variables if var.is_retval]:
            # Add the return value to functions variables
            _v = Variable.Variable(subprogram, ret_val, ret_type, 0, module)
            subprogram.add_variable(_v)
            _v.is_retval = True
            # Specify the type of the function
            subprogram.type = ret_type
            subprogram.return_value = _v
    # Save object
    return subprogram


def find_subroutines(module, vault):
    """
    Finds subroutine declarations within a module, extracts their attributes, and stores them in the vault.

    This function scans the module's source code for subroutine declarations, identifies their names, dummy arguments,
    variable declarations, and used modules. It creates subroutine objects with appropriate attributes and adds them
    to the vault. It also identifies any internal subroutines declared within the subroutine's scope.

    Parameters:
        module (Module): The module containing the source code to scan for subroutine declarations.
        vault (Vault): The vault object where subroutines and their associated information are stored.

    Returns:
        None

    Raises:
        Error.SubprogramNotFound: If the corresponding `end subroutine` statement for a subroutine cannot be found.
    """
    #  Looks into the sourcefile for routine declarations, storing
    #  name, type, dimensions and optionality of the arguments.

    for _index, line in enumerate(module.lines):
        # Look if routine starts with (recursive) subroutine
        sbr_name = re.search(RegexPattern.subroutine_declaration, line, re.IGNORECASE)
        if sbr_name:
            sbr_name = sbr_name.group(1)
            subroutine_start = _index
            # Look for end subroutine statements
            try:
                subroutine_end = [index for index, l in enumerate(module.lines)
                                  if re.search(r'end\s+subroutine\s+%s\b' % sbr_name, l, re.I)][0]
            except IndexError:    
                try:
                    message = f"The subprogram 'end subroutine {sbr_name}' statement from the module '{module.name}' doesn't have the subroutine name."
                    logger.warn(message)
                    # Trying to find the corresponding end_subroutine
                    subroutine_end = [index + subroutine_start for index, l in enumerate(module.lines[subroutine_start:])
                    if re.search(r'\bend\s+subroutine\s*$', l, re.I)][0]
                except IndexError as err:
                    raise Error.SubprogramNotFound(
                        'The subprogram "end subroutine {subname}" statement from the module "{module}" has not been found.'.format(
                            subname=sbr_name, module=module.name))

            # Find name and dummy arguments
            subroutine_name, dummy_arguments = get_dummy_arguments(module, _index)
            # Find declarations
            var_declarations = find_subprogram_declaration(module, subroutine_start, subroutine_end,
                                                           obj_to_find=RegexPattern.variable_declaration)
            used_modules = find_subprogram_declaration(module, subroutine_start, subroutine_end,
                                                       obj_to_find=RegexPattern.use_statement)
            header = module.lines[subroutine_start]
            # Create subroutine objects, with variables and their attribute. Then add it to the module
            subroutine = create_subprogram(module, header, subroutine_name, dummy_arguments, var_declarations,
                                           used_modules, subprogram_type=Subprogram.SubRoutine)
            # Check if subroutines are defined inside this scope
            subroutine_lines = module.lines[subroutine_start + 1:subroutine_end - 1]
            internal_subprogram = [re.search(RegexPattern.subprogram_declaration, l, re.I) for l in subroutine_lines
                                   if re.search(RegexPattern.subprogram_declaration, l, re.I)]
            if internal_subprogram:
                subprogram_names = [i_s.group(2) for i_s in internal_subprogram]
                subroutine.declares = subprogram_names

            vault.add_block(subroutine)


def add_external_subprogram(unknown_calls, vault: 'Vault'):
    """
    Adds external subprogram calls to the vault, marking variables used in external subprograms.

    This function stores external subprogram calls in the vault's block dictionary and marks variables used in
    these calls as involved in external subprograms.

    Parameters:
        unknown_calls (UnknownCalls): The object containing subprogram calls that are not yet recognized.
        vault (Vault): The vault object where subprogram call information and associated variables are stored.

    Returns:
        None
    """
    for subprogram_call in unknown_calls.args[0]:
        # Stores the external call in the database
        sbp_type = type(subprogram_call.subprogram).__name__
        vault.block_dictionary[sbp_type][subprogram_call.subprogram.name] = [subprogram_call.subprogram]
        for arg in subprogram_call.arguments:
            if arg.variable is not None:
                # When producing the final list of variable we will have to exclude these variables
                arg.variable.is_used_in_external = subprogram_call.name


def fill_line_info_call(vault: 'Vault'):
    """
    Populates the line information in the vault by processing function and subroutine calls in each module's line info.

    Iterates through each module and its line information, identifying function and subroutine calls. If a call
    corresponds to an unknown subprogram, it adds the external subprogram to the vault. The information is stored
    in the vault's dictionary of calls, with the key being the subprogram's name (or module name for non-external calls).

    Parameters:
        vault (Vault): The vault object containing the modules and their associated data.

    Returns:
        None
    """
    for module in tqdm(vault.modules.values(), desc="Fill info line module"):
        for line_info in module.line_info:
            # Remove if condition
            line = line_info.unconditional_line
            if_condition = line_info.if_condition
            block = line_info.block
            for line_part in line, if_condition:
                # Otherwise all function call ends up duplicated
                if not line_part.strip():
                    continue
                # Search for functions
                try:
                    called_functions = CallManager.get_function(line_part, block, vault)
                except Error.ProcedureNotFound as unknown_subroutines_calls:
                    # If unknown function was found add it to vault
                    add_external_subprogram(unknown_subroutines_calls, vault)
                    called_functions = CallManager.get_function(line_part, block, vault)
                # Search for subroutines call ( after function, unknown function could be used as sbr argument)
                try:
                    called_subroutines = CallManager.get_subroutine(line_part, block, vault)
                except Error.ProcedureNotFound as unknown_subroutines_calls:
                    # If unknown subroutine was found add it to vault
                    add_external_subprogram(unknown_subroutines_calls, vault)
                    called_subroutines = CallManager.get_subroutine(line_part, block, vault)
                # Add the information to line info and fill vault dictionary of calls
                subprogram_call = called_functions + called_subroutines
                for i_s_call, s_call in enumerate(subprogram_call):
                    # Name will be subprogram name + module name, to avoid confusion among subprograms with same name
                    if not s_call.subprogram.is_external:
                        name = s_call.subprogram.module.name + "_mp_" + s_call.subprogram.name
                    else:
                        name = s_call.subprogram.name
                    s_call.line_info = line_info
                    # Store the index of the call wrt the total number of this function's call on the line
                    s_call.index = len([c for c in subprogram_call[:i_s_call] if c.name == s_call.name])
                    vault.dictionary_of_calls[name].append(s_call)

    print("\n")


def check_external_function(vault: 'Vault'):
    """
    Verifies that external subprograms are not mistakenly identified as internal due to misspelling,
    ensuring that variables used in external functions are properly analyzed.

    Parameters:
        vault (Vault): The vault object containing information about subprograms and interfaces.

    Returns:
        None
    """
    list_interface = [p[0].name.lower() for p in vault.block_dictionary['Interface'].values()]
    for procedure_type in ['SubRoutine', 'Function']:
        list_external = [p[0].name.lower() for p in vault.block_dictionary[procedure_type].values() if p[0].is_external]
        list_internal = [p[0].name.lower() for p in vault.block_dictionary[procedure_type].values()
                         if not p[0].is_external] + list_interface
        common = [le for le in list_external if le in list_internal]
        if common:
            message = f"{procedure_type} {common[0]} has been misspelled"
            clean_line()
            logger.warn(message)
            # raise Error.ExceptionNotManaged(message)

# def _fill_subprogram_level(vault):
#     # Recursive function to compute the level of the function in the pipeline
#     def compute_procedure_level(p, v):
#         # If the subprogram is not calling any function its level is 0
#         if not p.internal_call:
#             p.level = 0
#             return 0
#         # If there are internal calls, compute the pipeline level
#         set_depth = [-1]*len(p.internal_call)
#         for i, p_name in enumerate(p.internal_call):
#             internal_procedure = v.procedures_dictionary[p_name][0]
#             # The level of the internal call has already been computed
#             if internal_procedure.level != -1:
#                 set_depth[i] = internal_procedure.level
#             else:
#                 # We hit a recursive functions
#                 if p.name in internal_procedure.internal_call:
#                     internal_procedure.level = 1
#                 else:
#                     # Recursively compute the internal function level
#                     internal_procedure.level = compute_procedure_level(internal_procedure, v)
#                 set_depth[i] = internal_procedure.level
#         # Return the biggest among the level. the +1 accounts for this function extra-layer
#         return max(set_depth) + 1
#
#     # Store subprograms called by each subprogram
#     for call in vault.dictionary_of_calls.values():
#         # Using the dictionary of calls, we look where the call happened
#         for c in call:
#             # Retrieve the object describing the scope
#             scope = vault.procedures_dictionary[c.block.name]
#             # To avoid this we should store block name with subprogram_name_mp_module_name
#             if len(scope) != 1:
#                 Error.ExceptionNotManaged("One function expected, got two")
#             # Retrieve the actual name, in case it was a call to an interface
#             name = c.subprogram.name
#             # Check the call uses dummy arguments of real type (we do not care if the calls are not entangled)
#             used_da = [da for da in scope[0].dummy_arguments if da.type in VariablePrecision.real_id if
#                        da in [a.variable for a in c.arguments]]
#             if name not in scope[0].internal_call and used_da:
#                 scope[0].internal_call.extend([name])
#
#     # For each function in the dictionary, compute the "level" in the pipeline
#     for procedure_name in vault.procedures_dictionary:
#         if procedure_name == 'main':
#             continue
#         procedure = vault.procedures_dictionary[procedure_name][0]
#         if isinstance(procedure, Subprogram.SubRoutine) or isinstance(procedure, Subprogram.Function):
#             if procedure.level == -1:
#                 procedure.level = compute_procedure_level(procedure, vault)


def find_types(module: Module, vault: 'Vault'):
    """
    Scans the module for type declarations and extracts information about derived types and their members.

    This function looks for type declarations, including any type extensions, and parses the variables
    associated with each type. It then adds the derived types and their variables to the vault.

    Parameters:
        module (Module): The module containing lines of code to be analyzed for type declarations.
        vault (Vault): The database where derived types and their variables are stored.

    Returns:
        None
    """
    # Looks into the module lines for type declaration
    in_type_declaration = False
    derived_types = []
    type_name = None
    variable_counter = None
    for _index, line in enumerate(module.lines):
        # Look if routine starts with subroutine
        if not in_type_declaration:
            # Check if a type has been declared
            m = re.search(RegexPattern.type_declaration, line, re.I)
            if m:
                in_type_declaration = True
                variable_counter = 0
                type_name = m.group(3)
                extended_type = None
                # Case in which a type is extending another type, search the extended type name
                extend_statement = re.search(RegexPattern.name_occurrence % "extends", line, re.I)
                if extend_statement:
                    extend_statement = BasicFunctions.close_brackets(line[extend_statement.start():])
                    extended_type = CallManager.find_call_arguments(extend_statement)[0]
                # Create the structure
                derived_type = Procedure.DerivedType(type_name, module, extended_type)
                derived_types.append(derived_type)
        else:
            # Check if we are exiting a type declaration
            m = re.search(RegexPattern.end_type_statement, line, re.IGNORECASE)
            if m:
                in_type_declaration = False
            else:
                m = re.search(RegexPattern.variable_declaration, line)
                if m:
                    attributes, variables = m.groups()
                    var_type, dimension, intent, optional, \
                    allocatable, is_pointer, is_parameter = AttributeParser.parse_attributes(attributes, variables)

                    variable_name = AttributeParser.get_variable_name(variables)

                    v = Variable.Variable(derived_type, variable_name, var_type, dimension, module, _declaration=line)
                    v.position = variable_counter
                    v.is_dummy_argument = True
                    v.is_allocatable = allocatable
                    v.is_parameter = is_parameter
                    v.is_pointer = is_pointer
                    v.is_member_of = type_name
                    derived_type.add_member(v)
                    variable_counter += 1
    # Now that also the variables have been added to data structure we can fill the dictionary
    for dt in derived_types:
        vault.derived_types.append(dt)
        vault.add_block(dt)


def find_module_variables(module: Module):
    """
    Extracts and processes variable declarations from a module, excluding variables within type and function
    declaration zones.

    Parameters:
        module (Module): The module to analyze for variable declarations.

    Returns:
        None
    """
    line_to_check = True

    for line in module.lines:
        if line_to_check:
            # Check if we are entering a type declaration zone
            is_type_declaration = re.search(RegexPattern.type_declaration, line, re.IGNORECASE)
            if is_type_declaration or NatureDeterminer.is_function_declaration_statement(line):
                line_to_check = False
                continue
        else:
            # Check if we are exiting a type declaration zone
            is_end_type_declaration = re.search(RegexPattern.end_type_statement, line, re.IGNORECASE)
            if is_end_type_declaration or NatureDeterminer.is_end_function_statement(line):
                line_to_check = True
            # Even if we are inside or exiting a type declaration zone, we have to jump to next line
            continue

        if line.lower().count("contains"):
            break
        if line.lower().count("end program"):
            break
        match = re.search(RegexPattern.variable_declaration, line)
        if match:
            attributes, variables = match.groups()
            var_type, dimension, intent, optional, \
            allocatable, is_pointer, is_parameter = AttributeParser.parse_attributes(attributes, variables)
            variable_name = AttributeParser.get_variable_name(variables)
            # It means is a variable and not a public subprogram
            if var_type:
                v = Variable.Variable(module.main, variable_name, var_type, dimension, module, _declaration=line)
                v.is_allocatable = allocatable
                v.is_pointer = is_pointer
                v.is_parameter = is_parameter
                module.main.add_variable(v)
                module.main.add_accessible_var(v)
                module.variables.append(v)


def find_namelist_variable(module: Module, vault: 'Vault'):
    """
    Identifies variables in a namelist declaration, associates them with the module and namelist, and
    updates their metadata.

    Parameters:
        module (Module): The module containing the namelist declarations.
        vault (Vault): The database storing variables and their associated metadata.

    Returns:
        None
    """
    if module.get_text().lower().count('namelist'):
        for index, line in enumerate(module.lines):
            if line.lower().strip().find("namelist") == 0:
                # Retrieve all variables in the namelist and set the module and name of the namelist
                namelist_variables = [var.strip() for var in line.split("/")[2].split(",")]
                namelist_name = re.search(r'namelist\s*/(.*)/', line, re.I).group(1)
                for nv in namelist_variables:
                    var = vault.get_variable_by_name(nv, module.line_info[index].block)
                    var.appears_in_namelist = [module.module_name, namelist_name]


def find_functions(module: Module, vault: 'Vault'):
    """
    Extracts function declarations from a module, including their names, arguments, and attributes, and stores
    them in the vault.

    Parameters:
        module (Module): The module containing the function declarations.
        vault (Vault): The vault object where function metadata is stored.

    Returns:
        None
    """
    # Definition: Looks into the sourcefile for routine declarations, storing the name, type,
    # dimensions and optionality of the arguments.
    for _index, line in enumerate(module.lines):
        if NatureDeterminer.is_function_declaration_statement(line):
            function_start = _index
            # Look for end subroutine statements
            function_end = BasicFunctions.find_next_end(module.lines, _index, "end function")

            # Find name and dummy arguments
            function_name, dummy_arguments = get_dummy_arguments(module, _index)
            # Find declarations
            variables_declarations = find_subprogram_declaration(module, function_start, function_end, obj_to_find="::")
            used_modules = find_subprogram_declaration(module, function_start, function_end, obj_to_find=r"^use\s")
            # Parse everything and store
            header = module.lines[function_start]
            function = create_subprogram(module, header, function_name, dummy_arguments, variables_declarations,
                                         used_modules, subprogram_type=Subprogram.Function)
            vault.add_block(function)


def find_interfaces(vault: 'Vault'):
    """
    Extracts interface declarations from all modules in the vault, identifies their associated procedures,
    and stores them as interface objects.

    Parameters:
        vault (Vault): The vault containing modules and their metadata.

    Returns:
        None
    """
    for module in vault.modules.values():
        # Definition: Looks into the sourcefile for interface declarations, storing the name.
        for _index, _line in enumerate(module.lines):
            if _line.strip().lower().find("interface") == 0 or _line.strip().lower().find("abstract interface") == 0:
                interface_start = _index
                interface_end = BasicFunctions.find_next_end(module.lines, _index, "end interface")
                try:
                    # Check if it is abstract or not
                    if _line.strip().lower().find("abstract interface") == 0:
                        interface_name = None
                        is_abstract = True
                    else:
                        interface_name = _line.split()[1].strip()
                        is_abstract = False
                except IndexError:
                    # interface to an external procedure or a procedure used in a procedure with the DEFERRED attribute
                    continue
                interfaced_procedure = []
                for interface_line in module.lines[interface_start:interface_end + 1]:
                    # if interface_line.strip().lower().startswith("module procedure") == 0:
                    if interface_line.strip().lower().startswith("module procedure"):
                        line_procedure = interface_line.replace("module procedure", "")
                        line_procedure = line_procedure.replace("MODULE PROCEDURE", "")
                        line_procedure = [_r.strip() for _r in line_procedure.split(",")]
                        interfaced_procedure += line_procedure
                    elif interface_line.strip().lower().startswith("procedure"):
                        line_procedure = interface_line.replace("procedure", "")
                        line_procedure = line_procedure.replace("PROCEDURE", "")
                        line_procedure = [_r.strip() for _r in line_procedure.split(",")]
                        interfaced_procedure += line_procedure
                    elif interface_line.strip().lower().strip().find("subroutine") == 0 \
                            or interface_line.strip().lower().strip().find("function") == 0:
                        subroutine_name = interface_line[:interface_line.find("(")].split()[1]
                        interfaced_procedure += [subroutine_name]

                # Create a name for the abstract interface based on the procedures names
                if interface_name is None:
                    interface_name = "abstract_interface_" + "_".join(interfaced_procedure).replace(" ", "_")

                interface = Interface.Interface(interface_name, module, is_abstract)
                for ip in interfaced_procedure:
                    interface.add_module_procedure(vault.get_subprogram_by_name(ip, ['Function', 'SubRoutine']))
                interface.generate_key()
                # Don't add variables, since they have already been added from module procedures
                vault.add_block(interface, add_var=False)
                vault.interfaces_dictionary[interface.name] = interface

    # Once the dictionary of interface is full, add the interface property "has mixed interface"
    for interface in vault.interfaces_dictionary.values():
        for subprograms in interface.agnostic_key['all'].values():
            # More than one subprogram correspond to the same agnostic key: is a sp/dp interface
            if len(subprograms) > 1:
                for s in subprograms:
                    s = interface.get_module_procedure(s)
                    s.has_mixed_interface = True


def find_used_modules(module: Module, vault: 'Vault'):
    """
    Parses the 'use' statements in a module to identify dependencies and imports variables or subprograms into the module.

    Parameters:
        module (Module): The module to analyze.
        vault (Vault): The vault containing all module definitions and metadata.

    Returns:
        None
    """
    for index, line in enumerate(module.lines):
        line = line.strip().lower()
        # First line will be the module name, skip it
        if line.lower().find("module ") == 0 or line.lower().find("program ") == 0:
            continue
        # No need to parse the entire file
        if not line.find("use ") == 0:
            break

        module_name = line.split()[1]

        use_only = []
        if line.count(","):
            use_only = line.split(":")[1].lower().replace("only", "")
            use_only = use_only.lower().replace(":", "").strip()
            use_only = [u.strip() for u in use_only.split(",")]
        if module_name.count(","):
            # Remove the "only" information
            module_name = module_name.split(",")[0].strip()

        # Add to the module the used modules
        try:
            used_module = vault.modules[module_name]
        except KeyError:
            # It was an external import
            continue

        # Sometimes use statement are repeated
        if used_module not in module.accessible_mod:
            if use_only:
                for var in use_only:
                    try:
                        var = vault.modules[module_name].get_variable(var, 'main')
                    except Error.VariableNotFound:
                        # It means a subprogram has been imported
                        continue
                    module.use_only.append(var)
            else:
                module.accessible_mod.append(used_module)


def fill_alloc_info(vault: 'Vault'):
    """
    Identifies allocation and deallocation of allocatable variables and updates their metadata.

    Parameters:
        vault (Vault): The vault containing all modules, variables, and metadata.

    Returns:
        list: A list of allocatable variables with their type, dimensions, name, allocation block, and module.
    """

    def find_mem_statement(var, l_i, pattern):
        # Remove conditional part, where variables can't be allocated
        line = l_i.unconditional_line
        if re.search(pattern % var.name, line, re.I):
            # Check that we did not match a member with the same name: a_i will also match %a_i
            if not re.search(RegexPattern.allocation_member_name % var.name, line.replace(" ", ""), re.I):
                return True
        return False

    alloc_list = [v for v in vault.variables if v.is_allocatable]
    for alloc_var in alloc_list:
        f_a = False
        f_da = False
        if alloc_var.is_global:
            line_info = []
            for m in [alloc_var.module] + alloc_var.procedure.module.used_by:
                line_info.extend(m.line_info)
            # Variables can be allocated just inside subprograms
            line_info = [li for li in line_info if li.block.name == 'main']
        else:
            module = alloc_var.module
            procedure = alloc_var.procedure.name
            line_info = [li for li in module.line_info if li.block.name == procedure]

        # Search in all possible lines
        for l_info in line_info:
            if not f_a:
                if find_mem_statement(alloc_var, l_info, pattern=RegexPattern.allocation_variable_name):
                    f_a = True
                    alloc_var.allocate_info.line_info = l_info
            if not f_da:
                if find_mem_statement(alloc_var, l_info, pattern=RegexPattern.deallocation_variable_name):
                    f_da = True
                    alloc_var.allocate_info.is_deallocated = True
            if f_a and f_da:
                break
    return [[v.type, v.dimension, v.name, v.allocate_info.line_info.block.name, v.module.name] for v in vault.variables
            if
            v.is_allocatable and v.allocate_info.line_info is not None and not v.allocate_info.is_deallocated]


def find_function_type_from_header(header: str, var_declaration: list[str]):
    """
    Extracts the return type and name of a function from its header and variable declarations.

    Parameters:
        header (str): The function declaration line.
        var_declaration (list): A list of variable declarations within the function.

    Returns:
        tuple: A pair containing the function's return type and name.
    """

    # Get the function name
    fun_name = header.lower().split('function')[1]
    fun_name = fun_name.split("(")[0]
    fun_name = fun_name.replace("(", "")
    fun_name = fun_name.strip()

    # Check if a return val is declared
    if header.lower().count("result"):
        ret_val = header.lower().split('result')[1]
        ret_val = ret_val.replace('results', '')
        ret_val = ret_val.replace('(', '')
        ret_val = ret_val.replace(')', '').strip()
    else:
        ret_val = fun_name

    # Check if the return_val typ is specified among the function variables
    declaration_of_retval = [v.split("::")[1].lower().strip() for v in var_declaration
                             if v.split("::")[1].lower().strip() in [fun_name, ret_val]]
    if declaration_of_retval:
        return None, declaration_of_retval[0]
    # The type is specified in front of the function
    pattern = "(.*)function"
    match = re.search(pattern, header.strip(), re.IGNORECASE)
    fun_type = remove_brackets_content(match.groups(0)[0].strip().lower())
    if fun_type == "real":
        real_declaration = match.group(1)
        nt = re.match(RegexPattern.precision_of_real_declaration, real_declaration, re.I)
        if nt is not None:
            try:
                fun_type = VariablePrecision.lookup_table[nt.group(3)]
            except KeyError:
                raise Error.ExceptionNotManaged("Pleas add this type specifier into VariablePrecision.lookup_table: %s"
                                                % nt.group(3))
        else:
            print("Type specifier not found in real function " + header + " declaration")
            return VariablePrecision.real_id['wp']
    if match.group(0).count('rpe_var'):
        return 'rpe_var', fun_name
    else:
        return fun_type, fun_name


def remove_brackets_content(string: str):
    """
    Removes the content inside parentheses, including the parentheses themselves.

    Parameters:
        string (str): The input string.

    Returns:
        str: The string with parentheses and their content removed.
    """
    op = [i for i, x in enumerate(string) if x == "("]
    cp = [i for i, x in enumerate(string) if x == ")"]
    _new_line = []
    for n in range(len(string)):
        # If comma index n is outside parenthesis (number of openings equal number of closings) substitute
        if len([x for x in op if x <= n]) == len([x for x in cp if x < n]):
            _new_line += [string[n]]
    return "".join(_new_line)


def process_pointers(vault: 'Vault'):
    """
    Processes pointer variables in the vault, resolving their types and ensuring there are no duplicates.

    Parameters:
        vault (Vault): The vault containing the variables and types to process.

    Returns:
        None
    """
    for var in vault.variables:
        if var.is_pointer:
            if var.is_pointer.count("type"):
                pointer_name = var.is_pointer.replace("type", "")
                pointer_name = BasicFunctions.remove_outer_brackets(pointer_name)
                search_array = vault.derived_types
            elif var.is_pointer.count("class"):
                # Same of type, but for compiler reason they have to be declared as classes
                pointer_name = var.is_pointer.replace("class", "")
                pointer_name = BasicFunctions.remove_outer_brackets(pointer_name)
                search_array = vault.derived_types
            elif var.type == "procedure":
                pointer_name = var.is_pointer
                search_array = []
                for val in vault.procedures_dictionary.values():
                    search_array += val
            else:
                # It is a pointer to real or a pointer to integer
                continue
            pointed_obj = [obj for obj in search_array if obj.name == pointer_name]
            if len(pointed_obj) > 1:
                raise Error.DuplicatedObject
            else:
                var.is_pointer = pointed_obj
            continue


def handle_misspelled_variable(dummy_argument: str, variables: List[str]):
    """
    Checks if a dummy argument is in the variables list, case insensitively.

    Parameters:
        dummy_argument (str): The dummy argument to check.
        variables (List[str]): The list of variables to search.

    Returns:
        str: The matching variable if found.

    Raises:
        Error.VariableNotFound: If no matching variable is found.
    """
    for variable in variables:
        if dummy_argument.lower() == variable.lower():
            return variable
    raise Error.VariableNotFound(f"The variable {dummy_argument} is misspelled.")



def find_undefined_type_parameters(vault: 'Vault'):
    """
    Finds and assigns types to undefined kind parameters used in the code, based on the declaration.

    Parameters:
        vault: The vault containing variables and their metadata.

    Returns:
        None

    Raises:
        NotImplementedError: If multiple potential types are found for the same kind parameter.
    """

    import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
    lookup_table = VariablePrecision.lookup_table
    variables = vault.variables
    for key, value in lookup_table.items():
        if isinstance(value, VariablePrecision.UndefinedPrecision):
            potential_canditates = [v for v in variables if v.name == value.name]
            potential_types = [get_type_from_declaration(v.declaration) for v in potential_canditates if v.declaration]
            if len(set(potential_types)) == 1:
                new_type = potential_types[0]
                VariablePrecision.lookup_table[key] = new_type
                for variable in variables:
                    if isinstance (variable.type, VariablePrecision.UndefinedPrecision):
                        if variable.type.name == value.name:
                            variable.type = new_type
            else:
                raise NotImplementedError("More than one potential type found? Please report since it neved happened with our tested codes.")


def get_type_from_declaration(declaration: str) -> str:
    """
    Extracts and deduces the type from a variable declaration.

    Parameters:
        declaration (str): The variable declaration, e.g., 'real :: var = kind_parameter'

    Returns:
        str: The deduced type based on the declaration.
    """
    type_definition = declaration.split("=")[1].strip()
    return deduce_precision(type_definition)


def deduce_precision(fortran_kind: str) -> str:
    """
    Determines if the Fortran kind specifier corresponds to single or double precision.
    
    Parameters:
        fortran_kind (str): The Fortran kind specification as a string (e.g., 'kind ( 1.0D+00 )').
    
    Returns:
        str: 'single' if the specifier corresponds to single precision,
             'double' if it corresponds to double precision.
    
    Raises:
        ValueError: If the input string does not contain a valid precision specifier.
    """
    # Normalize and extract the kind argument
    fortran_kind = fortran_kind.strip().lower()
    
    if "kind" in fortran_kind and "(" in fortran_kind and ")" in fortran_kind:
        # Extract the value inside the parentheses
        precision_value = fortran_kind.split("kind")[1].strip(" ()")
        
        # Check for 'd' indicating double precision
        if "d" in precision_value:
            return "dp"
        # Check for 'e' indicating single precision
        elif "e" in precision_value or precision_value.isdigit():
            return "sp"
        else:
            raise ValueError(f"Unrecognized kind specifier: {fortran_kind}")
    else:
        raise ValueError(f"Invalid Fortran kind string: {fortran_kind}")
