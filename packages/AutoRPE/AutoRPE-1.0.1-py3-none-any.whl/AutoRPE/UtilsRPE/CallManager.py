import AutoRPE.UtilsRPE.Classes.Interface as Interface
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.Classes.Procedure as Procedure
import AutoRPE.UtilsRPE.Classes.Vault as Vault
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.Error as Error
import re

from AutoRPE.UtilsRPE.logger import clean_line, logger


def find_called_function(string: str):
    """
    Identifies the name of a function being called in a given string.

    Parameters:
        string (str): The input string containing the function call.

    Returns:
        str: The name of the called function.
    """
    return re.match(RegexPattern.call_to_function, string.strip(), re.I).group(1)


def find_call_arguments(string: str):
    """
    Extracts the arguments of a function call from a given string.

    Parameters:
        string (str): The input string containing the function call.

    Returns:
        list[str]: A list of arguments as strings.
    """

    # Check contains a call
    first_parenthesis = re.search(r'\(', string)
    if not first_parenthesis:
        return []
    else:
        # Remove function name
        string = string[first_parenthesis.start():]
    # Remove first, last brackets
    string = BasicFunctions.remove_outer_brackets(string)

    # Call without arguments
    if not string.strip():
        return []

    # Index that mark if we are inside an array
    bracket_balance = 0
    for char_index, c in enumerate(string):
        if c in ["(", "["]:
            bracket_balance -= 1
        elif c in [")", "]"]:
            bracket_balance += 1
        elif c == "," and bracket_balance == 0:
            # Mark commas outside arrays, or function calls
            string = string[:char_index] + "#" + string[char_index+1:]
        else:
            continue
    if string.count("#"):
        return [a.strip() for a in string.split("#")]
    else:
        return [string.strip()]


def is_call_to_function(contents: str, procedure: Procedure, vault: Vault, called_function=[]):
    """
    Determines if a string represents a function call.

    Parameters:
        contents (str): The input string to check.
        procedure (Procedure): Procedure object where the call is made.
        vault (Vault): The database containing metadata about the code.
        called_function (list, optional): A list to store details about the called function.

    Returns:
        bool: True if the string represents a function call, False otherwise.
    """
    from AutoRPE.UtilsRPE.NatureDeterminer import is_array
    """
    Identify if a certain string is a call to a function or it's an array.
    """
    # Check if matches the syntax of a function call
    call_to_function = re.match(RegexPattern.call_to_function, contents.strip(), re.I)
    if not call_to_function:
        return False

    # Check brackets match
    if not contents == BasicFunctions.close_brackets(contents):
        return False

    # Check if one of the argument is a slice: then is an array (matches function call syntax)
    if is_array(contents, check_sliced=True):
        return False

    function_name = find_called_function(contents)

    # Match the ret val of a function or fortran builtins (IF(.false.) will match function regex)
    if (isinstance(procedure, Subprogram.Function) and function_name == procedure.return_value.name) or \
            function_name.lower() in SourceManager.Fortran_builtins:
        return False

    # If is call to intrinsic
    if function_name.lower() in list(SourceManager.list_of_intrinsics):
        called_function.append(function_name.lower())
        return True
    try:
        function = vault.get_subprogram_by_name(function_name, block_type=['Function', 'Interface'])
        called_function.append(function)
    except Error.ProcedureNotFound:
        # Must be a variable
        try:
            var = vault.variables_dictionary[function_name]
            # Match variables ensuring that it is not the ret_val of a function with the same name
            if var[0].procedure.name != var[0].name:
                return False
        except KeyError:
            # External function, if vault externals have not yet been filled
            raise Error.ProcedureNotFound

    # It is a subprogram
    return True


def get_function(string: str, procedure: Procedure, vault: Vault):
    """
    Retrieves the function(s) being called in a given string.

    Parameters:
        string (str): The input string.
        procedure (Procedure): The procedure where the call is made.
        vault (Vault): The database containing metadata about the code.

    Returns:
        list: A list of function objects being called.
    """
    from AutoRPE.UtilsRPE.NatureDeterminer import is_function_declaration_statement
    not_found = []
    ret_val = []
    if string.count("::") or is_function_declaration_statement(string):
        return []
    # If it's a call to sbr search for function as arguments. Here we look for 'call' statements
    # anywhere in the line, not just in the beginning of the line (it can go aftern an 'if' statement)
    _match = re.search(RegexPattern.name_occurrence % 'call', string, re.I)
    if _match:
        # We only need to focus on the part of the line that corresponds to the subroutine call:
        call_string = string[_match.start():]
        arguments = find_call_arguments(call_string)
        for arg in arguments:
            try:
                func = _get_subprogram(arg, procedure, vault, RegexPattern.call_to_function,
                                       Subprogram.Function)
            except Error.ProcedureNotFound as func_not_found:
                not_found.append(func_not_found.args[0][0])
                continue
            ret_val.extend(func)
    else:
        ret_val = _get_subprogram(string, procedure, vault, RegexPattern.call_to_function,
                                  Subprogram.Function)

    if len(not_found):
        raise Error.ProcedureNotFound(not_found)
    return ret_val


def get_subroutine(string: str, procedure: Procedure, vault: Vault):
    """
    Retrieves the subroutine(s) being called in a given string.

    Parameters:
        string (str): The input string.
        procedure (Procedure): The procedure where the call is made.
        vault (Vault): The database containing metadata about the code.

    Returns:
        list: A list of subroutine objects being called.
    """
    if not re.search(RegexPattern.name_occurrence % 'call', string, re.I):
        return []
    else:
        return _get_subprogram(string, procedure, vault, RegexPattern.call_to_subroutine, Subprogram.SubRoutine)


def _get_subprogram(string, procedure, vault, regex_pattern, procedure_type):
    import AutoRPE.UtilsRPE.Getter as Getter
    string = string.strip()
    # string = MaskCreator.remove_literals(string)
    to_return = []
    external_subprogram = []
    is_unknown_external = False
    # Check is not a function or subroutine declaration, to avoid matching with functions syntax
    if re.search(RegexPattern.subprogram_declaration, string, re.I):
        return to_return

    # Avoid structures to be identified as subprogram
    purged_string = MaskCreator.mask_arrays_and_structures(string, only_structures=True)
    matches = [m for m in re.finditer(regex_pattern, purged_string, flags=re.I)]
    if matches:
        for m in matches:
            subprogram_name = m.group(1)

            # Try to look for a reachable variable with the same name
            var = procedure.get_variable_by_name(subprogram_name)
            if var is not None:
                continue

            # Exclude intrinsics functions or subroutines
            if subprogram_name.lower() in SourceManager.list_of_intrinsics:
                continue

            # Exclude derived types constructors
            if subprogram_name in vault.block_dictionary['DerivedType']:
                continue

            # Get the actual call
            call = re.sub(r'\bcall\b', '', BasicFunctions.close_brackets(string[m.start():]), flags=re.I)

            if procedure_type == Subprogram.Function:
                try:
                    # Check is not a variable or a builtin function
                    if not is_call_to_function(call, procedure, vault):
                        continue
                except Error.ProcedureNotFound:
                    # An external function was hit, create an external subprogram to be returned as the error
                    is_unknown_external = True
                    subprogram = procedure_type(subprogram_name, module=None, is_external=True)

            if not is_unknown_external:
                # We ruled out the possibility of variables or intrinsics: must be a subprogram
                try:
                    subprogram = vault.get_subprogram_by_name(subprogram_name,
                                                              module=procedure.module)
                except Error.ProcedureNotFound:
                    # An external subroutine was hit, create an external subprogram to be returned as the error
                    is_unknown_external = True
                    subprogram = procedure_type(subprogram_name, module=None, is_external=True)

            # Find called arguments
            called_arguments = find_call_arguments(call)

            if not isinstance(subprogram, procedure_type):
                # Search for the correct subprogram
                if isinstance(subprogram, Interface.Interface):
                    subprogram = Getter.get_interface(called_arguments,
                                                      interface=subprogram,
                                                      block=procedure,
                                                      vault=vault)
                    # If the subprogram is not of the correct type, skip the occurrence
                    if not isinstance(subprogram, procedure_type):
                        continue
                # TODO remove?
                elif isinstance(subprogram, Procedure.DerivedType):
                    continue
                else:
                    raise Error.ProcedureNotFound(subprogram)

            subprogram_call = create_SubprogramCall(call, subprogram, procedure, vault)
            if is_unknown_external:
                external_subprogram.append(subprogram_call)
            else:
                to_return.append(subprogram_call)
    # Raise an error returning all the unknown subprogram calls found in line
    if external_subprogram:
        raise Error.ProcedureNotFound(external_subprogram)
    return to_return


def create_SubprogramCall(call: str, subprogram: Subprogram, procedure: Procedure, vault: Vault):
    """
    Creates a `SubprogramCall` object for a given subprogram call.

    Parameters:
        call (str): The string representation of the subprogram call.
        subprogram (Suborogram): The subprogram being called.
        procedure (Procedure): The procedure where the call is made.
        vault (Vault): The database containing metadata about the code.

    Returns:
        SubprogramCall: The created `SubprogramCall` object.
    """
    # Interfaces can be called both with function name or the interface name
    subprogram_name = subprogram.name
    if subprogram.interface:
        if re.search(RegexPattern.name_occurrence % subprogram.interface.name, call):
            subprogram_name = subprogram.interface.name
    # Create the obj
    subprogram_call = SubprogramCall(subprogram_name, subprogram, procedure)
    # Line_info may not be filled yet, pass the call and fill dummy and dummy arguments
    subprogram_call.fill_dummy_arg(call)
    subprogram_call.update_actual_arguments(call=call, vault=vault)
    subprogram_call.check_argument_consistency()
    return subprogram_call


class SubprogramCall:
    """
    Represents a call to a subprogram (function or subroutine) in the source code.

    Attributes:
        name (str): The name of the subprogram being called.
        subprogram (Subprogram): The subprogram object representing the called subprogram.
        is_external (bool): Whether the subprogram is external.
        block: The block in which the call is made.
        arguments (list): The actual arguments passed to the subprogram.
        dummy_arguments (list): The expected dummy arguments for the subprogram.
        cast: The type cast applied to the arguments, if any.
        line_info: Information about the line in which the call occurs.
        index (int): The index of the call in the source line.
    """
    def __init__(self, name, subprogram, block):
        self.name = name
        self.subprogram = subprogram
        self.is_external = subprogram.is_external
        self.block = block
        self.arguments = []
        self.dummy_arguments = []
        self.cast = None
        self.line_info = None
        self.index = 0

    @property
    def call(self):
        """
        Retrieves the string representation of the subprogram call.

        Returns:
            str: The subprogram call as a string.

        Raises:
            ExceptionNotManaged: If the line information is not filled or the call cannot be located.
        """
        import re
        if self.line_info is None:
            raise Error.ExceptionNotManaged("Line info has not been filled yet")
        line = self.line_info.line
        # Get the correct call based on the index (in case there is more than one occurrence)
        
        # Search with the subprogram name
        match = re.finditer(RegexPattern.name_occurrence % self.name, line, re.I)
        starts = [m.start() for m in match]

        # Search with the interface name
        if not starts:
            match = re.finditer(RegexPattern.name_occurrence % self.subprogram.interface.name, line, re.I)
            starts = [m.start() for m in match]
        if not starts:
                raise Error.ExceptionNotManaged(f"Couldn't find call to {self.name!r} in line {line!r}")

        start = starts[self.index]
        return BasicFunctions.close_brackets(line[start:])
    
    

    @call.setter
    def call(self, updated_call):
        """
        Updates the subprogram call in the source code.

        Parameters:
            updated_call (str): The updated string representation of the call.

        Raises:
            ExceptionNotManaged: If the line information is not filled.
        """
        import re
        if self.line_info is None:
            raise Error.ExceptionNotManaged("Line info has not been filled yet")
        module = self.block.module
        line_number = self.line_info.line_number
        line = module.lines[line_number]
        # Get the correct call based on the index (in case there is more than one occurrence)
        match = re.finditer(RegexPattern.name_occurrence % self.name, line, re.I)
        start = [m.start() for m in match][self.index]
        line = line[:start] + updated_call
        module.lines[line_number] = line

    def check_argument_consistency(self):
        """
        Verifies the consistency between the arguments passed to the subprogram
        and the expected dummy arguments.
        """
        for du, aa in zip(self.dummy_arguments, self.arguments):
            if du.intent in ['out', 'inout'] and aa.variable is None and aa.type != "external":
                clean_line()
                logger.warn(f"Variable {du.name!r} should have intent in {self.subprogram.name}")

    def fill_dummy_arg(self, call=None):
        """
        Populates the list of dummy arguments for the subprogram call.

        Parameters:
            call (str, optional): The string representation of the call. If not provided,
                                  the existing call in the object is used.
        """
        import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
        if call is None:
            call = self.call
        called_arguments = find_call_arguments(call)
        if self.subprogram.is_external:
            return
        self.dummy_arguments = []
        for index, argument in enumerate(called_arguments):
            key_arg = []
            if not self.subprogram.is_external:
                if NatureDeterminer.is_keyword_argument(argument, key_arg):
                    dummy_var = self.subprogram.get_variable_by_name(key_arg[0])
                else:
                    dummy_var = self.subprogram.get_variable_by_position(index)
                self.dummy_arguments.append(dummy_var)

    def update_actual_arguments(self, vault, call=None):
        """
        Updates the list of actual arguments for the subprogram call.

        Parameters:
            vault: The vault object containing metadata about the code.
            call (str, optional): The string representation of the call. If not provided,
                                the existing call in the object is used.
        """
        import AutoRPE.UtilsRPE.Getter as Getter
        import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer

        if call is None:
            call = self.call
        called_arguments = find_call_arguments(call)
        self.arguments = []
        for index, argument in enumerate(called_arguments):
            key = False
            try:
                key_arg = []
                if NatureDeterminer.is_keyword_argument(argument, key_arg):
                    argument = key_arg[1]
                    var_type = Getter.get_type_of_contents(argument, procedure=self.block, vault=vault)
                else:
                    var_type = Getter.get_type_of_contents(argument, procedure=self.block, vault=vault)
            except Error.VariableNotFound:
                # An external variable has been used
                var_type = "external"

            if not var_type == "external":
                try:
                    var = Getter.get_variable(argument, procedure=self.block, vault=vault)
                except Error.VariableNotFound:
                    var = None
                var_type = var_type if var_type is not None else var.type
                arg = Subprogram.Argument(argument, key, var_type, var)
            else:
                arg = Subprogram.Argument(argument, _type="external", var=None)

            self.arguments.append(arg)
    
    def __repr__(self):
        return f"SubprogramCall(name={self.name!r}, subprogram={self.subprogram!r})"
