# coding=utf-8
"""
Copyright 2016 Load Impact

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from time import sleep
import click
from tzlocal import get_localzone

from loadimpact3.exceptions import ConnectionError

from .client import client
from .config import DEFAULT_PROJECT


@click.group(name='user-scenario')
@click.pass_context
def userscenario(ctx):
    pass


@userscenario.command('get', short_help='Get user-scenario.')
@click.argument('id')
def get_scenario(id):
    try:
        user_scenario = client.get_user_scenario(id)
        click.echo(user_scenario.script)
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@userscenario.command('list', short_help='List user-scenarios.')
@click.option('--project_id', default=DEFAULT_PROJECT, envvar='DEFAULT_PROJECT', help='Id of the project to list scenarios from.')
def list_scenarios(project_id):
    if not project_id:
        return click.echo('You need to provide a project id.')
    try:
        userscenarios = client.list_user_scenarios(project_id)
        click.echo("ID:\tNAME:")
        for userscenario in userscenarios:
            click.echo(u'{0}\t{1}'.format(userscenario.id, userscenario.name))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@userscenario.command('create', short_help='Create user-scenario.')
@click.argument('script_file', type=click.File('r'))
@click.argument('name')
@click.option('--project_id', default=DEFAULT_PROJECT, envvar='DEFAULT_PROJECT', help='Id of the project the scenario should be in.')
@click.option('--datastore_file', type=click.File('r'), multiple=True, help='A CSV file to be used as a new data store for the user scenario. The file is read from line 1 expecting comma (,) as a separator and double quotes (") as a delimiter and the name of the file is used as a name for the data store. Multiple files can be provided by repeating the option.')
@click.option('--datastore_id', type=int, multiple=True, help='The ID of an existing data store to be linked to the user scenario. Multiple IDs can be provided by repeating the option.')
def create_scenario(script_file, name, project_id, datastore_file, datastore_id):
    if not project_id:
        return click.echo('You need to provide a project id.')
    script = read_file(script_file)
    data = {
        u"name": name,
        u"script": script,
        u"project_id": project_id
    }
    data_store_ids = []

    if datastore_file:
        for data_store_file in datastore_file:
            data_store_json = {
                'name': data_store_file.name,
                'project_id': project_id,
                'delimiter': 'double',
                'separator': 'comma',
                'fromline': 1,
            }
            try:
                data_store = client.create_data_store(data_store_json, data_store_file)
            except ConnectionError:
                click.echo("Cannot connect to Load impact API")
            data_store_ids.append(data_store.id)

    data_store_ids += datastore_id

    if data_store_ids:
        data[u"data_store_ids"] = data_store_ids

    try:
        click.echo(client.create_user_scenario(data=data).script)
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@userscenario.command('update', short_help='Update user-scenario script.')
@click.argument('scenario_id')
@click.argument('script_file', type=click.File('r'))
def update_scenario(scenario_id, script_file):
    script = read_file(script_file)
    try:
        user_scenario = update_user_scenario_script(scenario_id, script)
        click.echo(user_scenario.script)
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@userscenario.command('delete', short_help='Delete user-scenario.')
@click.confirmation_option(help='Are you sure you want to delete the user-scenario?')
@click.argument('scenario_id')
def delete_scenario(scenario_id):
    try:
        click.echo(delete_user_scenario(scenario_id))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@userscenario.command('validate', short_help='Validate user-scenario script.')
@click.argument('scenario_id')
def validate_scenario(scenario_id):
    try:
        user_scenario = client.get_user_scenario(scenario_id)
        validation = get_validation(user_scenario)
        validation_results = get_validation_results(validation)
        click.echo(get_formatted_validation_results(validation_results))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


def delete_user_scenario(scenario_id):
    userscenario = client.get_user_scenario(scenario_id)
    return userscenario.delete()


def update_user_scenario_script(scenario_id, script):
    userscenario = client.get_user_scenario(scenario_id)
    userscenario.update_scenario({'script': script})
    return client.get_user_scenario(scenario_id)


def get_validation(user_scenario):
    validation = user_scenario.validate()
    return validation


def get_validation_results(validation):
    poll_rate = 10

    while not validation.is_done():
        validation = client.get_user_scenario_validation(validation.id)
        sleep(poll_rate)

    validation_results = client.get_user_scenario_validation_result(validation.id)
    return validation_results


def get_formatted_validation_results(validation_results):
    formatted_validations = ''
    for result in validation_results:
        result_in_local_time = get_timestamp_as_local_time(result.timestamp)
        result_level_formatted = ''
        if result.level:
            result_level_formatted = '{0} '.format(result.level)
        formatted_validations += u"{0}[{1}] {2}\n".format(result_level_formatted, result_in_local_time, result.message)
    return formatted_validations


def get_timestamp_as_local_time(timestamp):
    return timestamp.astimezone(get_localzone())


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def read_file(script_file):
    read_data = ""
    with script_file as f:
        read_data = f.read()
    return read_data
