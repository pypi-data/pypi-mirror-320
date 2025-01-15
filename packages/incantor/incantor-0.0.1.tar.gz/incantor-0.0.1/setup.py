# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['incantor']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'incantor',
    'version': '0.0.1',
    'description': 'Incantor',
    'long_description': '',
    'author': 'Lucas Nussbaum',
    'author_email': 'lucas@debian.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
