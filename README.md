# Load Impact CLI [![Build Status](https://travis-ci.org/loadimpact/loadimpact-cli.png?branch=master,develop)](https://travis-ci.org/loadimpact/loadimpact-cli) [![Coverage Status](https://coveralls.io/repos/loadimpact/loadimpact-cli/badge.svg?branch=develop&service=github)](https://coveralls.io/github/loadimpact/loadimpact-cli?branch=develop)

Command line interface for Load Impact API version 3.

## Install

[![PyPI](https://img.shields.io/pypi/v/loadimpact-cli.svg)](https://pypi.python.org/pypi/loadimpact-cli) [![PyPI](https://img.shields.io/pypi/dm/loadimpact-cli.svg)](https://pypi.python.org/pypi/loadimpact-cli)

Install using setup.py

```
python setup.py install
```

## Configuration

Before running the loadimpact cli you need to add your Load Impact API token and the default project you wish to work with to the config file.

The config file will be placed:

For MacOSX:

```
/Library/Application Support/LoadImpact/config.ini
```

For Linux:

```
~/.config/LoadImpact/config.ini
```

The config file should look like this:

```
[user_settings]
api_token=your_api_token
```

You can also specify the default project you want to work with here by adding the id of the project you wish to work with:

```
[user_settings]
api_token=your_api_token
default_project=2
```

Optionally, if you don't want to edit the config-file you can set default project and api key as environment variables instead:


```
export LOADIMPACT_API_TOKEN='your_api_token'
export LOADIMPACT_DEFAULT_PROJECT=1
```

## Running the cli

```
$ loadimpact
Usage: loadimpact [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  organization
  user-scenario
```

### Listing organizations

```
$ loadimpact organization list
```


### Listing the projects of an organization

Listing the projects of an organization with id 1. This will help you find the project you want to use as default project

```
$ loadimpact organization projects 1
```
