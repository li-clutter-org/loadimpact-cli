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
import loadimpact3
import click
from loadimpact3.exceptions import UnauthorizedError

from .version import __version__
from .config import LOADIMPACT_API_TOKEN


try:
    client = loadimpact3.ApiTokenClient(api_token=LOADIMPACT_API_TOKEN)
    client.user_agent = "LoadImpactCLI/%s" % (__version__)
except UnauthorizedError:
    click.echo("Authentication failed")
