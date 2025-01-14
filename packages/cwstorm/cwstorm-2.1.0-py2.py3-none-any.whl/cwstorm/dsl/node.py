from cwstorm.dsl.node_metaclass import NodeMeta
# from cwstorm.dsl.cmd import Cmd

class Node(object, metaclass=NodeMeta):
    """
Abstract base class for serializeable entities.

Subclasses should specify the attributes to be serialized in a class attribute called ATTRS. This is a dict, keyed by attribute name, with values specifying the attribute type and additional validation constraints.

The type is specified as a string, with the following options:

* **bool** -A boolean
* **str** - A string
* **int** - An integer
* **dict** - A dictionary
* **Cmd** - A Cmd object
* **list:str** - A list of strings
* **list:int** - A list of integers
* **list:dict** - A list of dictionaries
* **list:Cmd** - A list of Cmd objects

Validations depend on the type. For strings, the validator is a regular expression. For ints, the min and max values are specified.

The node metaclass generates a setter/getter for each attribute. This keeps the class definition easy to read and maintain.
    """
    ORDER = 0
    BASE_ATTRS = {}
    ATTRS = {}
 
  
    @property
    def __dict__(self):
        # Include all ATTRS with their current or default values
        result = {key: getattr(self, key)() for key in self.ATTRS.keys() if getattr(self, key)() is not None}
        return result

    def __iter__(self):
        """Enable casting self to dict.

        The dict contains the node's attributes, as specified in ATTRS, and their values. It does not contain attributes whose values are None or empty.
        """
        yield "type", self.__class__.__name__.lower()
        for key, kwargs in self.ATTRS.items():
            value = getattr(self, key)()

            # Skip empty values unless they have a default
            if value is None or value == [] or value == {}:
                if 'default' not in kwargs:
                    continue
                value = kwargs['default']

            # Cast Cmd objects as dicts. Their own __iter__ method will handle the rest.
            if isinstance(value, list):
                if all(type(x).__name__ == "Cmd"  for x in value):
                    value = [dict(x) for x in value]
            elif type(value).__name__ == "Cmd":
                value = dict(value)

            yield key, value

    @classmethod
    def validate_int(cls, name, *args, **kwargs):
        """Validate an int argument."""
        for arg in args:
            if not type(arg).__name__ == "int":
                raise TypeError("Value '{}' for '{}' must be an int".format(arg, name))
            if "validator" in kwargs:
                if "min" in kwargs["validator"] and arg < kwargs["validator"]["min"]:
                    raise ValueError(
                        "Value '{}' for '{}' must be at least '{}'".format(
                            arg, name, kwargs["validator"]["min"]
                        )
                    )
                if "max" in kwargs["validator"] and arg > kwargs["validator"]["max"]:
                    raise ValueError(
                        "Value '{}' for '{}' must be at most '{}'".format(
                            arg, name, kwargs["validator"]["max"]
                        )
                    )

    @classmethod
    def validate_string(cls, name, *args, **kwargs):
        """Validate a string argument."""
        for arg in args:
            if not type(arg).__name__ == "str":
                raise TypeError(
                    "Value '{}' for '{}' must be a string".format(arg, name)
                )
            if "validator" in kwargs and not kwargs["validator"].match(arg):
                raise ValueError(
                    "Value '{}' for '{}' must match {}".format(
                        arg, name, kwargs["validator"]
                    )
                )

    @classmethod
    def validate_cmd(cls, name, *args, **kwargs):
        """Validate a Cmd argument."""
        for arg in args:
            if not type(arg).__name__ == "Cmd":
                raise TypeError(
                    "Value '{}' for '{}' must be type Cmd".format(repr(arg), name)
                )
        # No need to validate command format here as it is done when the
        # command is instantiated.

    @classmethod
    def validate_dict(cls, name, *args, **kwargs):
        """Validate a dict argument."""
        for arg in args:
            if not type(arg).__name__ == "dict":
                raise TypeError("Value '{}' for '{}' must be a dict".format(arg, name))
        if "validator" in kwargs:
            valid_keys = kwargs["validator"]["keys"]
            for arg in args:
                for key in arg:
                    if key not in valid_keys:
                        raise ValueError(
                            "Key '{}' in '{}' must be one of {}".format(
                                key, name, valid_keys
                            )
                        )

    @classmethod
    def validate_bool(self, name, *args, **kwargs):
        """Validate a bool argument."""
        for arg in args:
            if not type(arg).__name__ == "bool":
                raise TypeError("Value '{}' for '{}' must be a bool".format(arg, name))
          