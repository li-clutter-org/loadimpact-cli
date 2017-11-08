# Load Impact CLI [![Build Status](https://travis-ci.org/loadimpact/loadimpact-cli.png?branch=master,develop)](https://travis-ci.org/loadimpact/loadimpact-cli) [![Coverage Status](https://coveralls.io/repos/loadimpact/loadimpact-cli/badge.svg?branch=develop&service=github)](https://coveralls.io/github/loadimpact/loadimpact-cli?branch=develop)

This is the Command line interface for Load Impact API version 3. The CLI can perform the following operations:
- user scenarios: listing, creating, retrieving, validating, updating, deleting
- data stores: listing, downloading, creating
- tests: listing, running
- metrics: list
- For all other use cases, reference the REST API at http://developer.loadimpact.com/api/index.html

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
export LOADIMPACT_API_V3_TOKEN='your_api_token'
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
123 My test name    2017-01-02 03:04:05   Finished            50 users 2s
456 My second test  2017-02-03 12:34:56   Aborted by user     10 users 5s; 100 users 60s
```

By default, it will display the first 20 Tests, ordered by their last run
date, from all the Projects from all the Organizations you have access to.
This can be narrowed down by the `--project_id` and the `--limit` flags. For
example, the following command:
```
$ loadimpact test list --project_id 100 --project_id 200 --limit 5
```

Will display the five most recent Tests from projects 100 and 200.

The output truncates the values of several columns (*Name* and *Config*) for
the purposes of readability. This can be overriden by the `--full-width`
argument, which will cause the information to be displayed fully and separated
by tab characters (`\t`).

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

'Initializing test ...'
TIMESTAMP:           VUs [1]: reqs/s [1]: bandwidth [1]: user load time [1]: failure rate [1]:
2017-01-02 03:04:00  5.0      6.626671    89340.2656     -                   -
2017-01-02 03:04:03  8.0      3.956092    53336.0410     -                   -
2017-01-02 03:04:06  10.0     2.644981    35659.6385     -                   -
2017-01-02 03:04:09  15.0     3.970042    53524.1070     -                   -
2017-01-02 03:04:12  17.0     2.646911    35685.6541     -                   -
2017-01-02 03:04:15  20.0     3.969141    53511.9623     -                   -
2017-01-02 03:04:18  22.0     6.613472    89162.8336     235.73              -
2017-01-02 03:04:21  25.0     5.289569    71313.9719     234.3               -
...
```

This output can be disabled by the `--quiet` flag. The metrics displayed can
also be selected using the `--metric` flag (in the case of default metrics) or
the `--raw_metric` flag (that allows the passing of parameters for the metrics
as defined the [in the documentation][api-results] directly):

```
$ loadimpact test run 123 --metric bandwidth --raw_metric __li_url_XYZ:1:225:200:GET
```

Please note that the default metrics (the ones selected by using the
`--metric` flag) will by default display the first aggregation function for
the aggregated world load zone.

The output displays the values using fixed width, truncating if needed, for
the purposes of readability. This can be overriden by the `--full-width`
argument, which will cause the information to be displayed fully and separated
by tab characters (`\t`).

If the test run finishes with a failure status then the CLI will exit with a
non-zero exit code. This is helpful in combination with [thresholds](http://support.loadimpact.com/knowledgebase/articles/918699-thresholds)
when using the CLI in an automation pipeline using tools and services like
Jenkins, CircleCI, TeamCity etc.

## Working with Metrics

#### Listing Metrics

The `metric list` command lists the Metrics available for a Test Run:
```
$ loadimpact metric list 789

NAME:                                                    ARGUMENT NAME:  TYPE:
__li_bandwidth:1                                         bandwidth       common
__li_bandwidth:13                                        bandwidth       common
__li_clients_active:1                                    clients_active  common
__li_clients_active:13                                   clients_active  common
__li_user_load_time:1                                    user_load_time  common
__li_user_load_time:13                                   user_load_time  common
__li_url_69e369c64ef5e40f6fd8566e4163860d:13:225:200:GET -               url
__li_url_69e369c64ef5e40f6fd8566e4163860d:1:225:200:GET  -               url
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

[api-results]: http://developers.loadimpact.com/api/#get-tests-id-results
