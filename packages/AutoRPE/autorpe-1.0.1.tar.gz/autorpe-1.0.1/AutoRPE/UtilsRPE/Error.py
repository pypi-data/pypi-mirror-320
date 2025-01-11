from argparse import ArgumentTypeError as err
import os


class PathType(object):
    """
    Validates file, directory, or symlink paths based on existence, type, and special cases
    like "-" for stdin/stdout.

    Attributes:
        exists (bool or None): Path existence condition.
        type (str or callable): Path type ('file', 'dir', 'symlink', or callable).
        dash_ok (bool): Whether "-" is allowed for stdin/stdout.

    Methods:
        __call__(self, string): Validates the given path string.
    """
    def __init__(self, exists=True, type='file', dash_ok=True):
        '''exists:
                True: a path that does exist
                False: a path that does not exist, in a valid parent directory
                None: don't care
           type: file, dir, symlink, None, or a function returning True for valid paths
                None: don't care
           dash_ok: whether to allow "-" as stdin/stdout'''

        assert exists in (True, False, None)
        assert type in ('file', 'dir', 'symlink', None) or hasattr(type, '__call__')

        self._exists = exists
        self._type = type
        self._dash_ok = dash_ok

    def __call__(self, string):
        if string == '-':
            # the special argument "-" means sys.std{in,out}
            if self._type == 'dir':
                raise err('standard input/output (-) not allowed as directory path')
            elif self._type == 'symlink':
                raise err('standard input/output (-) not allowed as symlink path')
            elif not self._dash_ok:
                raise err('standard input/output (-) not allowed')
        else:
            e = os.path.exists(string)
            if self._exists == True:
                if not e:
                    raise err("path does not exist: '%s'" % string)

                if self._type is None:
                    pass
                elif self._type == 'file':
                    if not os.path.isfile(string):
                        raise err("path is not a file: '%s'" % string)
                elif self._type == 'symlink':
                    if not os.path.symlink(string):
                        raise err("path is not a symlink: '%s'" % string)
                elif self._type == 'dir':
                    if not os.path.isdir(string):
                        raise err("path is not a directory: '%s'" % string)
                elif not self._type(string):
                    raise err("path not valid: '%s'" % string)
            else:
                if self._exists == False and e:
                    raise err("path exists: '%s'" % string)

                p = os.path.dirname(os.path.normpath(string)) or '.'
                if not os.path.isdir(p):
                    raise err("parent path is not a directory: '%s'" % p)
                elif not os.path.exists(p):
                    raise err("parent directory does not exist: '%s'" % p)

        return string


# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions."""
    pass


class SplitElementError(Error):
    """Raised when the split_element function does not split the element."""
    pass


class ValueTooSmallError(Error):
    """Raised when the input value is too small."""
    pass


class ValueTooLargeError(Error):
    """Raised when the input value is too large."""
    pass


class LineNotFound(Error):
    """Line you were searching for in file could not be found."""
    pass


class PointerTarged(Error):
    """Pointer and corresponding target types do not coincide."""
    pass


class ProcedureNotFound(Error):
    """The procedure you were searching for in vault could not be found."""
    pass


class InterfaceNotFound(Error):
    """The Interface you were searching for in vault could not be found."""
    pass


class DimensionNotFound(Error):
    """The dimension of the argument you were searching for in vault could not be found."""
    pass


class HardcodedRealWithoutPrecision(Error):
    """The hardcoded real does not have precision specification."""


class MemberNotFound(Error):
    """Structure member not found."""


class DerivedTypeNotFound(Error):
    """Derived type not found."""


class VariableNotFound(Error):
    """Variable not found in vault."""


class ModuleNotFound(Error):
    """Module not found in vault."""


class ExternalTypeUsed(Error):
    """External Derived type is used."""


class TypeOfContent(Error):
    """The function find type of error failed."""


class IsNotAnArray(Error):
    """Passed string is not an array."""


class DuplicatedObject(Error):
    """Found duplicated object, this should not happen. Check is needed."""


class ExceptionNotManaged(Error):
    """Found duplicated object, this should not happen. Check is needed."""


class IntentOutError(Error):
    """A variable was declared with an intent, but is used with a different one. Fix is needed."""


class ClusterCantBeDivided(Error):
    """A job failed on a leaf, and can not be subdivided anymore."""


class SubprogramNotFound(Error):
    """A subprogram name have not been found, probably \"end subroutine\" without the name. Fix is needed."""
