import argparse
import logging
import os
import sys

logger = logging.getLogger(__name__)


class KeyNotInPath(Exception):
    """key does not exist in path"""


def dotdict(dotpath: str, dictionary: dict) -> any:
    """Get the path from a dict based on a dotted path notation

    Args:
        dotpath (str): path of the variable to fetch
        dictionary (dict): dict to fetch the variable from

    Raises:
        ValueError: _description_

    Returns:
        any: result of the item in dict
    """
    path = dotpath.split(".")
    if not dictionary.get(path[0]):
        raise KeyNotInPath(f"unable to parse dotted string '{dotpath}' does not exist in the parameters")
    if len(path) > 1:
        return dotdict(".".join(path[1:]), dictionary[path[0]])
    return dictionary[path[0]]


def parse_variables(input_string: str, parameters: dict) -> str:
    """replace variables in a string based on a dictionary
        replaces strings that start with a '$' with the value of the key with this name

    Args:
        input_string (str): string that contains variables
        parameters (dict): dictionary of variables and values to apply

    Returns:
        str: formatted string
    """
    temp = []
    for word in input_string.split("."):
        if word[0] == "$":
            word = parameters.get(word[1:], word)
        temp.append(word)
    res = ".".join(temp)
    return res


class ParseArgs:
    """Parse commandline arguments, and generate choices based on existing files"""

    def __init__(self, jinja: any, parameters: dict = None, custom_args=None):
        if parameters is None:
            parameters = {}
        self.jinja = jinja
        self.parameters = parameters
        self.parser = argparse.ArgumentParser()
        self.sub_parser = self.parser.add_subparsers(dest="command")
        self.deploy_parser = self.sub_parser.add_parser("deploy", help='start a deployment')
        self.template_parser = self.sub_parser.add_parser("template", help='list ot get templates to start with')
        self.init_parser = self.sub_parser.add_parser("init", help='initialize configuration structure')

        # default parameters which are always available
        self.parser.add_argument(
            "-C",
            "--config-directory",
            # default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "config"),
            default=os.path.join(os.getcwd()),
            help="path to the config directory (default: current working directory)",
        )
        self.deploy_parser.add_argument(
            "-A",
            "--action",
            required=False,
            choices=["plan", "apply", "destroy"],
            help="Action to perform on the deployment",
        )
        self.deploy_parser.add_argument(
            "-l",
            "--loglevel",
            choices=["debug", "info", "warning", "error", "critical"],
            help="Set the logging level (default: %(default)s)",
            default="INFO",
        )
        # template
        self.template_parser.add_argument(
            "-l",
            "--list",
            action='store_true',
            help="list available templates",
        )
        self.template_parser.add_argument(
            "-a",
            "--add",
            help="add a template",
        )
        self.template_parser.add_argument(
            "-f",
            "--force",
            action='store_true',
            help="overwrite existing files when adding a template",
        )

        args, _ = self.parser.parse_known_args(custom_args)
        if len(sys.argv) == 1:
            self.parser.print_help()
            exit(1)

        if args.command == "init":
            self.parser.parse_args(custom_args)

        if args.command == "template":
            self.parser.parse_args(custom_args)

        if args.command == "template" and len(sys.argv) == 2:
            self.template_parser.print_help()
            exit(1)

    @staticmethod
    def get_file_base_names_from_path(path: str) -> list[str]:
        """get available deployments"""
        return [x.split(".")[0] for x in os.listdir(path)]

    def get_deployment(self, path: str, parameters: dict) -> dict:
        if len(self.get_file_base_names_from_path(path)) == 0:
            print(f"No deployments available in {path}. Create one first or start by using a template (tjcli template)")
            exit(1)

        """parse argument of deployment, and get additional arguments from the deployment yaml"""
        self.deploy_parser.add_argument(
            "-d",
            "--deployment",
            required=True,
            choices=self.get_file_base_names_from_path(path),
            help="Name of the deployment",
        )
        args, _unknown = self.parser.parse_known_args()
        return self.jinja.parse_file(os.path.join(path, f"{args.deployment}.yaml"))

    def parse_deployment_input(self, deployment, parameters) -> dict:
        required_input = deployment.get("required_input")
        if not required_input:
            return parameters

        for arg, config in required_input.items():
            choices = config.get("choices")
            if choices and not isinstance(choices, list):
                parameter = dotdict(parse_variables(choices, parameters), parameters)
                if isinstance(parameter, dict):
                    config["choices"] = [x for x in parameters.get(choices).keys()]
                if isinstance(parameter, str):
                    config["choices"] = [parameters]

            default = config.get("default")
            if default:
                if "." in default:
                    config["default"] = dotdict(parse_variables(default, parameters), parameters)

            self.deploy_parser.add_argument(f"-{arg[0]}", f"--{arg}", **config)

            # after each arg, parse it, so it can be used as input in the next if needed, merge it in parameters
            args, _unknown = self.parser.parse_known_args()
            parameters = self.jinja.merge(vars(args), parameters)
        return parameters

    def parse_args(self) -> argparse:
        """return all current parsable arguments"""
        return self.parser.parse_args()

    def parse_known_args(self) -> argparse:
        """return all current parsable arguments"""
        return self.parser.parse_known_args()
