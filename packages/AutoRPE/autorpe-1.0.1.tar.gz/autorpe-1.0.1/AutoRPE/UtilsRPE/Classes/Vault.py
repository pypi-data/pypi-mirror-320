from collections import defaultdict
from AutoRPE.UtilsRPE.logger import logger, clean_line
import AutoRPE.UtilsRPE.Classes.Procedure as Procedure
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.Classes.Interface as Interface
import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.ObtainSourceFileInfo as ObtainSourceFileInfo
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.preprocess.Preprocessor as Preprocessor
import AutoRPE.UtilsRPE.TrackDependency as TrackDependency
import AutoRPE.UtilsRPE.SourceManager as SourceManager
import AutoRPE.UtilsRPE.Error as Error
from AutoRPE.UtilsRPE.Classes.CaseInsensitiveUtils import CaseInsensitiveDictionary, CaseInsensitiveList

def load_vault(path):
    import pickle
    try:
        return pickle.load(open(path, "rb"))
    except IOError:
        return None


def create_database(path_to_sources, extension=".f90"):
    # Initialize an empty database
    vault = Vault()
    # Load all the files in the provided path with extension
    file_list = BasicFunctions.load_sources(path_to_sources, extension)

    # Removes comment and join split lines
    Preprocessor.clean_sources(file_list)
    # Fill database with info from input files
    ObtainSourceFileInfo.parse_sources(file_list, vault, extension)
    # Fill "same_as" properties of variables, i.e. the list of variables that are not independent
    TrackDependency.propagate_dependencies(vault, "var_dependency")

    return vault


class Vault:
    def __init__(self):
        self.modules = {}
        self.variables = CaseInsensitiveList()
        self.variables_dictionary = {}
        self.block_dictionary = defaultdict(dict)
        self.interfaces_dictionary = {}
        self.dictionary_of_calls = defaultdict(list)
        self.derived_types = CaseInsensitiveList()
        self.variables_hash_table = {}
        self.indexed_variables = {}

    def add_block(self, block, add_var=True):
        block_name_type = type(block).__name__
        if block_name_type not in self.block_dictionary.keys():
            self.block_dictionary[block_name_type] = CaseInsensitiveDictionary()
        try:
            self.block_dictionary[type(block).__name__][block.name] += [block]
        except KeyError:
            self.block_dictionary[type(block).__name__][block.name] = [block]

        # Interface's  variables have already been added
        if add_var:
            for variable in block.variables:
                try:
                    self.variables_dictionary[variable.name] += [variable]
                except KeyError:
                    self.variables_dictionary[variable.name] = [variable]

    def get_block_list(self, only_class=None, exclude_class=[]):
        import functools
        import operator
        ret_val = []
        if only_class is None:
            only_class = [v for v in self.block_dictionary.keys() if v not in exclude_class]
        for block_type in self.block_dictionary.keys():
            if block_type in only_class:
                # Convert dict_values obj to list
                ret_val.extend(list(self.block_dictionary[block_type].values()))

        # Return a flattened list
        return functools.reduce(operator.iconcat, ret_val, [])

    def add_scope_info(self):
        # Only functions and Subroutines have the scope for the moment
        only_class = ['Function', 'SubRoutine']
        block_list = self.get_block_list(only_class=only_class)
        # Cycle on the list and check which block declares subprograms
        for block in block_list:
            for declared_sbp in block.declares:
                # Retrieve the object
                declared_sbp = self.get_subprogram_by_name(declared_sbp, only_class)
                # Add the info about mother block to the scope
                declared_sbp.scope = block

    def index_variables(self):
        for variable in self.variables:
            if variable.id is not None:
                self.indexed_variables[variable.id] = variable

    def fill_hash_table(self):
        if not self.variables_hash_table:
            for variable in self.variables:
                self.variables_hash_table[variable.hash_id] = variable

    def get_variable_from_namelist_by_name(self, var_name, namelist):
        var = [var for var in self.variables if
               var.name.lower() == var_name.lower() and var.appears_in_namelist and namelist in var.appears_in_namelist]
        if len(var) > 0:
            return var[0]
        else:
            raise Error.VariableNotFound

    def get_variable_by_name(self, var_name, procedure):
        # Search just among the accessible variables
        try:
            private_variables = procedure.get_accessible_variable_by_name(var_name)

            if len(private_variables) == 1:
                return private_variables[0]
            # A variable has been declared both as global (procedure.name == main ) and as private procedure variable
            elif len(private_variables) > 1:
                # We check hierarchically
                try:
                    shadow_var = [v for v in private_variables if v in procedure.variables][0]
                except IndexError:
                    try:
                        shadow_var = [v for v in private_variables if v in procedure.module.variables][0]
                    except IndexError:
                        try:
                            shadow_var = [v for v in private_variables if v in procedure.module.accessible_var][0]
                        except IndexError:
                            raise Error.VariableNotFound
                
                clean_line()
                logger.warn("A global variable %s has been shadowed " % private_variables[0].name)
                return shadow_var
        except KeyError:
            try:
                # Search among all the variables stored in vault
                global_variables = self.variables_dictionary[var_name]
            except KeyError:
                raise Error.VariableNotFound
            # Just one var exists with this name
            if len(global_variables) == 1:
                return global_variables[0]
            elif len(global_variables) > 1:
                # A variable is used from a module indirectly imported

                var = [c for c in global_variables if c in procedure.module.indirect_accessible_var]
                if len(var) == 0:
                    raise Error.VariableNotFound(f"Variable {var_name} couldn't be found in {procedure.name}.")
                return var[0]

    def get_variable_by_id(self, var_id):
        # Purpose: Retrieve a variable by id
        return self.indexed_variables[var_id]

    def get_variable_by_info(self, var_name, var_procedure, var_module):
        var_hash = BasicFunctions.hash_from_list([var_name, var_procedure, var_module])
        return self.variables_hash_table[var_hash]

    def get_variable_from_hash(self, var_hash):
        return self.variables_hash_table[var_hash]

    def get_subprogram_by_name(self, subprogram_name,
                               block_type=None,
                               module=None):
        if block_type is None:
            block_type = self.block_dictionary.keys()
        # Purpose: Retrieve a subprogram by name
        for bt in block_type:
            block_dictionary = self.block_dictionary[bt]
            try:
                block = block_dictionary[subprogram_name]
                if module is not None and len(block) > 1:
                    block = [module.get_subprogram(subprogram_name)]
                return block[0]
            except KeyError:
                continue
        # The procedure hasn't been found in the dictionary with specified types
        raise Error.ProcedureNotFound("Procedure %s not found in procedure dictionary" % subprogram_name)

    def get_derived_type_constructor(self, item):
        try:
            return [dt for dt in self.derived_types if dt.name.lower() == item.lower()][0]
        except (IndexError, KeyError) as e:
            return None

    def add_module_use(self, module, use, indirect_accessible_mod):
        # Check this module contains "use" statement
        for mu in module.accessible_mod:
            # Exclude already visited nodes
            if mu not in indirect_accessible_mod + use:
                # Append this module to the list so it will be not visited twice
                indirect_accessible_mod.append(mu)
                # Recursively compute the list of accessible modules
                self.add_module_use(mu, use, indirect_accessible_mod)
        # return list of visited modules
        return indirect_accessible_mod

    def fill_indirect_accessible_mod(self):
        # Loop through the modules and deep search all the used modules
        for module in self.modules.values():
            # Store the property in the indirect_accessible_mod
            for use in module.accessible_mod:
                indirect_accessible_mod = []
                module.indirect_accessible_mod.extend(self.add_module_use(use,
                                                                          module.accessible_mod+module.indirect_accessible_mod,
                                                                          indirect_accessible_mod))

    def fill_sbp_variables_dict(self):
        """ Fill the info about accessible variables and fill the dictionary"""

        # Get list of subprograms
        subprograms = self.get_block_list(only_class=['Function', 'SubRoutine'])

        for sub in subprograms:
            list_of_accessible_variables = []
            if len(sub.use_only_variables):
                # Go through all the import statement
                for module in sub.use_only_variables:
                    # Add to the list just the imported variables
                    if module.count("only"):
                        used_var = module.split("only")[1].replace(":", "").strip()
                        used_module_name = module.split("only")[0].replace(",", "").strip()
                        for var in used_var.split(","):
                            used_module = self.modules[used_module_name]
                            variable = [v for v in used_module.variables if v.name == var.strip()]
                            if variable:
                                list_of_accessible_variables.append(variable[0])
                    else:
                        # Add all the variables, if the module is not external
                        try:
                            used_module = self.modules[module]
                            list_of_accessible_variables.extend(used_module.variables)
                        except KeyError:
                            continue
                # Add the variables imported from that module (some are duplicated)
                sub.use_only_variables = list(set(list_of_accessible_variables))

            # The info is complete, we can build the dictionary
            sub.fill_dictionary_of_variable()
            sub.fill_dictionary_of_accessible_var()

    def add_inheritance(self):
        import functools
        import operator

        # Fill the list of accessible modules looking at use statements
        self.fill_indirect_accessible_mod()

        # Add objects accessible through a use statement
        for module in self.modules.values():
            # Add global variables of the used modules
            accessible_variables = [um.variables for um in module.accessible_mod]
            # Add variable imported with use only statement
            accessible_variables.append([uo for uo in module.use_only])
            # Generate a single list and initialize the corresponding module property
            module.accessible_var = functools.reduce(operator.iconcat, accessible_variables, [])
            # Add public var of used modules to indirectly accessible var
            for indirect_accessible_mod in module.indirect_accessible_mod:
                if indirect_accessible_mod not in module.accessible_mod:
                    module.indirect_accessible_var.extend(indirect_accessible_mod.variables)

        # Loop through the list to see which modules use mine
        for module in self.modules.values():
            for mu in module.accessible_mod+module.indirect_accessible_mod:
                if module not in mu.used_by:
                    mu.used_by.append(module)

    def expand_derived_types(self):
        for derived_type in self.derived_types:
            if derived_type.extended_structure is not None:
                # Save mother structure in extension
                struct_to_extend = [s for s in self.derived_types if s.name == derived_type.extended_structure][0]
                struct_to_extend.extension = derived_type
                # Save extension the mother structure
                derived_type.extension = struct_to_extend
            # Now that everything is stored, we can fill the accessible variables
            derived_type.fill_dictionary_of_accessible_var()

    def store_external_data_structures(self):
        # Derived data types to avoid
        avoid_types = [dt.name.lower() for dt in self.derived_types] + ['char', 'character', 'integer', 'logical',
                                                                        'complex'] + [*VariablePrecision.real_id] + [
                          'rpe']

        # Stores names of external data type used in declarations
        # Use set() to avoid duplicates
        external_types = set(v.type for v in self.variables if v.type.lower() not in avoid_types)
        external_types = set(v.type for v in self.variables if v.type is not None and v.type.lower() not in avoid_types)

        # Store the external derived type along with the others
        for external_t in external_types:
            self.derived_types.append(Procedure.DerivedType(external_t, None, is_external=True))

    def generate_namelist_precisions(self, filename="namelist_precisions"):
        from os.path import abspath

        # Get the list of rpe variables that had an id assigned
        assigned_rpe_vars = [var for var in self.variables if var.id is not None]
        # The id sorts them alphabetically
        assigned_rpe_vars.sort(key=lambda x: x.id)
        line_text = "emulator_variable_precisions(%d) = %d\t! Variable:%24s\tRoutine:%22s\tModule:%16s\n"
        # Create a namelist with all variables set to double precision
        with open(filename, "w") as namelist:
            namelist.write("! namelist variable precisions\n&precisions\n")
            for var in assigned_rpe_vars:
                namelist.write(
                    line_text % (var.id, 52, var.name, var.procedure.name, var.procedure.module.name))
            namelist.write("/\n")
        print("\nNamelist written to " + abspath(filename))

    def remove_banned_variables(self, filename):
        banned_variables = SourceManager.load_variable_list(filename, vault=self)
        for var in banned_variables:
            var.is_banned = True
            for var_hash in var.same_as:
                v = self.get_variable_from_hash(var_hash)
                v.is_banned = True

    def set_cluster_id(self):
        # Variables have to enter the analysis and belonging to a cluster
        def condition(v):
            if v.type == 'rpe_var' and v.id is not None and v.is_used:
                if len([av for av in v.same_as if self.get_variable_from_hash(av).is_used]) > 1:
                    return True
            return False

        # Now divide variables by cluster
        cluster = []
        for var in self.variables:
            if condition(var):
                var.same_as.sort()
                if var.same_as not in cluster:
                    cluster.append(var.same_as)

        cluster.sort(key=lambda x: len(x))

        # Enumerate variables in clusters and assign a progressive id
        for cluster_id, uc in enumerate(cluster):
            cluster_variables = [self.get_variable_from_hash(h) for h in uc]
            for var in cluster_variables:
                if condition(var):
                    var.cluster_id = cluster_id

    def add_used_variables(self, filename):
        used_variables = SourceManager.load_variable_list(filename, vault=self, is_used=True)[0]
        for var in used_variables:
            if not var.is_banned:
                var.is_used = True
        # Set cluster id using is_used property
        self.set_cluster_id()

    def save(self, path):
        import sys
        from os.path import abspath
        import pickle
        # This workaround is needed to allow pickle to write the file, don't know yet about its risks
        sys.setrecursionlimit(10000)
        print("\nVault successfully dumped to ", abspath(path))
        pickle.dump(self, open(path, "wb"))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
