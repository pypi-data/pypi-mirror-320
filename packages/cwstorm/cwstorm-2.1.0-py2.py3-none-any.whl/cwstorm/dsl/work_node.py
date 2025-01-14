import re
from cwstorm.dsl.dag_node import DagNode



class WorkNode(DagNode):
    
    """
Abstract base class nodes that do some work.

Work nodes. Tasks, and integrations are work nodes. The job node is not a work node.
    """
    BASE_ATTRS = {}
    ATTRS = {}
    ORDER = 25
