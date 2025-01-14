from cwstorm.dsl.node import Node
import re


class Cmd(Node):
    """
A Cmd represents a single command line to be executed. 

Tasks hold a list of Cmds, and Cmd arguments are held in a list. Lists of commands in a task run in serial.
    """

    ORDER = 50
    ATTRS = {
        "argv": {
            "type": "list:str",
        },
    }

    def __init__(self, *args):
        self.argv(*args)
