import AutoRPE.UtilsRPE.Inserter as Inserter
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.Error as Error
import re


def find_subprogram_call(subprogram_call, module):

    # Find start and end of subprogram block where the fix is due
    _, indices = Inserter.find_subprogram_lines(subprogram_call.block)

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
    line_index = []
    # Search for all the calls with this program name and argument inside the subprogram body
    for index, line in enumerate(module.line_info[indices[0]:indices[1] + 1]):
        line = line.unconditional_line
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
                if subprogram_call.call == c.strip():
                    line_index.append(indices[0] + index)
                    continue

    if not line_index:
        raise Error.LineNotFound("Call %s not found in module %s", subprogram_call.call,
                                 module.module_name)
    return line_index


def cast_variable(var_name, precision, line):
    if precision == "hp":
        cast = "REAL(%s, hp)"
    elif precision == "wp":
        cast = "REAL(%s, wp)"
    elif precision == "dp":
        cast = "REAL(%s, dp)"
    else:
        raise Error.ExceptionNotManaged("Wrong input precision")

    # Avoid casting more than once
    if line.count(cast % var_name):
        name_occurrence = [i for i in re.findall(RegexPattern.escape_string(var_name), line)]
        cast_occurrence = [i for i in re.findall(RegexPattern.escape_string(cast % var_name), line)]
        if len(cast_occurrence) != len(name_occurrence):
            raise Error.ExceptionNotManaged("Line was not fixed properly: check")
        else:
            return line
    elif line.count(var_name):
        assignation = re.search(RegexPattern.assignation, line, re.I)
        if assignation:
            new_line = Inserter.replace_variable_exact_match(var_name, cast % var_name, assignation.group(3))
            new_line = assignation.group(1) + new_line
        else:
            try:
                new_line = Inserter.replace_variable_exact_match(var_name, cast % var_name, line)
            except Error.ExceptionNotManaged:
                raise Error.ExceptionNotManaged
        return new_line
    else:
        raise Error.LineNotFound()
