def generate_dict_key(el_types, el_dimensions, el_intent=None, uniform_intent=None):
    import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
    import hashlib
    # Create a key agnostic on the real type
    el_types = el_types[:]
    if uniform_intent == 'all':
        # Perform a copy not to modify the args in input
        for index, t in enumerate(el_types):
            if t in list(VariablePrecision.real_id) + ["rpe_var"]:
                el_types[index] = "uniform_real"
    elif uniform_intent == 'in':
        # Perform a copy not to modify the args in input
        for index, i in enumerate(el_intent):
            if i == 'in' and el_types[index] in list(VariablePrecision.real_id) + ["rpe_var"]:
                el_types[index] = "uniform_real"
    # Now substitute the value of wp with the real val
    el_types = el_types[:]
    for index, t in enumerate(el_types):
        if t == 'wp':
            el_types[index] = VariablePrecision.value_of_working_precision['wp']

    key = [str(len(el_types))] + el_types + [str(ed) for ed in el_dimensions]
    string_to_hash = "".join([k for k in key])
    hash_object = hashlib.md5(string_to_hash.encode())
    return hash_object.hexdigest()


class Interface:
    def __init__(self, _name, module, is_abstract=False):
        self.name = _name
        self.module = module
        self.subprogram = []
        self.agnostic_key = {}
        self.is_abstract = is_abstract

    #
    def __getitem__(self, item):
        for subprogram in self.subprogram:
            if subprogram.name == item:
                return subprogram

    @property
    def key(self):
        ret_val = {}
        for module_procedure in self.subprogram:
            mandatory_da_type = [da.type for da in module_procedure.mandatory_da]
            mandatory_da_dim = [da.dimension for da in module_procedure.mandatory_da]
            key = generate_dict_key(mandatory_da_type, mandatory_da_dim)
            ret_val[key] = module_procedure.name
        return ret_val

    def generate_key(self):
        # Just in case that we have to regenerate the key, empty the dict
        self.agnostic_key['all'] = {}
        self.agnostic_key['in'] = {}
        for module_procedure in self.subprogram:
            mandatory_da_type = [da.type for da in module_procedure.mandatory_da]
            mandatory_da_dim = [da.dimension for da in module_procedure.mandatory_da]
            mandatory_da_intent = [da.intent for da in module_procedure.mandatory_da]
            # key = generate_dict_key(mandatory_da_type, mandatory_da_dim)
            agnostic_key_all = generate_dict_key(mandatory_da_type, mandatory_da_dim,
                                                 el_intent=mandatory_da_intent, uniform_intent='all')
            # This is needed in post processing phase, when just intent out/inout intent have to be coherent
            agnostic_key_in = generate_dict_key(mandatory_da_type, mandatory_da_dim,
                                                el_intent=mandatory_da_intent, uniform_intent='in')
            # Create a unique key from interface argument starting from attribute
            try:
                # This key will store sp/dp version of interface
                self.agnostic_key['all'][agnostic_key_all] += [module_procedure.name]
            except KeyError:
                self.agnostic_key['all'][agnostic_key_all] = [module_procedure.name]
            try:
                # This key will match when cast on output args are needed
                self.agnostic_key['in'][agnostic_key_in] += [module_procedure.name]
            except KeyError:
                self.agnostic_key['in'][agnostic_key_in] = [module_procedure.name]

    def add_module_procedure(self, subprogram):

        self.subprogram.append(subprogram)
        # Don't know it will be useful yet
        if not subprogram.interface:
            subprogram.interface = self
        elif isinstance(subprogram.interface, list):
            subprogram.interface.append(self)
        else:
            subprogram.interface = [subprogram.interface, self]

    def get_module_procedure(self, mp_name):
        return [mp for mp in self.subprogram if mp.name == mp_name][0]
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"