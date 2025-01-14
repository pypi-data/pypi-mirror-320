from cwstorm.dsl.work_node import WorkNode
import re


class Email(WorkNode):
    """
An Email node sends a notification to a list of addresses.
    """

    ORDER = 60
    ATTRS = {
        "addresses": {
            "type": "list:str",
            "validator": re.compile(
                r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            ),
            "default": ["joe.bloggs@example.com"],
            "description": "The email addresses to send the message to.",
        },
        "subject": {
            "type": "str",
            "default": "Completed: ${workflow-id}",
            "validator": re.compile( r"^[^\r\n]{1,255}$", re.IGNORECASE),
            "description": "The subject of the email.",
        },
        "body": {
            "type": "str",
            "default": "The job with ID ${workflow-id} has been successfully completed.",
            "validator": re.compile(r"^[\s\S]*$", re.IGNORECASE),
            "description": "The body of the email.",
        },
    }
