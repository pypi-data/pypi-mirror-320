"""
This module provides serialization functionality for nodes and their relationships.

It includes methods to convert a graph of nodes into a dictionary format suitable storage or transport over a network.
"""
def serialize(node):
    """
    Serialize a node and its children into a dictionary containing 'nodes' and 'edges'.

    Args:
        node (Node): The root node to serialize.

    Returns:
        dict: A dictionary with two keys, 'nodes' and 'edges'. Each key maps to a list of serialized nodes and edges respectively.
    """
    
    elements = _serialize(node)
    result = {"nodes": [], "edges": []}
    for el in elements:
        if el.get("type") == "edge":
            result["edges"].append(el)
        else:
            result["nodes"].append(el)
    return result


def _serialize(node):
    """
    Recursively serialize a node and its children into a list of elements.

    Each element is a dictionary representing either a node or an edge. Nodes are represented 
    by their attributes, while edges indicate parent-child relationships between nodes.

    Args:
        node (Node): The node to serialize.

    Returns:
        list: A list of dictionaries, each representing a serialized node or edge.
    """
    elements = []

    elements.append(dict(node))

    for c in node.children:
        edge_element = {
            "source": c.name(),
            "target": node.name(),
            "type": "edge",
        }
        elements.append(edge_element)

    # nodes
    for c in node.children:
        if c.is_original(node):
            elements.extend(_serialize(c))
    return elements
