# Store patterns that are used frequently along the code

# REAL AND INTEGER VARIABLES
# Captures a real number with precision specification: 0.5_dp / 0_sp
real_number_with_precision = r"[0-9\.]+(_([a-zA-Z]+))"
integer_number_with_precision = r"^[0-9\.]*_\d+$"
# Pattern for numbers in exponential form: a - 1.e-20_wp + b group 2 will be 1.e-20_wp
number_exp_DPE_notation = r'(\W|^)(\d+\.?\d*[e|d][+|-]*\d+(_\w+)?)(\W|$)'
# Pattern for numbers with exponentiation, var**2
number_exponentiation = r'\*\*\s*\w+(\.\d*|_\w+)*'

# Unary operator, i.e. +/- when preceding a variable
unary_operator = r'^\s*[\+\-]'

#### VARIABLE
variable = r"^\w+$"
name_occurrence = r'\s*\b%s\b'

#### ARRAY
# Matches simple array, and sliced array
array = r"\w+\s*\(\s*[\w,:\d\s+\-\*]+\s*\)"
match_array_brackets = r"\w*\s*(\(\s*[\w,:\d\s+\-\*=]+\s*\))"
# array(:)%b
array_with_member = array + r"%\w+"
#  array(:)%b(:)
array_with_array_member = array + "%" + array

# Match with key word argument
key_word_argument = r"^[^()'\"=]*=[^=]"

###### STRUCTURE
# Simple multilayer strucure a%b%c%... keeping into account that @ can be present due to masking of arrays
structure = r"[\w|@]+(?:%[\w|@]+)+"
# Simple structure with array member a%b(:)
structure_with_member_array = r"\w+%" + array

# Matches with the (/old, style, vec /) or the new [array, style]
# hardcoded_array = r"(\(\/|\[)(\s*[\w\s,%.()\+\-=*]*\s*)(\/\)|\])"
hardcoded_array = r"\s*(\(\/|\[)(.*)(\/\)|\])"
hardcoded_array_parenthesis = r"\s*(\(\/)(.*)(\/\))"
hardcoded_array_brackets = r"\s*(\[)(.*)(\])"
# In write statement there can be a statement like
# WRITE(numout,9402) jj, (ilci(ji,jj), ilcj(ji,jj),ji=il1,il2)
# the second argument has the type of the first el of the array
array_in_write_statement = r"^\s*\([\s\w,\(\):]+=[\s\w,\(\):]+\)"

loop = r',\s*\w+\s*=\s*\d+\s*,'
do_loop = r'^ *do *[\w]* *='
end_do_loop = r"^ *end\s*do"

#### DECLARATION
# Variables declaration
variable_declaration = r"(.*)::(.*)"

# Old parameter declaration that need to be changed to f90
parameter_77style_declaration = r'^\s*PARAMETER\s*\(\s*[\w+=\s*]'


# TYPE
# type(rpe) declaration with assignation
rpe_parameter_declaration = r'^.*type\(rpe_var\).*::.*='

# Given a name match the type declared with this name
type_name_begin = r'\btype\b.*\b%s\b'

# Captures simple types declaration
type_declaration = r'^\s*\btype(,|)(?!\().*(::|)\s+(\w+)'
# simple_type_declaration = r"^ *type[^()]*[ \t](\w+) *$"
# # Captures just types declaration with extended the attribute
# extended_type_declaration = r"^ *type\s*,(\s*public\s*,|)\s*extends *\(\s*(\w*) *\) *:: * (\w*)"
# # Captures type with possible public and extended attributes
# general_type_declaration = r'^ *type\s*(,|)\s*(public\s*::|public|)\s*(,|)\s*(extends\((\w*)\)\s*::|) * (\w*)'
# Captures end of groups
end_type_statement = r"^\s*END TYPE"

# ASSIGNATION
# Captures the variable and value of an assignation
assignation_val = r"^([^\!]*)=([^\!]*)"
# Assignation via 'data' statement
data_statement_assignation = r"^\s*data\b\s*(\b\w+\b) .*"

# Array of strings init
# Captures strings like --> axis = [character(len=256) :: 'T', 'Z', 'Y', 'X']
string_array_initialization = r'\s*\[character.*::.*\]'


# REAL (Can be a variable declaration, or a function ret_val specification)

# All the lines that declare a real
# real(wp/sp/dp/[...]) :: var
# real_with_precision_declaration = r'(real\s*\(\s*(KIND\s*=\s*|)\w+\s*\))\s*(,\s*\w+\s*\([^)]*\)\s*)*(::|function)'
real_with_precision_declaration = (
    r'(real\s*'  # Match the keyword 'real'
    r'(?:\(\s*(?:KIND\s*=\s*|)(\w+)\s*\))?)'  # Match and capture KIND or precision
    r'\s*(?:,\s*\w+\s*(?:\((?:[^\(\)]|\([^)]*\))*\))?\s*)*'  # Match optional attributes with nested parentheses
    r'::'  # Match ::
)

# [...] :: var_name => group 1 = "::/FUNCTION"; group 2 = "var_name"
real_with_precision_declaration_name = r'(::|FUNCTION)\s*\b(\w+)\b'
# real :: var
# REAL((kind=)dp/sp/wp) => group(3) == dp/sp/wp
precision_of_real_declaration = r'real\s*\(\s*((kind\s*=|)\s*(\w+))\s*\)'

# Variables declared with traditional style without ::
traditional_declaration_pattern = (
    r'^\s*\b(real|integer|logical|character)\b\s*'  # Match the data type with word boundaries
    r'(\(.*?\))?\s*'                               # Match optional kind or len (e.g., "(kind=8)", "(len=255)")
    r'(,\s*dimension\(.*?\))?\s*'                  # Match optional dimension attribute
    r'(\w.*)$'                                     # Match variable names (with optional parentheses for indexing)
)


# POINTER

# Captures when a pointer is assigned on a line and gives back
# - group 0 => eventual ptr attributes
# - group 2 => ptr
# - group 3 => target
pointers_assignation = r"(.*::|)\s*(.*)=>\s*(.*)"


# SUBPROGRAM

function_declaration = r'function\b(?!(?<=\bend function)\s*)\s+(\w+)'
end_function_declaration = r'^\s*end\s*function'
function_precision_declaration = precision_of_real_declaration + r'\s+FUNCTION'
# - group 1 => subprogram type
# - group 2 => subprogram name
subprogram_declaration = r'(subroutine|function)\s+(\w+)\s*\(.*\)'
subroutine_declaration = r'subroutine\b(?!(?<=\bend subroutine)\s*)\s+(\w+)'
subprogram_name_declaration = r"((subroutine|function) +\b)%s\b"
subprogram_name_end_declaration = r"(end\s+(subroutine|function)\s+\b)%s\b"

# CALL
# (?![0-9])[a-z0-9_]+): Match for alphanumeric string with negative lookahead for only numbers
call_to_function = r"(?<!subroutine )(?<!call )[+-]*(\b(?!\d)\w+)\s*\("
call_to_function_masked = r"(?<!subroutine )(?<!call )[+-]*\b[A-Z0-9]+@([A-Z0-9]+)\s*\("
call_to_subroutine = r"^\s*call\s+(\w+)"
call_to_function_name = r'(?<!subroutine )(?<!call )[+-]*(\b%s\b)\s*\('
call_to_subroutine_name = r'^\s*call\s+%s\b'
assignation_to_DT = r"(\w+) *\("

# CALL to READ
call_to_read = r'^\s*(\bread\b\s*\(.*)'

# Allocation
allocation_variable_name = r"\ballocate\b\s*\(.*\b%s\b.*"
allocation_member_name = r"\ballocate\b\s*\(.*(?<=%%)\b%s\b.*"
deallocation_variable_name = r"\bdeallocate\b\s*\(.*\b%s\b.*"
deallocation_member_name = r"\bdeallocate\b\s*\(.*(?<=%%)\b%s\b.*"
general_allocation = r'\ballocate\b\s*\(.*'

# PURE function
pure_function_declaration = r"\s*(\bpure)\s+(function)\s*"

# Reshape:
# - group 0 => The entire call
# - group 1 => the hardcoded array being reshaped
reshape_function = r'RESHAPE\s*\(\s*(\(\/(.*)\/\))\s*,\s*\(\s*\/(.*)\/\)\s*\)'

# Use statement
use_statement = r'(?<!\w)use\s'

# Assignation like a = b
# - group 0 a =
# - group 3 b
assignation = r'(^\s*\w+(\(.*\))*\s*=)\s*(.*)'

# Identify the cast introduced for mixed precision purpose
CAST = r'CAST(SP|DP)'


def escape_string(string: str, strict: bool=True):
    """
    Escapes a given string to make it compatible with regular expressions.
    The function ensures that special characters like "+", "-", "*", and "."
    are escaped, and that word boundaries are added where appropriate.
    Additionally, it can apply stricter conditions to avoid matching certain
    structures or patterns (like names followed by parentheses or arrays).

    Parameters:
        string (str): The string to escape.
        strict (bool): Whether to apply strict escaping (default is True).

    Returns:
        str: The escaped string suitable for use in regular expressions.
    """
    import re
    escaped_string = string
    # In case string does start with a char we'll add the \b to indicate a word border
    if re.match(r"\w", escaped_string.strip()[0]):
        escaped_string = r'\b' + escaped_string.strip()

    # Escape operation signs that means something in  regex patterns
    escaped_string = escaped_string.replace("+", r"\+")
    escaped_string = escaped_string.replace("-", r"\-")
    escaped_string = escaped_string.replace("*", r"\*")
    # For floating point numbers
    escaped_string = escaped_string.replace(".", r"\.")
    if escaped_string.count("("):
        escaped_string = escaped_string.replace("(", r"\s*\(")
        escaped_string = escaped_string.replace(")", r"\)")
    # If the string is not ending with a symbol
    if re.match(r'\w', escaped_string.strip()[-1]):
        escaped_string += r"\b"
    if strict:
        # Avoid matching structures
        escaped_string = escaped_string + r"(?!%)"
        # Avoid substituting if name is followed by a bracket
        escaped_string = escaped_string + r"(?!\()"
        # Avoid bracket with space
        escaped_string = escaped_string + r"(?! \()"
    return escaped_string


def escape_deindexed_structures(string: str):
    """
    Modifies the provided string to handle structures with indexed members
    (i.e., using "%").
    The function adds the appropriate regular expression format for structures
    to ensure proper matching, including handling nested structures.

    Parameters:
        string (str): The string representing the structure to escape.

    Returns:
        str: The modified string suitable for use in regular expressions,
             accounting for structure members and indexing.
    """
    arguments = string.split("%")
    arguments[-1] = "%" + arguments[-1] + r"\b"
    arguments[0] = arguments[0] + r"[\w\( \),\d]*"
    return "".join(arguments)
