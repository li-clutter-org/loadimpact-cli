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
from operator import attrgetter

import click

from loadimpact3.exceptions import ConnectionError
from .client import client
from .util import Metric

# TestRunResults type codes.
TEXT_TO_TYPE_CODE_MAP = {
    'common': 1,
    'url': 2,
    'live_feedback': 3,
    'log': 4,
    'custom_metric': 5,
    'page': 6,
    'dtp': 7,
    'system': 8,
    'server_metric': 9,
    'integration': 10
}


@click.group()
@click.pass_context
def metric(ctx):
    pass


@metric.command('list', short_help='List metrics for a test run.')
@click.argument('test_run_id')
@click.option('--type', '-t', 'metric_types', multiple=True, type=click.Choice(TEXT_TO_TYPE_CODE_MAP.keys()),
              help='Metric type to include on the list.')
def list_metrics(test_run_id, metric_types):
    try:
        types = ','.join(str(TEXT_TO_TYPE_CODE_MAP[k]) for k in metric_types)
        result_ids = client.list_test_run_result_ids(test_run_id, data={'types': types})

        click.echo('NAME:\tARGUMENT NAME:\tTYPE:')
        for result_id in sorted(result_ids, key=attrgetter('type')):
            for key, _ in sorted(result_id.ids.items()):
                metric_ = Metric.from_raw(key)

                click.echo(u'{0}\t{1}\t{2}'.format(key,
                                                   metric_.str_param(),
                                                   result_id.results_type_code_to_text(result_id.type)))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")
