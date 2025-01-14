from cwstorm.dsl.work_node import WorkNode

import re


class Upload(WorkNode):
    """
Upload node.

Uploads contain lists of filepaths. They are a special kind of task and can be added anywhere Task can be added.
    """

    ORDER = 40
    ATTRS = {
        "files": {
            "type": "list:dict",
            "validator": {"keys": ["path", "size", "md5"]},
            "description": "The files to upload. Each file must have a path, size, and md5 hash.",
        }
    }
