from AutoRPE.UtilsRPE.Classes.Procedure import Procedure
import AutoRPE.UtilsRPE.Classes.Variable as Variable
import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile
import AutoRPE.UtilsRPE.Error as Error
from AutoRPE.UtilsRPE.Classes.CaseInsensitiveUtils import CaseInsensitiveList


class Module(SourceFile.SourceFile):
    def __init__(self, source_file, extension):
        super(Module, self).__init__(source_file.path, extension, source_file.lines,
                                     source_file.dictionary_of_masked_string)
        self.name = self.module_name
        self.main = Procedure("main", self)
        self.line_info = []
        self.variables = []
        self.subprogram = []
        self.accessible_mod = []
        self.indirect_accessible_mod = []
        self.use_only = []
        self.used_by = []
        self.accessible_var = []
        self.accessible_sbp = []
        self.indirect_accessible_var = CaseInsensitiveList()
        self.indirect_accessible_sbp = []

    def add_variable(self, _variable):
        assert isinstance(_variable, Variable.Variable)
        _variable.procedure = self
        self.variables.append(_variable)

    def update_lineinfo(self):
        """Add lines that have been inserted for truncation, update line index accordingly"""
        # Use old lines to update lineinfo
        old_lines = self.lines[:]
        new_index = 0
        new_line_info = []
        # Rebuild the text
        text = "".join([l + "\n" for l in self.lines[:]]).strip()
        # Update module lines so that line_info constructor can access the correct line
        self.lines = text.split("\n")
        # Update line info array: create new entry for all the lines that have been added
        for original_index, _line in enumerate(old_lines):
            split_count = _line.count("\n")
            if split_count:
                # All line's part belong to same block and have same loop depth, just a different line number
                for _i_line in _line.split("\n"):
                    new_line_info.append(LineInfo(new_index,
                                                  self.line_info[original_index].loop_depth,
                                                  self.line_info[original_index].block))
                    new_index += 1
            else:
                # Update line index in old obj
                self.line_info[original_index].line_number = new_index
                new_line_info.append(self.line_info[original_index])
                new_index += 1
        # Overwrite with new line info array
        self.line_info = new_line_info

    def create_block(self, vault):
        """For each line of the module store the "block", i.e. the object the procedure the line belongs to.
        A block can be: a subprogram definition or a data type declaration"""
        import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
        import re
        block_stack = [self.main]
        # Rebuild the text
        text = "".join([l.strip() + "\n" for l in self.lines[:] if l.strip()])
        # Now split the lines by marker
        self.lines = text.split("\n")
        loop_depth = 0
        for _index, _line in enumerate(self.lines):

            # Update the level stack in the array block_stack
            self.update_block_stack(block_stack, _line, vault)

            # Increment nesting index
            if re.search(RegexPattern.do_loop, _line, re.I):
                loop_depth += 1
            # Whenever a 'do loop' ends decrement nesting index
            # This way match bot the expression 'end do' and 'enddo' but excludes matches like 'enddo loop_name'
            elif re.search(RegexPattern.end_do_loop, _line, re.I):
                loop_depth -= 1

            # Store the line, line_index, loop_depth and block stack into an obj     
            self.line_info.append(LineInfo(_index, loop_depth, block_stack[-1]))

    def update_block_stack(self, block_stack, _line, vault):
        """block_stack contains the block we are in wrt main: main, inside a function, inside a nested function, etc"""
        import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
        import re

        _pattern = None
        # Declaration lines
        # Match standalone 'subroutine' or 'function'
        if re.search(r'\bsubroutine\b', _line, re.IGNORECASE):
            _pattern = RegexPattern.subroutine_declaration
            _group_idx = 1
        elif re.search(r'\bfunction\b', _line, re.IGNORECASE):
            _pattern = RegexPattern.function_declaration
            _group_idx = 1
        # Regex is needed here to avoid match like "END MODULE obs_types", and pop on an empty stack
        elif re.search(RegexPattern.name_occurrence % "type", _line, re.I):
            _pattern = RegexPattern.type_declaration
            _group_idx = 3
        # We are changing block
        if _pattern is not None:
            # We are exiting a block, get up one level in stack
            if _line.lower().find("end") == 0:
                block_stack.pop()
            # Entering a new block
            else:
                match = re.search(_pattern, _line, re.I)
                # Cases like variables names that contains "function" in it will not match
                if match:
                    block_name = match.group(_group_idx).strip()
                    current_block = self.get_block_by_name(block_name, vault)
                    if current_block is None:
                        raise Error.ProcedureNotFound
                    block_stack.append(current_block)

    def get_block_by_name(self, block_name, vault):
        # Purpose: Retrieve a block by name

        for bt in vault.block_dictionary.keys():
            block_dictionary = vault.block_dictionary[bt]
            try:
                block = block_dictionary[block_name]
                if len(block) > 1:
                    # this is safe until they start to define functions inside functions
                    return [b for b in block if b.module.name == self.name][0]

                return block_dictionary[block_name][0]
            except KeyError:
                continue

        return None

    def get_variable(self, var_name, procedure_name):
        try:
            var = [var for var in self.variables if var_name == var.name and procedure_name == var.procedure.name][0]
        except IndexError:
            raise Error.VariableNotFound("Variable %s from procedure %s in module %s not found" %
                                         (var_name, procedure_name, self.name))
        return var

    def get_subprogram(self, subprogram_name):
        ret_val = [s for s in self.subprogram if s.name == subprogram_name]
        if ret_val:
            if len(ret_val) > 1:
                raise Error.ExceptionNotManaged('Subprogram %s was declared twice, probably an error' % subprogram_name)
            return ret_val[0]
        else:
            for m in self.accessible_mod+self.indirect_accessible_mod:
                try:
                    ret_val = m.get_subprogram(subprogram_name)
                except Error.ProcedureNotFound:
                    continue
                if ret_val:
                    return ret_val

        raise Error.ProcedureNotFound

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class LineInfo:
    def __init__(self, index, loop_index, block):
        self.line_number = index
        self.block = block
        self.block_type = type(block).__name__
        self.loop_depth = loop_index

    @property
    def line(self):
        return self.block.module.lines[self.line_number]

    @property
    def if_condition(self):
        import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
        if_condition, _ = BasicFunctions.remove_if_condition(self.line, True)
        return if_condition
        
    @property
    def unconditional_line(self):
        import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
        return BasicFunctions.remove_if_condition(self.line)
