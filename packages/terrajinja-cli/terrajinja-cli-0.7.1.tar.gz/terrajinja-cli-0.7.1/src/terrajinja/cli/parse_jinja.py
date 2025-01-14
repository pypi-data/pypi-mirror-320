from datetime import datetime
import logging
import os
import textwrap
import json
import re
import ipaddress
import base64

import yaml
from deepmerge import Merger
from jinja2 import Environment, Undefined, FileSystemLoader
from yaml.parser import ParserError
from yaml.scanner import ScannerError

logger = logging.getLogger(__name__)


class SilentUndefined(Undefined):
    """Do not error out if a value is not found"""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""


def jinja_cidr_to_ip(cidr, nr):
    ipn = ipaddress.ip_network(cidr, strict=True)
    return str(ipn.network_address + nr)


def jinja_base64_encode(s):
    """
    Encode a string to base64.
    """
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


def jinja_read_file(path):
    try:
        with open(path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


# Define a custom function to read JSON file contents and return a JSON-serialized string
def read_json_file(filepath):
    try:
        with open(filepath, 'r') as file:
            content = json.load(file)  # Load JSON data from file
            json_str = json.dumps(content)  # Serialize JSON data to a string
            # Escape backslashes and single quotes, then wrap the content in single quotes
            escaped_content = json_str.replace('\\', '\\\\').replace("'", "\\'").replace('\\"', '\"')
            return escaped_content
    except Exception as e:
        return f"Error reading JSON file {filepath}: {e}"


def jinja_dict_to_yaml(*obj, **options) -> str:
    """
    Convert dict to yaml in human readable format.

    This writes the yaml in full format, for better parsing of jinja includes

    Args:
        obj: the object to present as yaml
        options: optional parameters to pass on to yaml.safe_dump function

    Return:
        A human readable yaml presentation of the original input

    """
    if options.get('indent'):
        indent = options['indent']
        del options['indent']
        return textwrap.indent(yaml.safe_dump(*obj, indent=2, allow_unicode=True, default_flow_style=False, **options),
                               ' ' * indent)

    return yaml.safe_dump(*obj, indent=4, allow_unicode=True, default_flow_style=False, **options)


def current_date(format: str = '%Y-%m-%d'):
    return datetime.now().strftime(format)


def get_nested(data, path):
    keys = path.split('.')
    for key in keys[:-1]:
        if isinstance(data, list):
            data = data[int(key)]
        else:
            data = data[key]
    return data, keys[-1]


def apply_regex_to_array(arr, match, replace):
    return [re.sub(match, replace, item) if isinstance(item, str) else item for item in arr]


def jinja_json_regex(obj: str, path: str, search: str = None, replace: str = None, delete_key: bool = False) -> str:
    """
    Apply a regex (replace) to a json object (obj) at a specific path

    Args:
        obj: the json object as a string
        path: path to adjust
        search: regex search
        replace: regex replace
        delete_key: delete_key if True (default: False)

    Return:
        json after applied regex as a string
    """
    if not delete_key and (not search or not replace):
        return "Error: match and replace must be provided when delete_key is False"
    try:
        data = json.loads(obj)
        parent, key = get_nested(data, path)

        if delete_key:
            if isinstance(parent, list):
                index = int(key)
                if index < len(parent):
                    del parent[index]
            elif key in parent:
                del parent[key]
        elif isinstance(parent, list):
            index = int(key)
            if index < len(parent):
                parent[index] = re.sub(search, replace, parent[index])
        elif key in parent:
            if isinstance(parent[key], list):
                parent[key] = apply_regex_to_array(parent[key], search, replace)
            else:
                parent[key] = re.sub(search, replace, parent[key])

        return json.dumps(data)
    except Exception as e:
        return f"Error adjusting JSON object: {e}"


class ParseJinja:
    """Parser for all jinja related files, and allows you to merge the output with initial parameters"""

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.jinja2env = Environment(undefined=SilentUndefined, extensions=['jinja2.ext.do'],
                                     loader=FileSystemLoader('.'))
        self.jinja2env.filters['to_yaml'] = jinja_dict_to_yaml
        self.jinja2env.filters['json_regex'] = jinja_json_regex
        self.jinja2env.filters['base64encode'] = jinja_base64_encode
        self.jinja2env.filters['cidr_to_ip'] = jinja_cidr_to_ip
        self.jinja2env.globals['read_json_file'] = read_json_file
        self.jinja2env.globals['read_file'] = jinja_read_file
        self.jinja2env.globals['current_date'] = current_date

    @staticmethod
    def merge(parameters_left: dict, parameters_right: dict) -> dict:
        """Combines 2 dicts with a merger

        Args:
            parameters_left (dict): low prio dict
            parameters_right (dict): high prio dict

        Returns:
            dict: merged dict
        """
        my_merger = Merger(
            [  # merger strategy
                (list, ["append"]),
                (dict, ["merge"]),
            ],
            ["override"],  # fallback strategies,
            ["override"],  # conflict strategy
        )
        return my_merger.merge(parameters_left, parameters_right)

    @staticmethod
    def get_yaml_filenames(path: str) -> list[str]:
        """get all yaml files in specified path

        Args:
            path (str): path to a directory

        Returns:
            list[str]: list of yaml files found
        """
        return [os.path.join(path, filename) for filename in os.listdir(f"{path}") if filename.endswith(".yaml")]

    def parse_directory(self, path: str, parameters: dict = None) -> dict:
        """parse all yaml files in the directory and return their merged value as dict
            results get merged with parameters before return

        Args:
            path (str): path to a directory
            parameters (dict, optional): parameters to merge the dict with. Defaults to {}.

        Returns:
            dict: merged dict of all parsed files and provided parameters
        """
        if parameters is None:
            parameters = {}
        for filename in self.get_yaml_filenames(path=path):
            parameters = self.parse_file(filename=filename, parameters=parameters)
        return parameters

    def parse_file(self, filename: str, parameters=None) -> dict:
        """parse a specific file and merge its result with parameters

        Args:
            filename (str): _description_
            parameters (dict, optional): parameters to merge the dict with. Defaults to {}.

        Raises:
            FileNotFoundError: file was not found

        Returns:
            dict: merged dict of all parsed file and provided parameters
        """
        if parameters is None:
            parameters = {}
        print(f"parsing file: {filename}")
        with open(filename, encoding="utf-8") as file:
            j2 = file.read()
            output = self.jinja2env.from_string(j2).render(env=os.environ, **parameters)
            logger.debug(f"output: {output}")
            try:
                y = yaml.safe_load(output)
            except ParserError as e:
                raise ParserError(f"in content:\n{output}\nerror: {e}")
            except ScannerError as e:
                raise ParserError(f"in content:\n{output}\nerror: {e}")
            if not y:
                return parameters

            # resources before merge
            rc_before = []
            tf_before = parameters.get('terraform')
            if tf_before:
                rc_before = tf_before.get('resources') or []

            # merge values
            merged = self.merge(parameters, y)

            # resources after merge
            rc_after = []
            tf_after = merged.get('terraform')
            if tf_after:
                rc_after = tf_after.get('resources') or []

            if len(rc_before) > len(rc_after):
                raise ValueError(
                    f'file {filename} is causing number of resources to be lower than previous file ({len(rc_before)}->{len(rc_after)}).'
                    + 'are you overwriting the terraform.resources with an empty value?')

            return merged
