from __future__ import annotations
from tqdm import tqdm
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.Getter as Getter
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.Inserter as Inserter
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.Classes.Vault as Vault
import AutoRPE.UtilsRPE.Classes.Module as Module
import AutoRPE.UtilsRPE.Classes.Procedure as Procedure

from AutoRPE.UtilsRPE.postproc.Formatter import format_fortran_content

from AutoRPE.UtilsRPE.logger import clean_line, logger
from AutoRPE.UtilsRPE.Classes.Subprogram import SubRoutine
import re
from pathlib import Path

# Hardcoded list, this should be solved
list_of_intrinsics_2fix = ["max", "maxloc", "maxval", "min", "minloc", "minval", "epsilon",
                           "isnan", "count", "abs", "mod", "reshape",
                           "atanh", "sqrt", "log",
                           "sum",
                           "erfc",
                           "merge",
                           "dsqrt", "cmplx", "transfer",
                           "matmul", "dot_product",
                           "huge"]


def Implement_RPE(path_to_input_sources: str, path_to_output_sources: str, blacklist: list[str]) -> ImplementRPE.vault:
    """
    Implements the Reduced Precision Emulator (RPE) for the source code located in `path_to_input_sources`
    and stores the modified sources in `path_to_output_sources`. Additionally, a database (referred to as
    vault) is created to store detailed information about the source code, including functions, subroutines,
    modules, variables and their precisions, and all corresponding dependencies.

    Parameters:
        path_to_input_sources: The directory of the original pre-processed sources.
        path_to_output_sources: The directory where modified sources will be saved.
        blacklist: list of files that should not be modified by the tool.

    Returns:
        Vault: Database with all the information of the code.
    """
    # Changes all the real declaration for RPE declaration
    implementer = ImplementRPE(path_to_input_sources, path_to_output_sources, blacklist,
                               extension=".f90")

    # Replaces real declaration with RPE declaration and save files to output sources
    implementer.replace_real_with_RPE_declaration()
    # Fix the problem the changes implied
    implementer.fix_sources()

    # Insert precision specification into sources
    Inserter.add_sbits_to_rpe_variables(implementer.vault)

    # Add the read_precisions and rpe_emulator use statement into all files (should be accessible for all modules)
    Inserter.insert_use_statement(implementer.vault)

    # Save module txt files to disk
    implementer.save_files()

    # Use fortran formatter with the output files
    implementer.format_output_files()

    # Create the read_precisions.f90 module
    Inserter.create_read_precisions_module(path_to_output_sources, implementer.vault)

    return implementer.vault


class ImplementRPE:
    """
    A class to implement the Reduced Precision Emulator (RPE) for Fortran source code.

    This class facilitates modifying Fortran source files to use reduced precision
    emulation, making necessary adjustments to variable declarations, function and
    subroutine calls, interfaces, and more. It also integrates a vault for managing
    metadata about the code, such as variables, subprograms, and modules.

    Attributes:
        output_path (str): The directory where modified sources will be saved.
        blacklist (list): List of filenames or modules to exclude from modification.
        vault (Vault): A database-like object containing detailed information about
            the code structure and dependencies.
    """

    def __init__(self, path_to_input_sources: str, path_to_output_sources: str, blacklist: list[str], extension=".f90"):
        self.output_path = path_to_output_sources
        self.blacklist = blacklist
        # Parse the sources and obtain all info in the output sources
        self.vault = Vault.create_database(path_to_input_sources, extension)  

    def save_files(self):
        """
        Saves all modified source files to the output directory specified during initialization.

        This method iterates through all modules in the vault and writes their updated
        content to disk.
        """
        for module in self.vault.modules.values():
            module.save_file(self.output_path)
    
    def format_output_files(self):
        for module in self.vault.modules.values():
            module_file_path =  Path(self.output_path) / module.filename
            format_fortran_content(module_file_path)

    def replace_real_with_RPE_declaration(self):
        """
        Replaces declarations of real variables with RPE variables in the source files.

        This method identifies real variable declarations and ensures they are
        converted to `type(rpe_var)` where applicable. It also propagates changes
        to dependent variables while considering constraints such as module
        blacklists and variable usage in external subprograms.
        """
        def ban_condition(variable):
            if variable.is_parameter:
                return True
            if variable.is_used_in_external is not None:
                # There are external subprograms which have an interface for mixed call
                # if variable.is_used_in_external.lower() not in SourceManager.allowed_externals:
                if variable.is_used_in_external not in SourceManager.allowed_externals:
                    return True
            # Black list all the variables that belong to black listed modules
            if variable.module.filename in self.blacklist:
                return True
            return False
        var_found = 0
        # Stores the variables that can't be changed
        unchanged_variables_hash = []
        for v in self.vault.variables:
            if v.type in VariablePrecision.real_id:
                if ban_condition(v):
                    unchanged_variables_hash.append(v.hash_id)
        # Now propagate their dependency
        for hash_id in unchanged_variables_hash:
            var = self.vault.get_variable_from_hash(hash_id)
            for additional_var_hash in var.same_as:
                if var.module.filename in self.blacklist:
                    # Do not propagate if procedure has an interface for mixed or ought to have one
                    if var.procedure.name[-3:] in ['_dp', '_sp'] or var.procedure.name in ['sum3x3_2d',
                                                                                           'sum3x3_3d',
                                                                                           'iom_get_123d',
                                                                                           'set_grid_bounds']:
                        continue

                # This loop could be simplified, but would cause a mem error
                if additional_var_hash not in unchanged_variables_hash:
                    unchanged_variables_hash.append(additional_var_hash)

        for module in self.vault.modules.values():
            if module.filename in self.blacklist:
                continue
            # print("\rReplacing real variables %i/%i  %20s" % (index + 1, n_of_file, source_file.filename), end="")
            # Replace real declarations with type(rpe_var)
            # Look at each line for REAL variable declarations and replace it with type(rpe_var
            for _index, line in enumerate(module.lines):
                _real_with_precision = re.search(RegexPattern.real_with_precision_declaration, line, re.I)
                if not _real_with_precision:
                    # No real declared in line
                    continue
                # Get the variable name
                var_name = re.search(r'(::|FUNCTION)\s*\b(\w+)\b', line).group(2)
                procedure_name = module.line_info[_index].block.name
                # Retrieve the var object
                var_obj = self.vault.get_variable_by_info(var_name, procedure_name, module.name)
                # Update this function using module.line_info[_index].block.name
                # if not BasicFunctions.is_in_reals_blacklist(self.real_blacklist, line, source_file.module_name,
                #                                             dt_name):

                # Replace original precision if allowed
                if var_obj.hash_id not in unchanged_variables_hash:
                    var_obj.type = 'rpe_var'
                    var_found += 1
                    module.lines[_index] = line.replace(_real_with_precision.group(1), "type(rpe_var)")


    def fix_sources(self):
        """
        Applies a series of fixes to the source files to integrate RPE.

        This includes adjusting parameter declarations, function and subroutine calls,
        read/write statements, interfaces, and pointer assignments to ensure compatibility
        with RPE.
        """
        n_of_modules = len(self.vault.modules)

        # This fixes all modules at a time, execute it just once: Remove indistinguishable  interfaces
        self.fix_interfaces()

        for module in tqdm(self.vault.modules.values(), desc="Fixing modules"):
            # Fix all RPE variables declared with assignation
            self.fix_parameter_declaration(module)

            # Remove keyword PURE from function declarations
            self.fix_pure_functions(module)

            # Process intrinsic calls
            self.fix_intrinsic_functions(module)

            # Fix calls to type constructor with RPE components
            self.fix_derived_type_constructor(module)

            # Process read and write calls
            self.fix_read_and_write_calls(module)

            # Fix pointer assignations
            self.fix_pointer_assignations(module)

        self.fix_subprogram_calls()

    def fix_pure_functions(self, module:Module):
        """
        Removes the `pure` attribute from function declarations in a given module.

        Parameters:
            module (Module): The module object containing the lines of source code to modify.
        """
        for _index, line in enumerate(module.lines):
            if re.search(RegexPattern.pure_function_declaration, line, flags=re.IGNORECASE):
                module.lines[_index] = re.sub(RegexPattern.pure_function_declaration, "function ", line,
                                              flags=re.IGNORECASE)

    def fix_parameter_declaration(self, module:Module):
        """
        Adjusts parameter declarations in a module to comply with RPE requirements.

        This includes converting parameter declarations with assignments to use
        the RPE constructor where necessary.

        Parameters:
            module (Module): The module object containing the lines of source code to modify.
        """
        # If there's an assignation whe have to convert everything to an rpe constructor call
        for _index, line in enumerate(module.lines):
            if re.search(RegexPattern.rpe_parameter_declaration, line, flags=re.I):
                arguments = line.split("::")[1]

                assignation = arguments.split("=")[1].strip()
                content_of_declaration = self._find_kind_of_parameter_declaration(assignation,
                                                                                  module.line_info[_index].block)

                # The argument need to be converted to real
                if not content_of_declaration == "is_a_number":
                    # Take the real part of the rpe expression, to be passed to the RPE constructor
                    assignation_real_part = self.get_assignation_real_part(module.line_info[_index].block, assignation,
                                                                           line,
                                                                           content_of_declaration)
                    # Substituting the assignation with its real part in line
                    line = line.replace(assignation, assignation_real_part)
                    assignation = assignation_real_part

                # Add the rpe constructor to assignation in line
                module.lines[_index] = Inserter.add_rpe_type_constructor(assignation, line)
            # There are some variables that are assigned values via the 'data' statement, for which we need a
            # different pattern:
            elif re.search(RegexPattern.data_statement_assignation, line, flags=re.I):
                arguments = re.search(RegexPattern.data_statement_assignation, line, flags=re.I).group(1)
                # assignation = line.split(arguments)[1].strip()  # This is commented because we do not need it for now
                # Assignation via `data`` declaration only accepts numbers (no operations, no using other variables),
                # so we can assume that the assignation part will be a number. We only need to check if the variable
                # is a `rpe_var` type variable or not. First, we get the index of this var in vault.variables:
                indx = next((indx_ for indx_, var_ in enumerate(self.vault.variables) if var_.name == arguments), None)
                if indx is None:
                    raise Exception(f"Could not found var {arguments}.")
                # Then, by accessing to vault.variables[index] we get the type of variable:
                if self.vault.variables[indx].type == 'rpe_var':
                    module.lines[_index] = f"{line.split(arguments)[0]}{arguments}%val{line.split(arguments)[1]}"

    def get_assignation_real_part(self, procedure: Procedure, argument: str, line: str, type_of_exception: str):
        """
        Extracts the real part of an RPE variable or expression during an assignment.

        Parameters:
            procedure: The procedure containing the assignment.
            argument: The argument being assigned.
            line: The source code line containing the assignment.
            type_of_exception: The type of special handling needed for the assignment
                            (e.g., intrinsic, operation, etc.).

        Returns:
            str: The modified assignment string with the real part extracted.
        """
        # The assignation is made with a simple RPE variable
        if type_of_exception == "rpe_var":

            # Take the real part of the RPE var
            return argument + "%val"

        elif type_of_exception == "has_operation":

            # add %val member to rpe variable among the operands
            return self.get_operation_real_part(argument, procedure)
        elif type_of_exception == 'has_intrinsics':

            # Check if the intrinsic argument is an rpe var, and add the %val where needed
            return self.get_intrinsic_real_part(argument, procedure)

        else:
            raise Error.ExceptionNotManaged("This %s is not managed yet" % type_of_exception)

    def fix_interfaces(self):
        """
        Fixes indistinguishable interfaces by resolving conflicts caused by
        substituting `sp/dp` real types with `rpe_var`.

        This ensures that module procedures are properly updated to match
        the expected interfaces.
        """
        all_interfaces = self.vault.interfaces_dictionary
        interfaces_to_fix = [interface for interface in all_interfaces
                             if len(all_interfaces[interface].key) != len(all_interfaces[interface].subprogram)]
        if interfaces_to_fix:
            for interface in interfaces_to_fix:
                interface = all_interfaces[interface]
                interface_to_remove = [n.name for n in interface.subprogram if n.name not in interface.key.values()]
                for interface_name in interface_to_remove:
                    for index, line in enumerate(interface.module.lines):
                        # Matches the name of the interface
                        match = re.search(r'MODULE PROCEDURE .*(\b%s\b)' % interface_name, line)
                        if match:
                            # Remove the offending module procedure, keeps the rest
                            interface.module.lines[index] = "MODULE PROCEDURE " + \
                                                            ",".join([i.strip() for i in
                                                                      line.split("MODULE PROCEDURE")[1].split(",")
                                                                      if not i.strip() == interface_name])
                            if interface.module.lines[index].strip() == "MODULE PROCEDURE":
                                interface.module.lines[index] = ""
                            break
                    if not match:
                        raise Error.ExceptionNotManaged("An indistinguishable interface was not fixed!")

    def fix_derived_type_constructor(self, module: Module):
        """
        Adjusts calls to derived type constructors in the given module to be compatible with RPE.

        This method ensures that arguments passed to derived type constructors
        match the expected type, performing conversions if necessary.

        Parameters:
            module: The module object containing the lines of source code to modify.
        """
        for line_index, line in enumerate(module.lines):
            called_derived_type = self._call_to_derived_type_constructor(line, module.module_name)
            if called_derived_type and not called_derived_type.is_external:
                # Find call to type constructor
                constructor_call = BasicFunctions.close_brackets(
                    line[re.search(r'\b%s\b' % called_derived_type.name, line, re.I).start():])
                called_arguments = CallManager.find_call_arguments(constructor_call)
                if not called_arguments:
                    continue

                fixed_constructor_call = constructor_call
                for argument_index, argument in enumerate(called_arguments):
                    argument_type = Getter.get_type_of_contents(argument, module.line_info[line_index].block,
                                                                self.vault)
                    dummy_argument = called_derived_type.get_member_by_position(argument_index)
                    if not dummy_argument:
                        raise AssertionError("Variable not found in position: %i" % argument_index)
                    if VariablePrecision.type_are_equivalent(argument_type, dummy_argument.type):
                        continue
                    elif argument_type in VariablePrecision.real_id and dummy_argument.type == "rpe_var":
                        fixed_constructor_call = Inserter.add_rpe_to_argument(argument, fixed_constructor_call)
                    else:
                        raise AssertionError("Types do not coincide and the case is not considered %s %s" % (
                            argument_type, dummy_argument.type))
                module.lines[line_index] = line.replace(constructor_call, fixed_constructor_call)

    def _fix_read_calls(self, module):
        for line_index, line in enumerate(module.lines):
            matches = re.search(RegexPattern.call_to_read, BasicFunctions.remove_if_condition(line), re.I)
            if matches:
                read_call = BasicFunctions.close_brackets(matches.groups()[0])
                # Remove the read call
                read_arguments = BasicFunctions.remove_if_condition(line)[matches.start(1):].replace(read_call, "")
                # Continue just if arguments follow the call
                if not read_arguments:
                    continue
                replacement = read_arguments.replace(" ", "")
                # Add parenthesis because the read() doesn't use them
                arguments = CallManager.find_call_arguments("(" + replacement + ")")

                # Further separate arguments. Used in case of loops READ(inum,*) ( tpifl (jfl), jfl=1, jpnrstflo)
                list_arguments = []
                index_to_remove = []
                for argument_index, argument in enumerate(arguments):
                    if BasicFunctions.is_all_inside_parenthesis(argument):
                        index_to_remove.append(argument_index)
                        argument = CallManager.find_call_arguments(argument)
                        list_arguments.extend(argument)
                # Remove the original argument
                for i in index_to_remove[::-1]:
                    del arguments[i]
                # Add the split argument
                arguments.extend([i for i in list_arguments])

                # Check the argument type and replace just if is an rpe
                for argument_index, argument in enumerate(arguments):
                    argument_type = Getter.get_type_of_contents(argument, procedure=module.line_info[line_index].block,
                                                                vault=self.vault)
                    if argument_type == "rpe_var":
                        replacement = Inserter.replace_variable_exact_match(argument, argument + "%val", replacement)

                # Rebuilt the line
                # self.lines[line_index] = read_call + " " + read_arguments
                module.lines[line_index] = line.replace(read_arguments, replacement)

    def _fix_write_calls(self, module: Module):
        for l_index, line in enumerate(module.lines):
            write_statement = re.search(RegexPattern.call_to_function_name % "write", line, re.I)
            if write_statement:
                wc = BasicFunctions.close_brackets(line[write_statement.start():])
                # Separate write statement from arguments
                split_index = line.index(wc) + len(wc)
                write_statement, arguments = line[:split_index], line[split_index:]
                if not arguments.strip():
                    # There is no argument to fix
                    continue
                # Transform the string in a list of arguments
                arguments = CallManager.find_call_arguments("(" + arguments + ")")

                for argument_index, argument in enumerate(arguments):
                    # Prepare array for possible match
                    hardcoded_array = []
                    if NatureDeterminer.is_hardcoded_array(argument, hardcoded_array):
                        subst = False
                        for el_index, el in enumerate(hardcoded_array):
                            argument_type = Getter.get_type_of_contents(el, module.line_info[l_index].block, self.vault)
                            if argument_type == "rpe_var":
                                subst = True
                                hardcoded_array[el_index] = "real( %s )" % el
                        if subst:
                            arguments[argument_index] = "(/ " + ", ".join(hardcoded_array) + " /)"
                    elif re.match(r"\(", argument):
                        # For calls like  WRITE(numout,9402) (ilci(ji,jj),ilcj(ji,jj),ji=il1,il2)
                        array_elements = CallManager.find_call_arguments(argument)
                        for el_index, el in enumerate(array_elements):
                            argument_type = Getter.get_type_of_contents(el, module.line_info[l_index].block, self.vault)
                            if argument_type == "rpe_var":
                                array_elements[el_index] = "real( %s )" % el
                        arguments[argument_index] = "( " + ", ".join(array_elements) + " )"
                    else:
                        argument_type = Getter.get_type_of_contents(argument, module.line_info[l_index].block,
                                                                    self.vault)
                        if argument_type == "rpe_var":
                            arguments[argument_index] = "real( %s )" % argument
                module.lines[l_index] = write_statement + " " + ", ".join(arguments)

    def fix_read_and_write_calls(self, module: Module):
        """
        Adjusts read and write calls in a module to handle RPE variables correctly.

        Parameters:
            module (Module): The module object containing the lines of source code to modify.
        """
        self._fix_read_calls(module)
        self._fix_write_calls(module)

    def fix_pointer_assignations(self, module: Module):
        """
        Adjusts pointer assignments in the given module to be compatible with RPE variables.

        This method ensures that assignments between pointers and targets of
        different types (e.g., `rpe_var` and standard types) are handled correctly.

        Parameters:
            module (Module): The module object containing the lines of source code to modify.
        """
        for line_index, line in enumerate(module.lines):
            #TODO: The new timing function uses some pointing structures that are difficult to handle. For now we will just ignore it.
            # However this error clause is probably too broad.
            try:
                assignation = Getter.get_pointer_assignment(line, self.vault, module.line_info[line_index].block)
            except Error.VariableNotFound as err:
                logger.error(err)
                assignation = None
            if assignation:
                ptr, target = assignation[0]
                if 'rpe_var' in [ptr.type, target.type] and ptr.type != target.type:
                    module.lines[line_index] = line.replace(target.name, "%s%%val" % target.name)
                    raise Error.ExceptionNotManaged("Why is this happening? Are dependency propagated correctly?")

    def fix_intrinsic_functions(self, module: Module):
        """
        Adjusts calls to intrinsic functions in the given module to handle RPE variables.

        This involves identifying intrinsic function calls, determining whether
        their arguments are RPE variables, and applying the appropriate transformations
        to ensure compatibility.

        Parameters:
            module (Module): The module object containing the lines of source code to modify.
        """
        # Fix all the intrinsics function that are not overloaded in the RPE library
        for _index, _line in enumerate(module.lines):

            # No need to fix intrinsics in declaration, they have already been fixed
            if re.search(RegexPattern.variable_declaration, _line, re.I):
                continue
            # Cycle through the matches, that can be more than one in a line
            replacements = []
            pieces_to_replace = []
            # Mask literals to avoid false positive
            mask_line = MaskCreator.mask_literal(_line)

            matches_start_list = [i.start(1) for i in re.finditer(RegexPattern.call_to_function, mask_line, re.I)
                                  if i.group(1).lower() in list_of_intrinsics_2fix]

            for start in matches_start_list[::-1]:
                # Save the piece that need change
                pieces_to_replace.append(_line[start:].strip())

                # Current index
                i_match = len(pieces_to_replace) - 1
                # Get intrinsic call
                pieces_to_replace[i_match] = BasicFunctions.close_brackets(pieces_to_replace[i_match])
                replacements.append(pieces_to_replace[i_match])

                _line = _line[:start] + _line[start:].replace(pieces_to_replace[i_match],
                                                              "ALREADY_FIXED_" + str(i_match))
                # Split the calls argument
                arguments = CallManager.find_call_arguments(pieces_to_replace[i_match])
                for arg in arguments:
                    if arg.count("ALREADY_FIXED_"):
                        if re.match(r"ALREADY_FIXED_\d+", arg):
                            continue
                        split_elements = []
                        if NatureDeterminer.has_operations(arg, split_elements):
                            # Split elements, removing the arguments already fixed, adding the others to the loop
                            arguments.extend([el for el in split_elements if not el.count("ALREADY_FIXED_")])
                            continue
                        if NatureDeterminer.is_logical_comparison(arg):
                            # For example: mask = iszij1 == ALREADY_FIXED_0
                            continue
                        try:
                            # Case in which an intrinsic is used as indexing of an array
                            Getter.get_variable(arg, module.line_info[_index].block, self.vault)
                        except Error.VariableNotFound:
                            continue
                            # raise Error.ExceptionNotManaged("Check this intrinsic please")

                    argument_type = Getter.get_type_of_contents(arg, module.line_info[_index].block, self.vault)
                    if argument_type != 'rpe_var':
                        continue

                    if re.match(RegexPattern.variable, arg):
                        replacements[i_match] = Inserter.add_val_to_argument(arg, replacements[i_match])
                    else:
                        replacements[i_match] = Inserter.add_real_to_argument(arg, replacements[i_match],
                                                                              VariablePrecision.real_id["wp"])
            for i_match, (piece_to_replace, replacement) in reversed(
                    list(enumerate(zip(pieces_to_replace, replacements)))):
                # Starting from the end, and substituting just first match we avoid re-substituting matches
                _line = _line.replace("ALREADY_FIXED_" + str(i_match), replacement, 1)
            module.lines[_index] = _line

    def _fix_external_call(self, external_call, line):

        temporal_call = BasicFunctions.remove_if_condition(line)

        called_arguments = external_call.arguments
        # In case the procedure is not found, consider it external
        for argument in called_arguments:
            if argument.type == "rpe_var":
                # If it is not a single variable a cast is safe, it must be intent IN
                if NatureDeterminer.has_operations(argument.name):
                    temporal_call = Inserter.add_real_to_argument(argument.name, temporal_call,
                                                                  VariablePrecision.real_id["dp"])
                else:
                    # Here we add the real member of the RPE type
                    temporal_call = Inserter.add_rpe_real_member_to_argument(argument.name, temporal_call)
        return temporal_call.strip()

    def _fix_arguments(self, subprogram_call):
        original_line = subprogram_call.line_info.line
        called_arguments = CallManager.find_call_arguments(subprogram_call.call)
        if not subprogram_call.subprogram.is_external:
            for index, (called_arg, arg, dummy_a) in enumerate(zip(called_arguments, subprogram_call.arguments, subprogram_call.dummy_arguments)):

                # This argument is not a real, don't need to check
                if arg.type not in list(VariablePrecision.real_id.values()) + ['rpe_var']:
                    continue

                # This argument is coherent
                if VariablePrecision.type_are_equivalent(arg.type, dummy_a.type):
                    continue

                # Inconsistency between used argument and what the call expects
                if dummy_a.intent == "in":
                    if dummy_a.type == "rpe_var" and arg.type in VariablePrecision.real_id:
                        called_arguments[index] = Inserter.add_rpe_to_argument(arg.name, called_arg, dummy_a.is_pointer)
                    elif dummy_a.type in VariablePrecision.real_id and arg.type == "rpe_var":
                        if dummy_a.is_pointer and arg.variable.is_pointer:
                            print('call %s', subprogram_call.call)
                            # raise Error.ExceptionNotManaged("This dependency should have been be considered")
                        # %val member is dp by def, so we can use the val member only if the dummy is dp
                        if arg.variable is not None and not dummy_a.type == VariablePrecision.real_id['sp']:
                            called_arguments[index] = Inserter.add_val_to_argument(arg.name, called_arg)
                        # In all other cases, a cast is the only solution
                        else:
                            called_arguments[index] = Inserter.add_real_to_argument(arg.name, called_arguments[index],
                                                                                    VariablePrecision.real_id['dp'])
                # The value of the argument can be modified by the call, if its an rpe pass the val
                else:
                    if arg.type == "rpe_var" and dummy_a.type in VariablePrecision.real_id:
                        called_arguments[index] = Inserter.add_val_to_argument(arg.name, called_arg)
                    else:
                        raise Error.ExceptionNotManaged("Here we should use temporal variables")
            # Create the new call

            # Initialize fixed_call_name with the default value
            fixed_call_name = subprogram_call.name

            # TODO: The following section was only needed to fix a bug with a subprogram_call with a function glob_sum
            # which was replacing the interface call with the call to the matching function instead.
            # Handle the edge case in which the call used the interface name and it differs from the subprogram_call
            # Check if the subprogram has an interface and if the interface name is different from the subprogram call name
            has_interface = subprogram_call.subprogram.interface is not None
            interface_name_differs = has_interface and subprogram_call.subprogram.interface.name != subprogram_call.name

            if has_interface:
                interface_name = subprogram_call.subprogram.interface.name
                if interface_name_differs:
                    # Check if the interface name is present in the original line (case insensitive)
                    interface_in_line = re.search(r'\b' + re.escape(interface_name) + r'\b', original_line, re.IGNORECASE) is not None
                    if interface_in_line:
                        fixed_call_name = interface_name

            fixed_call = f"{fixed_call_name}({', '.join(called_arguments)})"
        else:
            fixed_call = self._fix_external_call(subprogram_call, subprogram_call.call)

        if isinstance(subprogram_call.subprogram, SubRoutine): fixed_call = f" {fixed_call}"

        # Nothing needed to be fixed
        if subprogram_call.call == fixed_call:
            return
        module = subprogram_call.block.module
        index = subprogram_call.line_info.line_number
        module.lines[index] = original_line.replace(subprogram_call.call, fixed_call)

    def fix_subprogram_calls(self):
        """
        Ensures consistency between subprogram calls and their arguments.

        This includes adjusting arguments passed to subprograms based on their
        expected types and modifying the calls as needed.
        """
        # Check if call and arguments are coherent, fix where not
        for subprogram_calls in self.vault.dictionary_of_calls.values():
            for call in subprogram_calls:
                # Refresh arguments, that may have changed type due to previous fixes
                call.update_actual_arguments(self.vault)
                self._fix_arguments(call)

    def _find_kind_of_parameter_declaration(self, argument, procedure):
        """Return the nature of the parameter declaration. Depending on the type, the fix will be different"""
        type_of_exception = None
        # These are real, but need some manipulation before adding the RPE constructor
        if argument.count(","):
            if argument.count("(/") or argument.count("RESHAPE([") or re.search(r"= *\[.*\]", argument):
                type_of_exception = "is_a_number"
            elif argument.count("rpe_var("):
                type_of_exception = "already_fixed"
        else:
            # Get the type of content
            content_type = Getter.get_type_of_contents(argument, procedure, self.vault)

            # Check for intrinsic first: they return a real, but their argument need to be fixed if its an RPE
            if NatureDeterminer.has_intrinsics(argument):
                type_of_exception = 'has_intrinsics'
            # If it doesn't have intrinsic and is real or integer, then is a number: just add and RPE constructor
            elif content_type in list(VariablePrecision.real_id) + ['integer']:
                return "is_a_number"
            # Need to split operand, find rpe_variable and take their real part
            elif NatureDeterminer.has_operations(argument):
                type_of_exception = 'has_operation'
            # Just a %val will be added
            else:
                type_of_exception = "rpe_var"

        if not type_of_exception:
            print(argument)
            pass
            # raise Error.ExceptionNotManaged("Unknown type of parameter declaration")
        return type_of_exception

    def get_operation_real_part(self, argument: str, procedure: Procedure):
        """
        Extracts the real parts of RPE variables involved in an operation.

        This method processes operations containing RPE variables and ensures
        that their real parts are correctly referenced.

        Parameters:
            argument (str): The expression containing the operation.
            procedure (Procedure): The procedure where the operation is defined.

        Returns:
            str: The operation with the real parts of RPE variables substituted.
        """
        # Get the elements in operation
        split_elements = []
        NatureDeterminer.has_operations(argument, split_elements)
        argument_real_part = argument
        for element in split_elements:
            # If is an RPE get the real part
            element = element.strip()

            if Getter.get_type_of_contents(element, procedure, self.vault) == 'rpe_var':
                element_real_part = " %s%%val " % element
            # In case of intrinsic we need to fix the argument, because it has to be real
            elif NatureDeterminer.has_intrinsics(element):
                element_real_part = self.get_intrinsic_real_part(element, procedure)
            else:
                continue
            argument_real_part = Inserter.replace_variable_exact_match(element, element_real_part,
                                                                       argument_real_part)
        return argument_real_part

    def get_intrinsic_real_part(self, string: str, procedure: Procedure):
        """
        Adjusts the arguments of intrinsic function calls to handle RPE variables.

        This method ensures that RPE variables used as arguments in intrinsic
        functions have their real parts correctly referenced.

        Parameters:
            string: The intrinsic function call as a string.
            procedure: The procedure where the function call is defined.

        Returns:
            str: The modified function call with the real parts of RPE variables substituted.
        """
        # We need to fix ALL intrinsic, because their overload is not available at declaration time
        intrinsic_argument = MaskCreator.mask_intrinsics(string)
        rpe_element = []
        for arg in intrinsic_argument:
            if Getter.get_type_of_contents(arg, procedure, self.vault) == 'rpe_var':
                # Get the real part of the RPE variable
                split_elements = []
                if NatureDeterminer.has_operations(arg, split_elements):
                    # List rpe element involved in the operation
                    rpe_element.extend([el for el in split_elements if
                                        Getter.get_type_of_contents(el, procedure, self.vault) == "rpe_var"])

                else:
                    rpe_element.append(arg)
        for el in rpe_element:
            string = Inserter.replace_variable_exact_match(el, el + "%val", string)
        return string

    def _call_to_derived_type_constructor(self, line, module_name):
        line = MaskCreator.remove_literals(line)
        matches = re.finditer(RegexPattern.assignation_to_DT, line, flags=re.I)
        if matches:
            for m in matches:
                fun_name = m.groups()[0]
                try:
                    derived_type = self.vault.get_derived_type_constructor(fun_name)
                    if derived_type:
                        return derived_type
                except Error.DerivedTypeNotFound:
                    pass
        return None
