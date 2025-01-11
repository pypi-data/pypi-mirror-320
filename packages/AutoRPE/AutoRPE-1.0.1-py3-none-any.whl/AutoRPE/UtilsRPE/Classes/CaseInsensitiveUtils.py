import warnings
from AutoRPE.UtilsRPE.logger import logger, clean_line


class CaseInsensitiveDictionary:
    def __init__(self, *args, **kwargs):
        self._data = {}
        self._original_keys = {}
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        lowercase_key = key.lower()
        if lowercase_key in self._data:
            original_key = self._original_keys[lowercase_key]
            if key != original_key:
                logger.warn(f"Accessing key '{key}' instead of original key '{original_key}'")
            return self._data[lowercase_key]
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        lowercase_key = key.lower()
        self._data[lowercase_key] = value
        self._original_keys[lowercase_key] = key

    def __delitem__(self, key):
        lowercase_key = key.lower()
        del self._data[lowercase_key]
        del self._original_keys[lowercase_key]

    def __contains__(self, key):
        return key.lower() in self._data

    def get(self, key, default=None):
        return self._data.get(key.lower(), default)

    def setdefault(self, key, default=None):
        lowercase_key = key.lower()
        if lowercase_key not in self._data:
            self._data[lowercase_key] = default
            self._original_keys[lowercase_key] = key
        return self._data[lowercase_key]

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def keys(self):
        return [self._original_keys[key] for key in self._data.keys()]

    def items(self):
        return [(self._original_keys[key], value) for key, value in self._data.items()]

    def values(self):
        return self._data.values()

    def __repr__(self):
        return str({self._original_keys[key]: value for key, value in self._data.items()})

    def __len__(self):
        return self._data.__len__()
    

class CaseInsensitiveList(list):
    """
    Class to a store a list for which the __cointains__ method has been overloaded to behave as case insensitive.
    """
    def __contains__(self, item):
        for element in self:
            if isinstance(element, str) and isinstance(item, str):
                if item.lower() == element.lower():
                    return True
            else:
                if item == element:
                    return True
        return False
