# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['roc',
 'roc.rap',
 'roc.rap.config',
 'roc.rap.tasks',
 'roc.rap.tasks.bia',
 'roc.rap.tasks.lfr',
 'roc.rap.tasks.lfr.bp',
 'roc.rap.tasks.tds',
 'roc.rap.tasks.thr',
 'roc.rap.tests',
 'roc.rap.tools']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=3,<4',
 'h5py>=3.7,<4.0',
 'numpy>=1.20,<3',
 'pandas>1,<3',
 'poppy-core>0.12.0',
 'poppy-pop>0.12.0',
 'roc-dingo>=1,<2',
 'roc-idb>=1,<2',
 'roc-rpl>=1,<2',
 'spice_manager']

setup_kwargs = {
    'name': 'roc-rap',
    'version': '1.6.0',
    'description': 'Rpw dAta Processor (RAP): a plugin used to process RPW L0, L1 and HK data',
    'long_description': 'roc-rap\n============\n\nPython Package to process RPW L0 data.\n\nThis package has been initially designed to be run in the RPW Operations and Data Pipeline (RODP).\nContact the developer team for more details.\n\n## Quickstart\n\nTo install package using [pip](https://pypi.org/project/pip-tools/):\n\n```\npip install roc-rap\n```\n\n## Authors\n\n- xavier dot bonnin at obspm dot fr\n- florence dot henry at obspm dot fr\n- sonny dot lion at obspm dot fr\n\n## License\n\nThis project is licensed under CeCILL 2.1.\n\n## Acknowledgments\n\n* Solar Orbiter / RPW Operation Centre (ROC) team',
    'author': 'Xavier Bonnin',
    'author_email': 'xavier.bonnin@obspm.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gitlab.obspm.fr/ROC/Pipelines/Plugins/RAP',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4',
}
from build_cython import *
build(setup_kwargs)

setup(**setup_kwargs)
