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

import click
import requests
import shutil
from time import sleep

from loadimpact3.exceptions import ConnectionError
from loadimpact3 import DataStore

from .client import client
from .config import DEFAULT_PROJECT


@click.group(name='data-store')
@click.pass_context
def data_store(ctx):
    pass


@data_store.command('list', short_help='List datastore.')
@click.option('--project_id', default=DEFAULT_PROJECT, envvar='DEFAULT_PROJECT', help='Id of the project to list data stores from.')
def list_datastore(project_id):

    if not project_id:
        return click.echo('You need to provide a project id.')

    try:
        data_stores = client.list_data_stores(project_id)
        click.echo("ID:\tNAME:")
        for data_store in data_stores:
            click.echo(u"{0}\t{1}".format(data_store.id, data_store.name))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@data_store.command('download', short_help='Get datastore CSV.')
@click.argument('datastore_id')
@click.option('--file_name', help='Full path of file to save downloaded datastore in.')
def download_csv(datastore_id, file_name):
    try:
        data_store = client.get_data_store(datastore_id)
        file_path = file_name if file_name else "{0}.csv".format(data_store.id)
        click.echo("Downloading CSV file, please wait.")
        _download_csv(data_store, file_path)
        click.echo("Finished download.")
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@data_store.command('create', short_help='Create datastore.')
@click.argument('name')
@click.argument('datastore_file', type=click.File('r'))
@click.option('--delimiter', default='double', help='CSV file delimiter.')
@click.option('--separator', default='comma', help='CSV file separator.')
@click.option('--fromline', default=1, help='CSV file read from line')
@click.option('--project_id', default=DEFAULT_PROJECT, envvar='DEFAULT_PROJECT', help='Id of the project to create the data store in.')
def create_datastore(datastore_file, name, project_id, delimiter, separator, fromline):

    if not project_id:
        return click.echo('You need to provide a project id.')
    try:
        data_store_json = {
            'name': name,
            'project_id': project_id,
            'delimiter': delimiter,
            'separator': separator,
            'fromline': fromline,
        }
        data_store = client.create_data_store(data_store_json, datastore_file)
        data_store = _wait_for_conversion(data_store)

        click.echo("Data store conversion completed with status '{0}'".format(
                   (DataStore.status_code_to_text(data_store.status))))

    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@data_store.command('update', short_help='Update datastore.')
@click.argument('id')
@click.argument('datastore_file', type=click.File('r'))
@click.option('--name', default=None)
@click.option('--delimiter', default='double', help='CSV file delimiter.')
@click.option('--separator', default='comma', help='CSV file separator.')
@click.option('--fromline', default=1, help='CSV file read from line')
@click.option('--project_id', default=DEFAULT_PROJECT, envvar='DEFAULT_PROJECT', help='Project id of the data store')
def update_datastore(id, datastore_file, name, project_id, delimiter, separator, fromline):
    if not project_id:
        return click.echo('You need to provide a project id.')
    try:
        data_store = client.get_data_store(id)
        file_obj = datastore_file
        data_store_json = {
            'name': name if name else data_store.name,
            'project_id': project_id,
            'delimiter': delimiter,
            'separator': separator,
            'fromline': fromline,
        }
        data_store = client.update_data_store(id, data_store_json, file_obj)
        data_store = _wait_for_conversion(data_store)

        click.echo("Data store conversion completed with status '{0}'".format(
                  (DataStore.status_code_to_text(data_store.status))))

    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


def _wait_for_conversion(data_store):
    while not data_store.has_conversion_finished():
        sleep(3)
    return data_store


def _download_csv(user_scenario, file_path):
    response = requests.get(user_scenario.public_url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
