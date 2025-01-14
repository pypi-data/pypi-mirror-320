# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starknet_py',
 'starknet_py.abi.v0',
 'starknet_py.abi.v1',
 'starknet_py.abi.v2',
 'starknet_py.cairo',
 'starknet_py.cairo.deprecated_parse',
 'starknet_py.cairo.v1',
 'starknet_py.cairo.v2',
 'starknet_py.devnet_utils',
 'starknet_py.hash',
 'starknet_py.net',
 'starknet_py.net.account',
 'starknet_py.net.models',
 'starknet_py.net.schemas',
 'starknet_py.net.schemas.rpc',
 'starknet_py.net.signer',
 'starknet_py.net.udc_deployer',
 'starknet_py.proxy',
 'starknet_py.serialization',
 'starknet_py.serialization.data_serializers',
 'starknet_py.utils',
 'starknet_py.utils.sync']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4,<4.0.0',
 'asgiref>=3.4.1,<4.0.0',
 'crypto-cpp-py==1.4.5',
 'eth-keyfile>=0.8.1,<1.0.0',
 'lark>=1.1.5,<2.0.0',
 'marshmallow-dataclass<8.8.0',
 'marshmallow-oneofschema>=3.1.1,<4.0.0',
 'marshmallow>=3.15.0,<4.0.0',
 'poseidon-py==0.1.5',
 'pycryptodome>=3.17,<4.0',
 'typing-extensions>=4.3.0,<5.0.0']

extras_require = \
{'docs': ['sphinx>=4.3.1,<8.0.0',
          'enum-tools[sphinx]==0.12.0',
          'furo>=2024.5.6,<2025.0.0'],
 'ledger': ['ledgerwallet>=0.5.0,<1.0.0', 'bip-utils>=2.9.3,<3.0.0']}

setup_kwargs = {
    'name': 'starknet-py',
    'version': '0.25.0',
    'description': 'A python SDK for Starknet',
    'long_description': '<div align="center">\n    <img src="https://raw.githubusercontent.com/software-mansion/starknet.py/master/graphic.png" alt="starknet.py"/>\n</div>\n<h2 align="center">Starknet SDK for Python</h2>\n\n<div align="center">\n\n[![codecov](https://codecov.io/gh/software-mansion/starknet.py/branch/master/graph/badge.svg?token=3E54E8RYSL)](https://codecov.io/gh/software-mansion/starknet.py)\n[![pypi](https://img.shields.io/pypi/v/starknet.py)](https://pypi.org/project/starknet.py/)\n[![build](https://img.shields.io/github/actions/workflow/status/software-mansion/starknet.py/checks.yml)](https://github.com/software-mansion/starknet.py/actions)\n[![docs](https://readthedocs.org/projects/starknetpy/badge/?version=latest)](https://starknetpy.readthedocs.io/en/latest/?badge=latest)\n[![license](https://img.shields.io/badge/license-MIT-black)](https://github.com/software-mansion/starknet.py/blob/master/LICENSE.txt)\n[![stars](https://img.shields.io/github/stars/software-mansion/starknet.py?color=yellow)](https://github.com/software-mansion/starknet.py/stargazers)\n[![starkware](https://img.shields.io/badge/powered_by-StarkWare-navy)](https://starkware.co)\n\n</div>\n\n## 📘 Documentation\n\n- [Installation](https://starknetpy.rtfd.io/en/latest/installation.html)\n- [Quickstart](https://starknetpy.rtfd.io/en/latest/quickstart.html)\n- [Guide](https://starknetpy.rtfd.io/en/latest/guide.html)\n- [API](https://starknetpy.rtfd.io/en/latest/api.html)\n- [Migration guide](https://starknetpy.readthedocs.io/en/latest/migration_guide.html)\n\n## ⚙️ Installation\n\nInstallation varies between operating systems.\n\n[See our documentation on complete instructions](https://starknetpy.rtfd.io/en/latest/installation.html)\n\n\n## 💨 Quickstart\n### Using FullNodeClient\nA [Client](https://starknetpy.readthedocs.io/en/latest/api/client.html#client) is a facade for interacting with Starknet. \n[FullNodeClient](https://starknetpy.readthedocs.io/en/latest/api/full_node_client.html#module-starknet_py.net.full_node_client) is a client which interacts with a Starknet full nodes like [Pathfinder](https://github.com/eqlabs/pathfinder), [Papyrus](https://github.com/starkware-libs/papyrus) or [Juno](https://github.com/NethermindEth/juno). \nIt supports read and write operations, like querying the blockchain state or adding new transactions.\n\n\n```python\nfrom starknet_py.net.full_node_client import FullNodeClient\n\nnode_url = "https://your.node.url"\nclient = FullNodeClient(node_url=node_url)\n\ncall_result = await client.get_block(block_number=1)\n```\nThe default interface is asynchronous. Although it is the recommended way of using starknet.py, you can also use a synchronous version. It might be helpful to play with Starknet directly in python interpreter.\n\n```python\nnode_url = "https://your.node.url"\nclient = FullNodeClient(node_url=node_url)\ncall_result = client.get_block_sync(block_number=1)\n```\nYou can check out all of the FullNodeClient’s methods here: [FullNodeClient](https://starknetpy.readthedocs.io/en/latest/api/full_node_client.html#module-starknet_py.net.full_node_client).\n\n### Creating Account\n[Account](https://starknetpy.readthedocs.io/en/latest/api/account.html#starknet_py.net.account.account.Account) is the default implementation of [BaseAccount](https://starknetpy.readthedocs.io/en/latest/api/account.html#starknet_py.net.account.base_account.BaseAccount) interface. \nIt supports an account contract which proxies the calls to other contracts on Starknet.\n\nAccount can be created in two ways:\n- By constructor (It is required to provide an `address` and either `key_pair` or `signer`).\n- By static method `Account.deploy_account_v3`\n\nAdditionally, you can use the [sncast](https://foundry-rs.github.io/starknet-foundry/starknet/index.html) tool to create an account, \nwhich will automatically be saved to a file.\nThere are some examples how to do it:\n```python\nfrom starknet_py.net.account.account import Account\nfrom starknet_py.net.full_node_client import FullNodeClient\nfrom starknet_py.net.models.chains import StarknetChainId\nfrom starknet_py.net.signer.key_pair import KeyPair\nfrom starknet_py.net.signer.stark_curve_signer import StarkCurveSigner\n\n# Creates an instance of account which is already deployed\n# Account using transaction version=1 (has __validate__ function)\nclient = FullNodeClient(node_url="https://your.node.url")\naccount = Account(\n    client=client,\n    address="0x4321",\n    key_pair=KeyPair(private_key=654, public_key=321),\n    chain=StarknetChainId.SEPOLIA,\n)\n\n# There is another way of creating key_pair\nkey_pair = KeyPair.from_private_key(key=123)\n# or\nkey_pair = KeyPair.from_private_key(key="0x123")\n\n# Instead of providing key_pair it is possible to specify a signer\nsigner = StarkCurveSigner("0x1234", key_pair, StarknetChainId.SEPOLIA)\n\naccount = Account(\n    client=client, address="0x1234", signer=signer, chain=StarknetChainId.SEPOLIA\n)\n```\n\n### Using Account\nExample usage:\n\n```python\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.client_models import ResourceBounds\nl1_resource_bounds = ResourceBounds(\n    max_amount=int(1e5), max_price_per_unit=int(1e13)\n)\n# Declare and deploy an example contract which implements a simple k-v store.\n# Contract.declare_v3 takes string containing a compiled contract (sierra) and\n# a class hash (casm_class_hash) or string containing a compiled contract (casm)\ndeclare_result = await Contract.declare_v3(\n    account,\n    compiled_contract=compiled_contract,\n    compiled_class_hash=class_hash,\n    l1_resource_bounds=l1_resource_bounds,\n)\n\nawait declare_result.wait_for_acceptance()\ndeploy_result = await declare_result.deploy_v3(\n    l1_resource_bounds=l1_resource_bounds,\n)\n# Wait until deployment transaction is accepted\nawait deploy_result.wait_for_acceptance()\n\n# Get deployed contract\nmap_contract = deploy_result.deployed_contract\nk, v = 13, 4324\n# Adds a transaction to mutate the state of k-v store. The call goes through account proxy, because we\'ve used\n# Account to create the contract object\nawait (\n    await map_contract.functions["put"].invoke_v3(\n        k,\n        v,\n        l1_resource_bounds=ResourceBounds(\n            max_amount=int(1e5), max_price_per_unit=int(1e13)\n        ),\n    )\n).wait_for_acceptance()\n\n# Retrieves the value, which is equal to 4324 in this case\n(resp,) = await map_contract.functions["get"].call(k)\n\n# There is a possibility of invoking the multicall\n\n# Creates a list of prepared function calls\ncalls = [\n    map_contract.functions["put"].prepare_invoke_v3(key=10, value=20),\n    map_contract.functions["put"].prepare_invoke_v3(key=30, value=40),\n]\n\n# Executes only one transaction with prepared calls\ntransaction_response = await account.execute_v3(\n    calls=calls,\n    l1_resource_bounds=l1_resource_bounds,\n)\nawait account.client.wait_for_tx(transaction_response.transaction_hash)\n```\n\n### Using Contract\n[Contract](https://starknetpy.readthedocs.io/en/latest/api/contract.html#starknet_py.contract.Contract) makes interacting with contracts deployed on Starknet much easier:\n```python\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.client_models import ResourceBounds\n\ncontract_address = (\n    "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"\n)\nkey = 1234\n\n# Create contract from contract\'s address - Contract will download contract\'s ABI to know its interface.\ncontract = await Contract.from_address(address=contract_address, provider=account)\n\n# If the ABI is known, create the contract directly (this is the preferred way).\ncontract = Contract(\n    address=contract_address,\n    abi=abi,\n    provider=account,\n    cairo_version=1,\n)\n\n# All exposed functions are available at contract.functions.\n# Here we invoke a function, creating a new transaction.\ninvocation = await contract.functions["put"].invoke_v3(\n        key,\n        7,\n        l1_resource_bounds=ResourceBounds(\n            max_amount=int(1e5), max_price_per_unit=int(1e13)\n        ),\n)\n# Invocation returns InvokeResult object. It exposes a helper for waiting until transaction is accepted.\nawait invocation.wait_for_acceptance()\n\n# Calling contract\'s function doesn\'t create a new transaction, you get the function\'s result.\n(saved,) = await contract.functions["get"].call(key)\n# saved = 7 now\n```\n\nTo check if invoke succeeded use `wait_for_acceptance` on InvokeResult and get its status.\n\nAlthough asynchronous API is recommended, you can also use Contract’s synchronous API:\n\n```python\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.client_models import ResourceBounds\n\ncontract_address = (\n    "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"\n)\n\nkey = 1234\ncontract = Contract.from_address_sync(address=contract_address, provider=account)\n\nl1_resource_bounds = ResourceBounds(\n            max_amount=int(1e5), max_price_per_unit=int(1e13)\n        ),\n\ninvocation = contract.functions["put"].invoke_v3_sync(key, 7, l1_resource_bounds=l1_resource_bounds)\ninvocation.wait_for_acceptance_sync()\n\n(saved,) = contract.functions["get"].call_sync(key)  # 7\n```\n\nContract automatically serializes values to Cairo calldata. This includes adding array lengths automatically. \nSee more info in [Serialization](https://starknetpy.readthedocs.io/en/latest/guide/serialization.html#serialization).\n\nQuickstart in docs - click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).\n',
    'author': 'Tomasz Rejowski',
    'author_email': 'tomasz.rejowski@swmansion.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/software-mansion/starknet.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9, <3.13',
}


setup(**setup_kwargs)
