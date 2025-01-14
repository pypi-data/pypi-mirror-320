from cwstorm.dsl.work_node import WorkNode

# from cwstorm.dsl.cmd import Cmd
import re


class Task(WorkNode):
    """
Tasks are generic nodes that contain commands.

They may be added to other Tasks as dependencies or to the Job.
    """

    ORDER = 30
    ATTRS = {
        "commands": {
            "type": "list:Cmd",
            "default": [],
            "description": "The commands to run on the instance.",
        },
        "hardware": {
            "type": "str",
            "validator": re.compile(r"^[a-z0-9_\-\.\s]+$", re.IGNORECASE),
            "description": "The instance type definition to run the task on.",
        },
        "preemptible": {
            "type": "bool",
            "default": True,
            "description": "Whether the task can be preempted by the cloud provider.",
        },
        "env": {
            "type": "dict",
            "description": "Environment variables to set on the instance.",
        },
        "lifecycle": {
            "type": "dict",
            "validator": {"keys": ["minsec", "maxsec"]},
            "description": "The minimum and maximum number of seconds the task is expected to run. If it runs shorter or longer, then the task is considered to have failed.",
        },
        "attempts": {
            "type": "int",
            "validator": {"min": 1, "max": 10},
            "default": 1,
            "description": "The number of times to attempt to run the task if it is preempted or failed.",
        },
        "output_path": {
            "type": "str",
            "default": "/tmp",
            "description": "The directory in which to store the output of the task. In most cases this will be set automatically by the system.",
        },
        "packages": {
            "type": "list:str",
             "default": [],
            "validator": re.compile(r"^[a-fA-F0-9]{32}$"),
            "description": "The set of packages Ids that describe the software to be made available and billed for this task.",
        },
    }

