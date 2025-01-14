import logging


from cwstorm.dsl.job import Job
from cwstorm.dsl import factory

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Function to turn a dictionary containing nodes and edges back into a DAG graph
def deserialize(spec):
    nodes = {}
    job = None
    
    # Create nodes
    for node in spec["nodes"]:
        node = factory.get(node)
        if isinstance(node, Job):
            job = node
        nodes[node.name()] = node

    # Create edges
    for edge in spec["edges"]:
        source_node = nodes[edge["source"]]
        target_node = nodes[edge["target"]]
        target_node.add(source_node)

    return job
