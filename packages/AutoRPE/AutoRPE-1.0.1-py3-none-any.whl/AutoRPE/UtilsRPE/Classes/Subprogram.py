from AutoRPE.UtilsRPE.Classes.Procedure import Procedure
import AutoRPE.UtilsRPE.Error as Error


class Subprogram(Procedure):
    def __init__(self, _name, module, is_external=False):
        super(Subprogram, self).__init__(_name, module)
        self.dummy_arguments = []
        self.mandatory_da = []
        self.interface = None
        self.scope = None
        self.declares = []
        self.has_mixed_interface = False
        # External subroutine will just have this attribute to true
        self.is_external = is_external
        # Case in which a use statement is found inside a subroutine definition
        self.use_only_variables = []
        self.level = -1
        self.internal_call = []

    def get_variable_by_position(self, position):
        for variable in self.dummy_arguments:
            if variable.position == position:
                return variable
        raise Error.VariableNotFound(f"Variable {variable.name} in {self.name} not found in position {position}")

    def fill_dictionary_of_variable(self):
        for var in self.variables:
            self.variables_dictionary[var.name] = var

    def fill_dictionary_of_accessible_var(self):

        for var in self.variables + self.module.variables + self.module.accessible_var:
            self.add_accessible_var(var)

        if self.scope is not None:
            for var in self.scope.variables:
                self.add_accessible_var(var)

        try:
            # Main, Interface and TYPE do not have this attribute
            for var in self.use_only_variables:
                self.add_accessible_var(var)
        except AttributeError:
            pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class SubRoutine(Subprogram):
    def __init__(self, _name, module, is_external=False):
        super(SubRoutine, self).__init__(_name, module, is_external)


class Function(Subprogram):
    def __init__(self, _name, module, is_external=False):
        super(Function, self).__init__(_name, module, is_external)
        self.return_value = None
        self.type = "external" if self.is_external else None


class Argument:
    def __init__(self, name, keyword=False, _type=None, var=None):
        self.name = name
        self.keyword = keyword
        self.type = _type
        self.variable = var