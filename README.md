# Load Impact CLI [![Build Status](https://travis-ci.org/loadimpact/loadimpact-cli.png?branch=master,develop)](https://travis-ci.org/loadimpact/loadimpact-cli) [![Coverage Status](https://coveralls.io/repos/loadimpact/loadimpact-cli/badge.svg?branch=develop&service=github)](https://coveralls.io/github/loadimpact/loadimpact-cli?branch=develop)

Command line interface for Load Impact API version 3. This CLI is still in BETA so we are still hunting bugs, adding features and changing things rapidly. 

## Install

[![PyPI](https://img.shields.io/pypi/v/loadimpact-cli.svg)](https://pypi.python.org/pypi/loadimpact-cli) [![PyPI](https://img.shields.io/pypi/dm/loadimpact-cli.svg)](https://pypi.python.org/pypi/loadimpact-cli)

### Install using setup.py

```
cd loadimpact-cli
python setup.py install
```

### Install using pip

```
pip install loadimpact-cli
```

## Configuration

Before running the CLI you need to add your [Load Impact V3 API token](https://app.loadimpact.com/account/api-token) to the config file. You can generate a Load Impact V3 API token in the user profile settings.

The config file will be placed:

For MacOSX:

```
/Users/<YOUR_USER_NAME>/Library/Application Support/LoadImpact/config.ini
```

For Linux:

```
~/.config/LoadImpact/config.ini
```

For Windows:

```
\AppData\LoadImpact\config.ini
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
  data-store
```

### Listing organizations

```
$ loadimpact organization list
```


### Listing the projects of an organization

Listing the projects of an organization with id 1. This will help you find the project you want to use as default project. 

```
$ loadimpact organization projects 1
```

## Working with User Scenarios scripts

A [User Scenario](http://support.loadimpact.com/knowledgebase/articles/174287-what-is-a-user-scenario) is a object that contains a script that defines your user behavior. This script should be written in Lua.

### Listing the User scenarios in a project.

In order to list the User scenarios in a project you need to specify a project id. Either you add this to the config or export them as an environment variable as mentioned above.

```
$ loadimpact user-scenario list

```

Or you can add it using the project_id-flag. 

```
$ loadimpact user-scenario list --project_id=1

```

Listing the user-scenarios prints the scripts of the user-scenarios of the specified projects. 

### Creating a new User Scenario

In order to create a new User Scenario you need to have specified the project you want the User scenario to belong to in some of the ways mentioned under "Listing the User scenarios in a project." 

You also need to specify the path to the script file you want to create the User scenario with. 


```
$ loadimpact user-scenario create 'script name' /path/to/script.lua --project_id=1

```
### Getting a User Scenario.

To get a User scenario script you'll need the id of that user scenario. 

```
$ loadimpact user-scenario get 1

```
### Updating a User Scenario

To update the script of a User scenario you need to specify the id of the scenario you wan't to update and the script you want to upload for it. 

```
$ loadimpact user-scenario update 1 /path/to/script.lua

```

### Validating a User Scenario

In order to be able to use a script it has to be valid, you can check if a script is valid by using the command validate. This will validate your script row by row. Please note that this command can takes some time to finish as we actually fire the script up and send some requests. 

```
$ loadimpact user-scenario validate 1

```

### Deleting a User Scenario

You can delete a User Scenario with the delete command. This will delete the entire User Scenario, not just remove the script. Since this is a destructive action you'll need to verify it. 

```
$ loadimpact user-scenario delete 1

```
If you need to bypass the verifying you can add the ```--yes``` flag. 

```
$ loadimpact user-scenario delete 1 --yes

```

## Working with Data stores

A Data store contains a .csv-file where you define values you want to use in your test. A Data store can be reused in many tests, making test-setups easier. For example a Data store .csv-file can contain [URL:s](http://support.loadimpact.com/knowledgebase/articles/174987-random-url-from-a-data-store) for a test. 

### Downloading a Data store

The ```data-store download``` command will download the .csv-file of the specified Data store. If the ```--file_name```-flag is omitted the file will be saved in the current directory as DATA-STORE-ID.csv

```
$ loadimpact data-store download 1 --file_name /path/where/you/want/file.csv

```

### Creating a Data store
The ```data-store create``` command will create a new Data store containing the file specified.

```
$ loadimpact data-store create  'Your Data store name' /path/to/file.csv
```

### Updating a Data store
The ```data-store update``` command will update the file of the specified Data store.

```
$ loadimpact data-store update 1 /path/to/file.csv
```

## Contribute!

If you wan't to contribute, please check out the repository and install the dependencys in a virtualenv using pip. The tests can be run with ```setup.py```

```
$ python setup.py test

```

If you've found a bug or something isn't working properly, please don't hesitate to create a ticket for us! 
