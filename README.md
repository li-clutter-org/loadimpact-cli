# Load Impact CLI [![Build Status](https://travis-ci.org/loadimpact/loadimpact-cli.png?branch=master,develop)](https://travis-ci.org/loadimpact/loadimpact-cli) [![Coverage Status](https://coveralls.io/repos/loadimpact/loadimpact-cli/badge.svg?branch=develop&service=github)](https://coveralls.io/github/loadimpact/loadimpact-cli?branch=develop)

This is the Command line interface for Load Impact API version 3. The CLI can perform the following operations:
- user scenarios: listing, creating, retrieving, validating, updating, deleting
- data stores: listing, downloading, creating
- For all other use cases, reference the REST API at http://developer.loadimpact.com/api/index.html

This CLI is still in BETA so we are still hunting bugs, adding features and changing things.

## Install

[![PyPI](https://img.shields.io/pypi/v/loadimpact-cli.svg)](https://pypi.python.org/pypi/loadimpact-cli) [![PyPI](https://img.shields.io/pypi/dm/loadimpact-cli.svg)](https://pypi.python.org/pypi/loadimpact-cli)

As a general recommendation, install `loadimpact-cli` in a `virtualenv` and make sure you use a recently upgraded `pip` install. See [issue #13](https://github.com/loadimpact/loadimpact-cli/issues/13) for some ideas if you are having trouble installing.

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

Before running the CLI you need to add your [Load Impact V3 API token](https://app.loadimpact.com/integrations/user-token) to the config file. You can generate a Load Impact V3 API token selecting CLI from the integrations page.

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
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  data-store
  metric
  organization
  test
  user-scenario
```

## Working with organizations and projects

#### Listing organizations

```
$ loadimpact organization list
```


#### Listing the projects of an organization

Listing the projects of an organization with id 1. This will help you find the project you want to use as default project. 

```
$ loadimpact organization projects 1
```

## Working with User Scenarios scripts

A [User Scenario](http://support.loadimpact.com/knowledgebase/articles/174287-what-is-a-user-scenario) is a object that contains a script that defines your user behavior. This script should be written in Lua.

#### Listing the User scenarios in a project.

In order to list the User scenarios in a project you need to specify a project id. Either you add this to the config or export them as an environment variable as mentioned above.

```
$ loadimpact user-scenario list

```

Or you can add it using the project_id-flag. 

```
$ loadimpact user-scenario list --project_id=1

```

Listing the user-scenarios prints the scripts of the user-scenarios of the specified projects. 

#### Creating a new User Scenario

In order to create a new User Scenario you need to have specified the project you want the User scenario to belong to in some of the ways mentioned under "Listing the User scenarios in a project." 

You also need to specify the path to the script file you want to create the User scenario with. 


```
$ loadimpact user-scenario create 'script name' /path/to/script.lua --project_id=1


```

You can also add a Data store to your user-scenario, either by using the id of an existing one:

```
$ loadimpact data-store list
ID: NAME:
43  Load Impact Basic
23  Fake Customers
$ loadimpact user-scenario create 'script name' /path/to/script.lua --project_id=1 --datastore_id=43


```

Or you can add a new Data store file using ```--datastore_file```,  this will create a new Data store in the project and add it to the User scenario. 

```
$ loadimpact user-scenario create 'script name' /path/to/script.lua --project_id=1 --datastore_file=/path/to/datastore.csv

```

#### Getting a User Scenario.

To get a User scenario script you'll need the id of that user scenario. 

```
$ loadimpact user-scenario get 1

```
#### Updating a User Scenario

To update the script of a User scenario you need to specify the id of the scenario you wan't to update and the script you want to upload for it. 

```
$ loadimpact user-scenario update 1 /path/to/script.lua

```

#### Validating a User Scenario

In order to be able to use a script it has to be valid, you can check if a script is valid by using the command validate. This will validate your script row by row. Please note that this command can takes some time to finish as we actually fire the script up and send some requests. 

```
$ loadimpact user-scenario validate 1

```

#### Deleting a User Scenario

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

#### Listing Data stores

The ```data-store list``` command lists the Data stores in the project.

```
$ loadimpact data-store list

```

#### Downloading a Data store

The ```data-store download``` command will download the .csv-file of the specified Data store. If the ```--file_name```-flag is omitted the file will be saved in the current directory as DATA-STORE-ID.csv

```
$ loadimpact data-store download 1 --file_name /path/where/you/want/file.csv

```

#### Creating a Data store
The ```data-store create``` command will create a new Data store containing the file specified.

```
$ loadimpact data-store create  'Your Data store name' /path/to/file.csv
```

#### Updating a Data store
The ```data-store update``` command will update the file of the specified Data store.

```
$ loadimpact data-store update 1 /path/to/file.csv
```

## Working with Tests

#### Listing Tests

The `test list` command lists the Tests you have access to:
```
$ loadimpact test list

ID: NAME:           LAST RUN DATE:        LAST RUN STATUS:    CONFIG:
123 My test name    2017-01-02 03:04:05   Finished            #321 100% at amazon:ie:dublin | 1s 50users
456 My second test  2017-02-03 12:34:56   Aborted by user     #987 100% at amazon:ie:dublin | 10s 50users
```

By default, it will display all the Tests from all the Projects from all the
Organizations you have access to. This can be narrowed down by the
`--project_id` flag:
```
$ loadimpact test list --project_id 100 --project_id 200
```

#### Running Tests

The `test run` command launches a Test Run from an existing Test:
```
$ loadimpact test run 123
```

The command will periodically print the metrics collected during the test run
(defaulting to VUs, requests/second, bandwidth, VU load time and failure rate)
until the test run is finished:

```
$ loadimpact test run 123

TEST_RUN_ID:
456
TIMESTAMP:           METRIC:                      AGGREGATE:  VALUE:
2017-01-02 03:04:00  __li_bandwidth:1             avg         1111.2222
2017-01-02 03:04:00  __li_clients_active:1        value       5.0
2017-01-02 03:04:00  __li_requests_per_second:1   avg         8.7654321
2017-01-02 03:04:03  __li_bandwidth:1             avg         2222.3333
2017-01-02 03:04:03  __li_clients_active:1        value       10.0
2017-01-02 03:04:03  __li_requests_per_second:1   avg         9.8765432
...
```

This output can be disabled by the `--quiet` flag. The metrics displayed can
also be selected using the `--metric` flag:

```
$ loadimpact test run 123 --metric __li_bandwidth --metric __li_clients_active:1
```

## Working with Metrics

#### Listing Metrics

The `metric list` command lists the Metrics available for a Test Run:
```
$ loadimpact metric list 789

NAME:                                                       TYPE:
__li_user_load_time:1                                       common
__li_total_requests:1                                       common
...
__li_url_b2d8b7afb66fd4d3c7faf263b13228e9:13:225:200:GET    url
__li_url_b2d8b7afb66fd4d3c7faf263b13228e9:1:225:200:GET url
...
```

The list of metrics to output can be narrowed down by metric type by using the
`--type` flag:

```
$ loadimpact metric list 789 --type common --type log
```

## Contribute!

If you wan't to contribute, please check out the repository and install the dependencys in a virtualenv using pip. The tests can be run with ```setup.py```

```
$ python setup.py test

```

If you've found a bug or something isn't working properly, please don't hesitate to create a ticket for us! 
