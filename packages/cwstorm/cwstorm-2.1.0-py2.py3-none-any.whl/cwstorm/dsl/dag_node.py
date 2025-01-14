import re
from cwstorm.dsl.node import Node
from cwstorm.dsl.cmd import Cmd

VALID_NAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\-]*$")
NAME_NUMBER_PADDING = 5

STATUSES = ["holding", "open", "running", "canceled", "succeeded", "failed", "incomplete", "completed"]

class DagNode(Node):
    """
Abstract base class nodes that can appear in the DAG graph.

This class maintains unique naming for each instance and provides functionality to manage DAG-specific properties and relationships such as parents, children, and instance tracking.

The `step` and `order` properties of the coords attribute are used as hints for laying out nodes in a visual graph. They represent semantic coordinates. The Cytoscape layout plugin [storm-layout](https://github.com/ConductorTechnologies/storm-layout) uses these attributes to position nodes in a graph so that they bear some relation to the intent of the original author. They are not required, and any graph layout tools should provide a fallback, such as Klay or Dagre, if these attributes are not present.

See the [README](https://github.com/ConductorTechnologies/cwstorm/blob/master/README.md) for more information.
    """


    BASE_ATTRS = {
        "status": {
            "type": "str",
            "validator": re.compile(f"^({'|'.join(STATUSES)})$"),
            "default": "holding",
            "description": "Whether the node should start when all it's inputs are complete, or be held and wait for manual approval to unhold.",
        },
        "metadata": {
            "type": "dict",
            "description": "Arbitrary metadata that can be used for filtering and so on.",
        },
        "coords": {
            "type":  "dict",
            "default": {"step": -1, "order": -1},
            "validator": {"keys": ["step", "order"]},
            "description": "A hint for the graph layout algorithm to place the node in a specific position.",
        },
    }
    ATTRS = {}
    ORDER = 10

    instances = {}  # Class dictionary to hold instances
    name_counter = {}  # Dictionary to keep track of class_name and number

    @classmethod
    def reset(cls):
        """Reset the class dictionary and name counter."""
        cls.instances.clear()
        cls.name_counter.clear()

    @classmethod
    def _resolve_name(cls, name=None, **kwargs):
        """Resolve the name."""

        proposed_name = name or kwargs.get("name")
        if proposed_name is None:
            class_name = cls.__name__
            cls.name_counter.setdefault(class_name, 0)
            counter = cls.name_counter[class_name]
            name = cls.format_name(class_name, counter)
            cls.name_counter[class_name] += 1
            return name

        if proposed_name not in cls.instances:
            return proposed_name

        base_name = proposed_name.split("_")[0]
        counter = 1
        while True:
            new_name = cls.format_name(base_name, counter)
            if new_name not in cls.instances:
                return new_name
            counter += 1

    @classmethod
    def format_name(cls, base_name, counter):
        """Format the name with the counter and pad the numeric part."""
        return f"{base_name}_{str(counter).zfill(NAME_NUMBER_PADDING)}"

    def __init__(self, name=None, **kwargs):
        """
        Initialize a DagNode instance.

        Args:
            name (str): The name of the node.
            **kwargs: Additional keyword arguments corresponding to the attributes defined in ATTRS.
        """
        self._name = self._resolve_name(name, **kwargs)

        self.instances[self._name] = self  # Add instance to class dictionary

        self.parents = []
        self.children = []

        super().__init__()
        self._initialize_attributes(**kwargs)

    def _initialize_attributes(self, **kwargs):
        """Initialize the attributes from kwargs."""
        for attr, properties in self.ATTRS.items():
            datatype = properties["type"]
            value = kwargs.get(attr, properties.get("default"))
            if value is None:
                continue
            if datatype == "Cmd":
                self.__getattribute__(attr)(Cmd(*value["argv"]))
            elif datatype == "list:Cmd":
                cmdlist = [Cmd(*cmd["argv"]) for cmd in value]
                self.__getattribute__(attr)(*cmdlist)
            elif datatype.startswith("list:"):
                self.__getattribute__(attr)(*value)
            else:
                self.__getattribute__(attr)(value)



    def add(self, *children):
        """Add children if not already added."""
        for child in children:
            if child not in self.children:
                self.children.append(child)
                if self not in child.parents:
                    child.parents.append(self)
        return self

    def name(self):
        """Get the name of the node."""
        return self._name

    def __str__(self):
        return self._name

    def is_leaf(self):
        return not self.children

    def is_root(self):
        return not self.parents

    def count_descendents(self):
        visited = set()

        def dfs_descendents(node):
            visited.add(node.name())
            for child in node.children:
                if child.name() not in visited:
                    dfs_descendents(child)

        dfs_descendents(self)
        return len(visited) - 1

    def count_ancestors(self):
        visited = set()

        def dfs_ancestors(node):
            visited.add(node.name())
            for parent in node.parents:
                if parent.name() not in visited:
                    dfs_ancestors(parent)

        dfs_ancestors(self)
        return len(visited) - 1

    def is_original(self, parent=None):
        """True if the parent is the first parent or there are no parents."""
        return not parent or not self.parents or self.parents[0] == parent

    def is_reference(self, parent):
        """True if the parent is a parent and not the first parent."""
        return (
            parent
            and len(self.parents) > 1
            and parent != self.parents[0]
            and parent in self.parents
        )

    @classmethod
    def validate_name(cls, name):
        if not isinstance(name, str):
            raise TypeError("name() argument must be a string")
        if not VALID_NAME_REGEX.match(name):
            raise ValueError(f"name() argument must match {VALID_NAME_REGEX.pattern}")
        return True

    def __iter__(self):
        """Enable cast self to dict."""
        yield "name", self.name()
        for item in super().__iter__():
            yield item
