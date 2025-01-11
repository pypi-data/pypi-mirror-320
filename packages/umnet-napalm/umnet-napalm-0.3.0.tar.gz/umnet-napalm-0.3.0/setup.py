# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['umnet_napalm',
 'umnet_napalm.asa',
 'umnet_napalm.ios',
 'umnet_napalm.iosxr',
 'umnet_napalm.iosxr_netconf',
 'umnet_napalm.junos',
 'umnet_napalm.nxos',
 'umnet_napalm.panos']

package_data = \
{'': ['*'],
 'umnet_napalm.asa': ['utils/textfsm_templates/*'],
 'umnet_napalm.ios': ['utils/textfsm_templates/*'],
 'umnet_napalm.iosxr': ['utils/textfsm_templates/*'],
 'umnet_napalm.nxos': ['utils/textfsm_templates/*']}

install_requires = \
['napalm-panos>=0.6.2,<0.7.0', 'napalm>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'umnet-napalm',
    'version': '0.3.0',
    'description': 'A custom version of NAPALM for UMnet',
    'long_description': '# umnet-napalm\nThis is a project that augments the [NAPALM](https://napalm.readthedocs.io/en/latest/) library in ways that are relevant to our interests.\nMore specifically, new [getter functions](https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix) have been implemented to pull\ndata from routers and parse it into a vender agnostic format.\n\nThe following platforms all have their own `umnet-napalm` drivers. Most of these inherit from other libraries.\n* `ASA` does not inherit - the NAPALM community ASA driver uses the web API which is currently impractical for us.\n* `IOS` inherits `napalm.ios.IOSDriver`\n* `IOSXRNetconf` inherits `napalm.iosxr_netconf.IOSXRNETCONFDriver`\n* `Junos` inherits `napalm.junos.JunOSDriver`\n* `NXOS` inherits `napalm.nxos_ssh.NXOSSSHDriver`\n* `PANOS` inherits `napalm_panos.panos.PANOSDriver`\n\nSee the `umnet_napalm` [Abstract Base Class](https://github.com/umich-its-networking/umnet-napalm/blob/main/umnet_napalm/abstract_base.py) definition to see what commands are supported across all platforms. For platforms that inherit from core NAPALM drivers, refer to the [getter matrix](https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix). For PANOS see [napalm-panos repo](https://github.com/napalm-automation-community/napalm-panos)\n\n## Using umnet-napalm\ntbd\n',
    'author': 'Amy Liebowitz',
    'author_email': 'amylieb@umich.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
