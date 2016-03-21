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

from setuptools import setup

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'loadimpactcli'))

from version import __version__

setup(
    name='loadimpact-cli',
    version=__version__,
    author='Load Impact',
    author_email='support@loadimpact.com',
    url='http://developers.loadimpact.com/',
    packages=['loadimpactcli'],
    py_modules=['loadimpactcli'],
    license='LICENSE.txt',
    description="The Load Impact CLI interfaces with Load Impact's cloud-based performance testing platform",
    include_package_data=True,
    data_files=[('', ['README.md'])],
    install_requires=[
        'setuptools>=18',
        'click',
        'loadimpact-v3',
        'tzlocal',
        'six',
        'mock'
    ],
    test_requires=['coverage'],
    entry_points={
        'console_scripts': [
            'loadimpact=loadimpactcli.loadimpact_cli:run_cli',
        ],
    },
    test_suite='tests',
)
