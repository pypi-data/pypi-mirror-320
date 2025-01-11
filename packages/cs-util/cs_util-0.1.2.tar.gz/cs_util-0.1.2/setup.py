# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cs_util', 'cs_util.tests']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.0,<6.0',
 'camb==1.5.4',
 'datetime>=5.5,<6.0',
 'keyring>=25.2.0,<26.0.0',
 'matplotlib>=3.8.4,<4.0.0',
 'numpy>=1.26.4,<2.0.0',
 'pyccl>=3.0.2,<4.0.0',
 'scipy>=1.13.0,<2.0.0',
 'swig>=4.2.1,<5.0.0',
 'vos>=3.6.1,<4.0.0']

setup_kwargs = {
    'name': 'cs-util',
    'version': '0.1.2',
    'description': 'Utility library for CosmoStat',
    'long_description': '# cs_util package\n\nUtility library for CosmoStat\n\n| Usage | Development | Release |\n| ----- | ----------- | ------- |\n| [![docs](https://img.shields.io/badge/docs-Sphinx-blue)](https://martinkilbinger.github.io/cs_util/) | [![build](https://github.com/martinkilbinger/cs_util/workflows/CI/badge.svg)](https://github.com/martinkilbinger/cs_util/actions?query=workflow%3ACI) | [![release](https://img.shields.io/github/v/release/martinkilbinger/cs_util)](https://github.com/martinkilbinger/cs_util/releases/latest) |\n| [![license](https://img.shields.io/github/license/martinkilbinger/cs_util)](https://github.com/martinkilbinger/cs_util/blob/master/LICENCE.txt) | [![deploy](https://github.com/martinkilbinger/cs_util/workflows/CD/badge.svg)](https://github.com/martinkilbinger/cs_util/actions?query=workflow%3ACD) | [![pypi](https://img.shields.io/pypi/v/cs_util)](https://pypi.org/project/cs_util/) |\n| [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide) | [![codecov](https://codecov.io/gh/martinkilbinger/cs_util/branch/master/graph/badge.svg?token=XHJIQXV7AX)](https://codecov.io/gh/martinkilbinger/cs_util) | [![python](https://img.shields.io/pypi/pyversions/cs_util)](https://www.python.org/downloads/source/) |\n| [![contribute](https://img.shields.io/badge/contribute-read-lightgrey)](https://github.com/martinkilbinger/cs_util/blob/master/CONTRIBUTING.md) | [![CodeFactor](https://www.codefactor.io/repository/github/martinkilbinger/cs_util/badge)](https://www.codefactor.io/repository/github/martinkilbinger/cs_util) | |\n| [![coc](https://img.shields.io/badge/conduct-read-lightgrey)](https://github.com/martinkilbinger/cs_util/blob/master/CODE_OF_CONDUCT.md) | [![Updates](https://pyup.io/repos/github/martinkilbinger/cs_util/shield.svg)](https://pyup.io/repos/github/martinkilbinger/cs_util/) | |\n\n---\n> Author: <a href="www.cosmostat.org/people/kilbinger/" target="_blank" style="text-decoration:none; color: #F08080">Martin Kilbinger</a>  \n> Email: <a href="mailto:martin.kilbinger@cea.fr" style="text-decoration:none; color: #F08080">martin.kilbinger@cea.fr</a>  \n> Year: 2022  \n---\n\n\n\n## Contents\n\n### Library\n\n- Galaxy catalogue handling\n- Weak-lensing related cosmological quantities (e.g. surface mass density)\n- VOS (Virtual Observatory Software)\n- Command line logging\n- Plotting\n- Basic statistic calculations\n- UNIONS/CFIS weak-lensing survey handling\n',
    'author': 'Martin Kilbinger',
    'author_email': 'martin.kilbinger@cea.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.13',
}


setup(**setup_kwargs)
