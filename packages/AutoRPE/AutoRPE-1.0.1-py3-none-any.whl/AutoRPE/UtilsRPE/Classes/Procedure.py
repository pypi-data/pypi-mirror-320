from typing import List
import AutoRPE.UtilsRPE.Error as Error
import AutoRPE.UtilsRPE.Classes.Variable as Variable


class Procedure:
    def __init__(self, _name, module):
        self.name = _name
        self.module = module
        self.variables = []
        self.accessible_var = {}
        self.variables_dictionary = {}

    def add_variable(self, _variable):
        try:
            assert isinstance(_variable, Variable.Variable)
        except AssertionError:
            pass
        _variable.procedure = self
        self.variables.append(_variable)

    def get_variable_by_name(self, name):
        # In the pre-processing phase this dictionary is empty
        if self.variables_dictionary:
            try:
                return self.variables_dictionary[name]
            except KeyError:
                None
        else:
            for variable in self.variables:
                if variable.name.lower() == name.lower():
                    return variable

    def add_accessible_var(self, var):
        try:
            self.accessible_var[var.name] += [var]
        except KeyError:
            self.accessible_var[var.name] = [var]

    def get_accessible_variable_by_name(self, name):
        # In the pre-processing phase this dictionary is empty
        try:
            return self.accessible_var[name]
        except KeyError as err:
            for key, variable in self.accessible_var.items():
                if name.lower() == key.lower():
                    return variable
            raise err
            raise AssertionError(f"{name} in {self.name}")
            for variable in self.variables:
                if variable.name.lower() == name.lower():
                    return variable
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name} parent={self.module})"
    
    def procedure_lines(self) -> List[str] :
        return [l for i,l in enumerate(self.module.line_info) if l.block == self]

    def executable_part(self) -> int:
        import re

        def find_specification_end(lines):
            """
            Identify where the specification part ends in a Fortran module or program.
            
            Args:
                lines (list of str): List of lines from the Fortran source code.
            
            Returns:
                int: The index of the line where the specification part ends.
                    For modules, this is the line with `contains`.
                    For programs, this is the first executable statement.
            """
            # Define patterns for key transitions
            contains_pattern = re.compile(r"^\s*contains\s*$", re.IGNORECASE)  # `contains` keyword
            executable_pattern = re.compile(r"^\s*(call|do|if|write|read|open|close|stop|return|end\s+program)\b", re.IGNORECASE)
            
            for i, line in enumerate(lines):
                stripped_line = line.strip().lower()

                # Check for the `contains` keyword (module case)
                if contains_pattern.match(stripped_line):
                    return i

                # Check for an executable statement (program case)
                if executable_pattern.match(stripped_line):
                    return i

            # If no transition is found, return -1 (no execution part)
            return -1
        lines = [l.line for l in self.procedure_lines() if l.line_number < len(self.module.lines)]
        return find_specification_end(lines)

        


class DerivedType(Procedure):
    def __init__(self, _name, module, _extended_structure=None, is_external=False):
        super(DerivedType, self).__init__(_name, module)
        self.members = []
        self.is_external = is_external
        self.extended_structure = _extended_structure
        self.extension = None

    def add_member(self, _variable):
        _variable.procedure = self
        self.members.append(_variable)

    def get_variable(self, item):
        for variable in self.variables:
            if variable.name.lower() == item.lower():
                return variable

    def get_member_by_position(self, position):
        for member in self.members:
            if member.position == position:
                return member
        raise Error.VariableNotFound("Variable not found in position %d" % position)

    def fill_dictionary_of_accessible_var(self):
        for var in self.variables:
            self.accessible_var[var.name] = [var]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name} parent={self.module})"