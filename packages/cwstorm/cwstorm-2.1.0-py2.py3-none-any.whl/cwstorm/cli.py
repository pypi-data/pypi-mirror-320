import os
import click
import importlib
import json
import yaml
import sys
from cwstorm.version import VERSION
from cwstorm.serializers import default
from cwstorm import validator
import textwrap
import re
import io

# These imports are used to generate the classes documentation
from cwstorm.dsl.node import Node
from cwstorm.dsl.dag_node import DagNode
from cwstorm.dsl.job import Job
from cwstorm.dsl.task import Task
from cwstorm.dsl.upload import Upload
from cwstorm.dsl.email import Email
from cwstorm.dsl.cmd import Cmd
from cwstorm import dsl

import markdown
import io
import tempfile
import webbrowser

from cwstorm import __version__

import traceback


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        # Recursively look for further subclasses
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


PURE = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/pure-min.css" integrity="sha384-X38yfunGUhNzHpBaEBsWLO+A0HDYOQi8ufWDkZ0k9e0eXz/tH3II7uKZ9msv++Ls" crossorigin="anonymous">
<meta name="viewport" content="width=device-width, initial-scale=1">
"""

EXAMPLES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "examples")
EXAMPLE_MODULES_PREFIX = "cwstorm.examples."
GET_JOB_FUNCTION_NAME = "get_job"


EXAMPLE_FILES = os.listdir(EXAMPLES_FOLDER)
MODULE_FILES = [
    file for file in EXAMPLE_FILES if file.endswith(".py") and not file.startswith("__")
]
MODULE_NAMES = [file[:-3] for file in MODULE_FILES]  # Remove the .py extension


def _wrap_text(text, width):
    return "\n".join(textwrap.wrap(text, width=width))


########################### MAIN #################################
@click.group(invoke_without_command=True)
@click.pass_context
@click.option("-v", "--version", is_flag=True, help="Print the version and exit.")

# print documantation info to JSON. It is a choice with 2 options, classes or cli
@click.option("-d", "--docinfo", type=click.Choice(choices=["classes", "cli"], case_sensitive=False), help="Print documantation info to JSON.")

def main(ctx, version, docinfo):
    """
    The `storm` command line tool for working with the Storm DSL.
    
    To export information to the docs site, use the following commands:
    
    - name: Generate dsl-cli.json
    run: storm -d cli > ../storm-doc/static/json/dsl-cli.json

    - name: Generate dsl-classes.json
    run: storm -d classes > ../storm-doc/static/json/dsl-classes.json

        
    """
    if not ctx.invoked_subcommand:
        if version:
            click.echo(VERSION)
            ctx.exit()
        if docinfo == "classes":
            klasses = [klass for klass in get_all_subclasses(Node)] + [Node]
            klasses = sorted(klasses, key=lambda x: x.ORDER)
            result = get_class_doc_dict(*klasses)
            print(json.dumps(result))
        elif docinfo == "cli":
            info = main.to_info_dict(ctx)
            info["version"] = VERSION
            print(json.dumps(info))
        else:
            click.echo(ctx.get_help())
        ctx.exit()


SERIALIZE_HELP = """The structure of serialized DAG. 

default: is a list of nodes and a list of edges. The edges contain source and target pointers to node labels. This is the simplest and easiest to understand. It is also understood by the UI.
"""

FORMAT_HELP = """The output format. JSON and YAML are implemented. Pretty is a pretty-printed JSON.
"""

EXAMPLE_HELP = """The example job to serialize. The examples are in the storm/examples folder. The examples are python modules that contain a function called get_job that returns a job object.
"""

########################### SERIALIZE #############################
@main.command()
@click.option(
    "-f",
    "--fmt",
    "--format",
    help=FORMAT_HELP,
    default="json",
    type=click.Choice(choices=["json", "pretty", "yaml"], case_sensitive=False),
)

@click.option(
    "-x",
    "--example",
    help=EXAMPLE_HELP,
    default="all",
    type=click.Choice(choices=MODULE_NAMES + ["all"], case_sensitive=True),
)

@click.argument(
    "output",
    required=False,
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True),
)

def serialize(fmt, example, output):
    """
Serialize an example job to `JSON` or `YaML`. The structure of the serialized job is an object with two properties: nodes and edges. Nodes hold information about the tasks to run, files to upload, and so on. Edges comprise of a source and target node label and as such define the connectivity of the graph. This structure is easy to understand and can be deserializes back into a graph in memory.

Examples:

```bash
# To serialize the "frames" example and write it to stdout as pretty-printed json.
storm serialize -f pretty -x frames

# Output json to the file ~/Desktop/frames.json for visualization.
storm serialize -f json -x frames ~/Desktop
```
    """
    if example == "all":
        for example in MODULE_NAMES:
            _serialize(fmt, example, output)
    else:
        _serialize(fmt, example, output)


def _serialize(fmt, example, output):
    module_name = EXAMPLE_MODULES_PREFIX + example
    module = importlib.import_module(module_name)
    storm_script = getattr(module, GET_JOB_FUNCTION_NAME)
    job = storm_script()

    serialized = default.serialize(job)
    # Determine the output method (stdout or file)
    if output:
        ext = {
            "json": "json",
            "pretty": "json",
            "yaml": "yml",
        }
        fh = open(os.path.join(output, f"{example}.{ext[fmt]}"), "w", encoding="utf-8")
    else:
        fh = sys.stdout
    try:
        if fmt == "json":
            json.dump(serialized, fh)
        elif fmt == "pretty":
            json.dump(serialized, fh, indent=3)
        elif fmt == "yaml":
            yaml.dump(serialized, fh)
        else:
            raise ValueError(f"Unknown format: {fmt}")
    finally:
        # Only close the file if we're not writing to stdout
        if output:
            fh.close()


# storm serialize -x all  /Volumes/xhf/dev/cio/cioapp/public/graphs/ done


########################### VALIDATE #############################

VALIDATE_FORMAT_HELP = """The output format. HTML is the default and opens a browser window. Markdown is printed to the console.
"""

@main.command()
@click.option(
    "-f",
    "--fmt",
    "--format",
    help=VALIDATE_FORMAT_HELP,
    default="html",
    type=click.Choice(choices=["markdown", "html"], case_sensitive=False),
)
@click.argument("infile", nargs=1, type=click.Path(exists=True, resolve_path=True))
def validate(fmt, infile):
    """
Validate a JSON file.

Example:
```bash
storm validate /path/to/file.json
```
    """

    md = _as_markdown(infile)
    if fmt == "markdown":
        print(md)
    else:  # fmt == "html":
        html = markdown.markdown(md, extensions=["markdown.extensions.tables"])
        html = decorate(html)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html)
            webbrowser.open("file://" + f.name, new=2)


def _as_markdown(infile):
    stream = io.StringIO()
    stream.write(f"# Storm Validation Report:\n\n{infile}")

    with open(infile, "r", encoding="utf-8") as fh:
        data = json.load(fh)
        try:
            validation = validator.validate(data)
        except Exception:
            tb_lines = traceback.format_exc().splitlines()
            stream.write("\n\n".join(["```python"] + tb_lines + ["```"]))
            return stream.getvalue()

    stream.write("\n\n## Input Counts\n\n")
    stream.write("| Type | Count |\n")
    stream.write("|------|-------|\n")
    for key, value in validation["input_info"]:
        stream.write(f"| {key} | {value} |\n")

    stream.write("\n\n## Deserialized Job Info\n\n")
    stream.write("| Param | Value | Valid |\n")
    stream.write("|-------|-------|-------|\n")
    for key, value, valid in validation["job_info"]:
        stream.write(f"| {key} | {value} | {valid} |\n")
    result = stream.getvalue()
    stream.close()
    return result


########################### DISPLAY #############################
CLASSES_FORMAT_HELP="""The output format. Write a Markdown file or show an HTML page. If you want to export classes documentation in pure JSON format, use `storm -d classes` instead of this command."""

@main.command()
@click.option(
    "-f",
    "--fmt",
    "--format",
    help=CLASSES_FORMAT_HELP,
    default="html",
    type=click.Choice(choices=["markdown", "html"], case_sensitive=False),
)
def classes(fmt):
    """
Display the classes.

Shows the attributes of classes in the DSL in a web page or as markdown.
    """

    # Get all subclasses of ParentClass
    klasses = [klass for klass in get_all_subclasses(Node)] + [Node]

    # sort classes based on the ORDER attribute in reverse order
    klasses = sorted(klasses, key=lambda x: x.ORDER)

    if fmt == "markdown":
        display_classes_markdown(*klasses)
    elif fmt == "html":
        display_classes_html(*klasses)
    else:
        raise ValueError(f"Unknown format: {fmt}")
    

def get_class_doc_dict(*klasses):
    class_docs = []
    for klass in klasses:
        class_docs.append(class_to_dict(klass))

    result = {
        "classes"   : class_docs,
        "version": __version__
    }
    return result


def display_classes_markdown(*klasses):
    stream = io.StringIO()
    _write_markdown(stream, *klasses)

    print(stream.getvalue())


def display_classes_html(*klasses):
    stream = io.StringIO()
    _write_markdown(stream, *klasses)

    html = markdown.markdown(
        stream.getvalue(), extensions=["markdown.extensions.tables"]
    )
    html = decorate(html)
    stream.close()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html)
        webbrowser.open("file://" + f.name, new=2)

def _write_markdown(stream, *klasses):
    stream.write("# Storm DSL Classes - Version {}\n\n".format(__version__))
    if dsl.__doc__:
        stream.write(dsl.__doc__)
        stream.write("\n\n---\n\n")
        
    for klass in klasses:
        write_class_to_stream(klass, stream)


def class_to_dict(klass):
    class_name = klass.__name__
    base_class = klass.__bases__[0].__name__
    docstring = klass.__doc__

    merged_attrs = {**klass.BASE_ATTRS, **klass.ATTRS}
    rows = []
    for attr_name, attr in merged_attrs.items():
        datatype = attr["type"]
        default_str = str(attr.get("default", ""))
        validator_str = ""
        if "validator" in attr:
            validator_str = str(attr["validator"]) if "validator" in attr else ""
        apis = get_api_obj(attr_name, datatype)
        description = attr.get("description", "")
        rows.append(
            {
                "attr_name": attr_name,
                "datatype": datatype,
                "default": default_str,
                "validator": validator_str,
                "apis": apis,
                "description": description,
            }
        )

    return {
        "class_name": class_name,
        "base_class": base_class,
        "docstring": docstring,
        "attrs": rows,
    }


def write_class_to_stream(klass, stream):
    class_name = klass.__name__

    base_class = klass.__bases__[0].__name__

    docstring_paragraphs = re.split(r"\n\s*\n", klass.__doc__) if klass.__doc__ else []
    docstring_paragraphs = [p.strip() for p in docstring_paragraphs]
    class_description = (
        "\n\n".join(docstring_paragraphs)
        if len(docstring_paragraphs) > 0
        else "No description available."
    )

    desc = f"## Class: {class_name} ({base_class})\n\n#### Description:\n{class_description}\n\n"
    stream.write(desc)

    merged_attrs = {**klass.BASE_ATTRS, **klass.ATTRS}

    if len(merged_attrs) == 0:
        stream.write("\n\n")
        return
    headers = ["Name", "Type", "Default", "Validator", "API"]
    rows = [format_attr(name, attr) for name, attr in merged_attrs.items()]
    column_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]
    column_widths = [20, 18, 25, 25, 25]
    row_format = (
        "| " + " | ".join("{:<" + str(width) + "}" for width in column_widths) + " |"
    )
    stream.write(row_format.format(*headers))
    stream.write("\n")
    stream.write("|-" + "-|-".join("-" * width for width in column_widths) + "-|")
    stream.write("\n")
    for row in rows:
        stream.write(row_format.format(*row))
        stream.write("\n")
    stream.write("\n\n")
    stream.write("---\n\n")


def format_attr(name, attr):
    # Format type
    datatype = attr["type"]
    type_str = (
        attr["type"]
        .replace("list:", "List of ")
        .replace("int", "Int")
        .replace("bool", "Bool")
        .replace("str", "String")
        .replace("dict", "Dict")
    )

    # Format default value
    default_str = str(attr.get("default", ""))

    default_str = f"`{default_str}`" if default_str else ""

    # Format validator
    validator_str = ""
    if "validator" in attr:
        if isinstance(attr["validator"], re.Pattern):
            validator_str = f"Regex: {attr['validator'].pattern}"

        else:
            validator_str = str(attr["validator"])
        validator_str = validator_str.replace("|", "\\|")
        validator_str = f"`{validator_str}`"

    # Format API
    api_str = get_api_markdown(name, datatype)

    return [name, type_str, default_str, validator_str, api_str]


def decorate(html):
    html = html.replace("<table>", '<table class="pure-table pure-table-bordered">')
    html = '<html><head>{}</head><body style="margin: 2em;width=800px">{}</body></html>'.format(
        PURE, html
    )
    return html


def get_api_obj(attr_name, datatype):
    if datatype in ["bool", "int", "str"]:
        return [f"n.{attr_name}(value) -> self", f"n.{attr_name}() -> {datatype}"]

    elif datatype == "dict":
        return [
            f"n.{attr_name}({{key: 'VAL', ...}}) -> self",
            f"n.update_{attr_name}({{key2: 'VAL2', ...}}) -> self",
            f"n.{attr_name}() -> dict",
        ]
    elif datatype == "Cmd":
        return [f"n.{attr_name}(Cmd(*args)) -> self", f"n.{attr_name}() -> Cmd"]

    elif datatype.startswith("list:"):
        sub_type = datatype.split(":")[1]

        if sub_type in ["bool", "int", "str"]:
            return [
                f"n.{attr_name}(*args) -> self",
                f"n.push_{attr_name}(*args) -> self",
                f"n.{attr_name}() -> list of {sub_type}",
            ]

        elif sub_type == "dict":
            return [
                f"n.{attr_name}({{key: 'VAL', ...}}, {{key: 'VAL', ...}}, ...) -> self",
                f"n.push_{attr_name}({{key: 'VAL', ...}}, {{key: 'VAL', ...}}, ...) -> self",
                f"n.{attr_name}() -> list of dict",
            ]
        elif sub_type == "Cmd":
            return [
                f"n.{attr_name}(Cmd(*args), Cmd(*args), ...) -> self",
                f"n.push_{attr_name}(Cmd(*args), Cmd(*args), ...) -> self",
                f"n.{attr_name}() -> list of Cmd",
            ]

    return ""


def get_api_markdown(attr_name, datatype):
    stream = io.StringIO()

    if datatype == "bool":
        stream.write(f"`n.{attr_name}(value) -> self`<br />")
        stream.write(f"`n.{attr_name}() -> bool`")

    elif datatype == "int":
        stream.write(f"`n.{attr_name}(value) -> self`<br />")
        stream.write(f"`n.{attr_name}() -> int`")

    elif datatype == "str":
        stream.write(f"`n.{attr_name}(value) -> self`<br />")
        stream.write(f"`n.{attr_name}() -> str`")

    elif datatype == "dict":
        stream.write(f"`n.{attr_name}({{key: 'VAL', ...}}) -> self`<br />")
        stream.write(f"`n.update_{attr_name}({{key2: 'VAL2', ...}}) -> self`<br />")
        stream.write(f"`n.{attr_name}() -> dict`")

    elif datatype == "Cmd":
        stream.write(f"`n.{attr_name}(Cmd(*args)) -> self`<br />")
        stream.write(f"`n.{attr_name}() -> Cmd`")

    elif datatype.startswith("list:"):
        sub_type = datatype.split(":")[1]

        if sub_type == "int":
            stream.write(f"`n.{attr_name}(*args) -> self`<br />")
            stream.write(f"`n.push_{attr_name}(*args) -> self`<br />")
            stream.write(f"`n.{attr_name}() -> list of int`")

        elif sub_type == "str":
            stream.write(f"`n.{attr_name}(*args) -> self`<br />")
            stream.write(f"`n.push_{attr_name}(*args) -> self`<br />")
            stream.write(f"`n.{attr_name}() -> list of str`")

        elif sub_type == "Cmd":
            stream.write(f"`n.{attr_name}(Cmd(*args), Cmd(*args), ...) -> self`<br />")
            stream.write(
                f"`n.push_{attr_name}(Cmd(*args), Cmd(*args), ...) -> self`<br />"
            )
            stream.write(f"`n.{attr_name}() -> list of Cmd`")

        elif sub_type == "dict":
            stream.write(
                f"`n.{attr_name}({{key: 'VAL', ...}}, {{key: 'VAL', ...}}, ...) -> self`<br />"
            )
            stream.write(
                f"`n.push_{attr_name}({{key: 'VAL', ...}}, {{key: 'VAL', ...}}, ...) -> self`<br />"
            )
            stream.write(f"`n.{attr_name}() -> list of dict`")

    return stream.getvalue()
