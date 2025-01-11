import itertools


class Variable:
    # Increment the var number automatically every time a variable is created
    incremental_number = itertools.count().__next__

    def __init__(self, procedure, _name, _type, _dimension, _module, _declaration=None):
        import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
        self.id = None
        self.incremental_number = Variable.incremental_number()
        self.module = _module
        self.procedure = procedure
        self.name = _name
        self.type = _type
        self.original_type = _type
        self.dimension = _dimension
        self.is_dummy_argument = False
        self.intent = None
        self.is_global = True if self.procedure.name == 'main' else False
        self.is_optional = None
        self.is_retval = False
        self.is_pointer = False
        self.position = None
        self.mandatory_position = None
        self.is_allocatable = False
        self.allocate_info = AllocateInfo(None, False)
        self.appears_in_namelist = False
        self.is_used_in_external = None
        self.precision = None
        self.is_parameter = None
        self.is_member_of = None
        self.same_as = []
        self.hash_id = BasicFunctions.hash_from_list([self.name, self.procedure.name, self.module.name])
        # to be used in the analysis
        self.is_used = False
        self.cluster_id = -1
        self.is_banned = False
        self.declaration = _declaration

        self.check_type()

    def check_type(self):
        if self.type is None:
            if self.declaration and self.declaration.count("external"):
                self.type = "external"
            else:
                raise AssertionError(f"Type of {self} is None")


    def is_equal_to(self, other):
        return self.name == other.name and \
               self.type == other.type and \
               self.is_member_of == other.is_member_of and \
               self.dimension == other.dimension and \
               self.is_pointer == other.is_pointer

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name} parent={self.procedure})"
    
    def description(self):
        description_str = f"""
        Name: {self.name}
        Procedure: {self.procedure}
        Module: {self.module}
        Type: {self.type}
        ID: {self.id}
        Incremental Number: {self.incremental_number}
        Original Type: {self.original_type}
        Dimension: {self.dimension}
        Is Dummy Argument: {self.is_dummy_argument}
        Intent: {self.intent}
        Is Global: {self.is_global}
        Is Optional: {self.is_optional}
        Is Retval: {self.is_retval}
        Is Pointer: {self.is_pointer}
        Position: {self.position}
        Mandatory Position: {self.mandatory_position}
        Is Allocatable: {self.is_allocatable}
        Allocate Info: {self.allocate_info}
        Appears in Namelist: {self.appears_in_namelist}
        Is Used in External: {self.is_used_in_external}
        Precision: {self.precision}
        Is Parameter: {self.is_parameter}
        Is Member Of: {self.is_member_of}
        Same As: {self.same_as}
        Hash ID: {self.hash_id}
        Is Used: {self.is_used}
        Cluster ID: {self.cluster_id}
        Is Banned: {self.is_banned}
        """
        return description_str.strip()


class AllocateInfo:
    def __init__(self, _line_info, _is_deallocated):
        self.line_info = _line_info
        self.is_deallocated = _is_deallocated
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(line_info={self.line_info} is_deallocated={self.is_deallocated})"

