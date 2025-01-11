# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['roc',
 'roc.rpl',
 'roc.rpl.compressed',
 'roc.rpl.packet_parser',
 'roc.rpl.packet_parser.parser',
 'roc.rpl.packet_structure',
 'roc.rpl.rice',
 'roc.rpl.tasks',
 'roc.rpl.tests',
 'roc.rpl.time']

package_data = \
{'': ['*'], 'roc.rpl.tests': ['data/*']}

install_requires = \
['cython>=3,<4',
 'numpy>=1.20,<3',
 'poppy-core>0.12.0',
 'poppy-pop>0.12.0',
 'roc-idb>=1.0,<2.0',
 'spice_manager']

setup_kwargs = {
    'name': 'roc-rpl',
    'version': '1.7.1',
    'description': 'RPW Packet parsing Library (RPL): a plugin for the RPW TM/TC packet analysis',
    'long_description': 'roc-rpl\n============\n\nPython Package to parse RPW raw telemetry.\n\nThis package has been initially designed to be run in the RPW Operations and Data Pipeline (RODP).\nContact the developer team for more details.\n\n## Quickstart\n\nTo install package using [pip](https://pypi.org/project/pip-tools/):\n\n```\npip install roc-rpl\n```\n\n## Authors\n\n- xavier dot bonnin at obspm dot fr\n- florence dot henry at obspm dot fr\n- sonny dot lion at obspm dot fr\n\n## License\n\nThis project is licensed under CeCILL 2.1.\n\n## Acknowledgments\n\n* Solar Orbiter / RPW Operation Centre (ROC) team',
    'author': 'ROC Team',
    'author_email': 'roc.support@sympa.obspm.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gitlab.obspm.fr/ROC/Pipelines/Plugins/RPL',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4',
}
from build_cython import *
build(setup_kwargs)

setup(**setup_kwargs)
