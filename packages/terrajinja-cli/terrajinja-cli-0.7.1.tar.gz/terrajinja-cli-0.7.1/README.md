# Terrajinja CLI

Is a intermediate command line interface that accepts YAML/Jinja2 template files as input in order to generate a terraform deployment

#### CLI command structure

Each command is represented as a command or subcommand, and there are a number of command and subcommand options available:

```
$ tjcli <command> {deploy,template,init} [args]
```
* init - creates the config directory structure
* template - list or add templates to your config
* deploy - create a deployment for your config

for additional help ad the --help parameter to the sub command
e.g.:
```
$ tjcli template --help
```

## Getting started
start by installing the cli using pip
```
$ pip install terrajinja-cli
```

next step is to choose a place to store your config, in general this is a git repository.
you can then create the initial directory stucture in that directory
```
$ tjcli init
creating directory project/deployments
creating directory project/templates
creating directory project/parameters
```

to get some inspiration look at the available templates that have already been created for your inspiration.
```
$ tjcli template --list
available templates:
  gitlab-runner: for creating a gitlab runner on kubernetes
```

you can add any of these templates to your project
```
$ tjcli template --add gitlab-runner
requesting to add template {args.template}...
dest: project/templates/generic_gitlab_runner_v0.0.1.yaml
adding: templates / generic_gitlab_runner_v0.0.1.yaml
dest: project/parameters/gitlab_runner.yaml
adding: parameters / gitlab_runner.yaml
```

## Configuring a deployment
Terra jinja expects the following paths to contain YAML or Jinja2 template files:

| directory | files | description |
| ------ | ------ | ------ |
| parameters | YAML only | main input to be used by all deployments |
| deployments | YAML/Jinja2 | this defines the accepted parameters and what templates to execute |
| templates | YAML/Jinja2 | the templates define the terraform modules to execute |

Please refer to the documentation for the full file specifications

## Deploying your deployment
Which deployment is available depends on the files you created in the deployments directory
e.g.:
```
$ tjcli deploy -d my_deployment -a mailrelay -e test
```
Note that the parameters are dynamicly based on the deployment file, so the actual parameters availabe will vary on your config.

Once terrajinja created your deployment you can run cdktf to apply or destroy your deployment. e.g.:
```
cdktf apply
```

