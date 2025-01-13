# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['t3tokit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 't3tokit',
    'version': '0.1.2',
    'description': 'A simple utility for creating directories.',
    'long_description': '## t3tokit\n\n### mzip.py\n\n压缩目录',
    'author': 'pytools',
    'author_email': 'hyhlinux@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
