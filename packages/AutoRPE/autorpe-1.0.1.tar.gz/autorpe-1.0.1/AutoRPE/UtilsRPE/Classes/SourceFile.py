import AutoRPE.UtilsRPE.Error as Error


class SourceFile:
    def __init__(self, _filename, extension, lines=[], dictionary_of_masked_string=None):
        self.path = _filename
        self.filename = self.path.split("/")[-1]
        self.module_name = self.filename.replace(extension, "")
        self.lines = lines
        # h90 files included through #include clause
        self.header_files = []
        self.dictionary_of_definition = {}
        self.dictionary_of_masked_string = {} if dictionary_of_masked_string is None else dictionary_of_masked_string

    def read_file(self, _filename, no_strip):
        try:
            with open(_filename) as f:
                text = f.read()
                if not no_strip:
                    self.lines = [l.strip() for l in text.split("\n")]
                else:
                    self.lines = [l for l in text.split("\n")]
        except UnicodeDecodeError:
            raise Error.ExceptionNotManaged("The file %s contains non UTF-8 character.\n"
                                            " Please clean, and retry." % self.path)

    def update_module_lines(self):
        old_lines = self.lines[:]
        self.lines = []
        for line in old_lines:
            if line.count("\n"):
                self.lines.extend(line.split("\n"))
            else:
                self.lines.append(line)

    def get_text(self):
        """Create a single string to be dumped to file"""
        return "\n".join(l for l in self.lines).strip()

    def unmaks_string(self):
        import AutoRPE.UtilsRPE.MaskCreator as MaskCreator
        import re
        # Start from first key stored (From python3.6 dictionaries are ordered items)
        for _index, _line in enumerate(self.lines):
            # Once a key is hit substitutes it
            if _line.count("@"):
                keys = re.findall(r'\b\w*@\w*', _line)
                for k in keys:
                    val = self.dictionary_of_masked_string[k]
                    self.lines[_index] = MaskCreator.unmask_from_dict(self.lines[_index], {k: val})

    def save_file(self, file_path=None):
        if file_path:
            path = file_path + "/" + self.filename
        else:
            path = self.path
        # Update text so as to save to disk the most updated version
        self.update_module_lines()
        self.unmaks_string()
        with open(path, "w") as output_file:
            output_file.write(self.get_text())

    def preprocess_header_file(self):
        import re
        import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions

        # Avoid including files more than once
        self.header_files = list(set(self.header_files))
        # Some header files include themselves, avoid infinite loop
        self.header_files = [f for f in self.header_files if f != self]

        for file in self.header_files:
            for line in file.lines:
                line = BasicFunctions.remove_comments(line)
                if re.search(r"#\s*define", line):
                    line = line.split("define")[1]
                    defined_function = re.search(r'\w+\(', line, re.I)
                    if defined_function:
                        # Store definition without indexing
                        defined_function = BasicFunctions.close_brackets(line)
                        function_definition = line.replace(defined_function, "")
                    else:
                        defined_function = re.search(r'\w+', line, re.I).group()
                        function_definition = line.replace(defined_function, "")
                    try:
                        self.dictionary_of_definition[defined_function.strip()] += [function_definition.strip()]
                    except KeyError:
                        self.dictionary_of_definition[defined_function.strip()] = [function_definition.strip()]
