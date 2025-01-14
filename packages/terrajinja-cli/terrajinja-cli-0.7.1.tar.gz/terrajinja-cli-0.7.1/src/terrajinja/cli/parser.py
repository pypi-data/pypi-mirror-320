import filecmp
import logging
import os
import shutil
import pathlib
import uuid
import json

from .parse_args import ParseArgs
from .parse_jinja import ParseJinja

logger = logging.getLogger(__name__)


class ParseConfig:
    def __init__(self, custom_args=None):
        self.jinja = ParseJinja()
        self.parse_args = ParseArgs(self.jinja, custom_args=custom_args)

    def get_config(self) -> dict:
        """parses all config files

        Returns:
            dict: merge of all configs

        """
        # get initial arguments and read parameters
        args, _ = self.parse_args.parse_known_args()

        if args.command == "template":
            self.use_template(args)
            exit(0)

        if args.command == "init":
            self.init_dir(args)
            exit(0)

        parameter_path = os.path.join(args.config_directory, 'parameters')
        deployments_path = os.path.join(args.config_directory, 'deployments')
        templates_path = os.path.join(args.config_directory, 'templates')

        # read all parameter files
        parameters = self.jinja.parse_directory(path=parameter_path)
        # if parameters is empty, no parameters where provided in yaml, odd but sure, you're new
        if not parameters:
            print(f'warn: no parameters were read from the parameter path {parameter_path}, this is unexpected')

        # read the deployment arg
        deployment = self.parse_args.get_deployment(path=deployments_path, parameters=parameters)

        # parse deployment input requirements and enhance parameters with the result
        parameters = self.parse_args.parse_deployment_input(deployment=deployment, parameters=parameters)
        if not parameters:
            print(
                'error: no parameters were read from the provided deployment file, please provide a yaml file as input')
            exit(1)

        # re-read the deployment file so that its jinja parsed too for the templates etc
        parameters = self.jinja.parse_file(filename=os.path.join(deployments_path, f"{parameters['deployment']}.yaml"),
                                           parameters=parameters)

        # finally parse the templates
        parameters = self.parse_templates(templates_path, parameters)
        return parameters

    def parse_templates(self, path: str, parameters: dict) -> dict:
        """parse all template files using the parameters provided

        Args:
            path: directory to the parameter files
            parameters: dict to use as input for the parameter files

        Returns:
            dict: formatted templates merged in a single dict

        """
        templates = parameters.get("templates")
        if templates:
            for template_filename, version in templates.items():
                parameters = self.jinja.parse_file(
                    filename=os.path.join(path, f"{template_filename}_v{version}.yaml",
                                          ),
                    parameters=parameters,
                )

        return parameters

    @staticmethod
    def init_dir(args: any):
        action = False
        for sub in ["deployments", "templates", "parameters"]:
            _path = os.path.join(args.config_directory, sub)
            if not os.path.exists(_path):
                print('creating directory', _path)
                os.mkdir(_path)
                action = True

        cdktf_out = {
            "language": "python",
            "app": "true",
            "appx": "pipenv run python main.py",
            "projectId": f"{uuid.uuid4()}",
            "sendCrashReports": "false",
            "terraformProviders": [],
            "terraformModules": [],
            "codeMakerOutput": "imports"
        }
        try:
            with open(os.path.join(args.config_directory, 'cdktf.json'), "x") as f:
                f.write(json.dumps(cdktf_out))
                action = True
        except FileExistsError:
            pass

        if not action:
            print('init already done, have a look at the template command to add a template (tjcli template -l)')
            exit(1)

        print(
            'initial directories created, have a look at the template command to add a template (tjcli template -l)')

    # noinspection PyStringFormat
    @staticmethod
    def use_template(args: any):
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')

        # get a list of all templates
        if args.list:
            print('available templates:')
            filenames = [filename for filename in os.listdir(template_dir)]
            for filename in filenames:
                desc_file = os.path.join(template_dir, filename, 'description.txt')
                if os.path.exists(desc_file):
                    description = open(desc_file).read()
                else:
                    description = 'no description found'
                print(f'  %-{len(max(filenames, key=len)) + 1}s: %s' % (filename, description))

        # add a template
        if args.add:
            print(f"requesting to add template '{args.add}':")
            template_named_dir = os.path.join(template_dir, args.add)
            if not os.path.exists(template_named_dir):
                print(f'error: non-existing template: {args.add}')
                exit(1)

            # check if destination path exists
            for sub in ["deployments", "templates", "parameters"]:
                destination_path = os.path.join(args.config_directory, sub)
                if not os.path.exists(destination_path):
                    print(f'destination path: {destination_path} does not exist, did you run tjcli init?')
                    exit(1)

            for file in pathlib.Path(template_named_dir).rglob('*'):
                if str(file).endswith('description.txt'):
                    continue
                short_path = str(file)[len(template_dir) + len(args.add) + 2:]
                target = os.path.join(args.config_directory, short_path)
                if file.is_dir():
                    pathlib.Path(target).mkdir(parents=True, exist_ok=True)

                if file.is_file():
                    if os.path.exists(target):
                        if filecmp.cmp(file, target):
                            print(f'add: {short_path} already exists but is the same, ignoring')
                            continue
                        if not args.force:
                            print(f'add: {short_path} already exists, aborting. use --force to overwrite')
                            exit(1)
                    print(f'add: {short_path}')
                    shutil.copyfile(file, target)
