<div align="center">

# NodePulse Python
[![PyPI Package](https://img.shields.io/pypi/v/nodepulse)](git branch -M main/)

**Maintain and utilize a list of healthy nodes.**

[Get Started](#get-started) | [Examples](examples)

</div>

NodePulse is a lightweight Python library designed to help developers maintain and utilize a list of healthy nodes (Currently it supports Hyperion and Atomic API nodes). The library connects to a Cloudflare Load Balanced API https://nodes.nodepulse.co/nodes (Which in turn connects to 3 backend APIs running on different cloud platforms) that provides a list of healthy nodes, which it regularly refreshes, and falls back to a predefined list of default nodes in case of not being able to contact any of the backends.

For now only the WAX network is supported.

## Features

- **GeoIP Integration**: Automatically connects you to geographically closest nodes
- **Real-time Node Discovery**: Dynamically finds and connects to available nodes
- **Fault Tolerance**: Maintains network integrity even if some nodes fail
- **Custom Default Nodes**: Allows overriding of default nodes for specific node types and networks
- **Network Supported**: WAX
- **Node Types Supported**: 
  - Hyperion
  - Atomic
  - LightAPI
  - IPFS

## Get Started

### Install the package

```bash
pip install nodepulse
```

### Basic Example

By default, it will provide you with 3 healthy Hyperion Mainnet nodes. To choose atomic and/or testnet nodes, you need to use custom options.

```python
from nodepulse import NodePulse

# Initialize NodePulse with default options
node_pulse = NodePulse()

# Retrieve the next healthy node in the list
node = node_pulse.get_node()
print(f"Using node: {node}")
```

### Custom Options.

You can customize the behavior of NodePulse by passing options when creating an instance. Available options include:

- `node_type`: Type of nodes to use ('hyperion', 'atomic', 'lightapi', or 'ipfs'). Default is 'hyperion'
- `network`: Network to use ('mainnet' or 'testnet'). Default is 'mainnet'
- `node_count`: Number of nodes to retrieve from the API. Default is 3
- `update_interval`: How often (in milliseconds) to refresh the node list. Default is 30000
- `api_url`: The API URL to fetch healthy nodes. Default is 'https://nodes.nodepulse.co/nodes'
- `default_nodes`: Custom default nodes to use as fallback
- `history_full`: (Hyperion only) Whether to return nodes with full history. Default is True
- `streaming_enabled`: (Hyperion only) Whether to return nodes with streaming enabled. Default is True
- `atomic_assets`: (Atomic only) Whether to return nodes with atomicassets support. Default is True
- `atomic_market`: (Atomic only) Whether to return nodes with atomicmarket support. Default is True
- `use_qry_hub`: Whether to use QryHub for fetching nodes. Default is False
- `qry_hub_api_url`: Custom QryHub API URL (optional, only used if `use_qry_hub` is True)
- `chain_id`: The chain ID to use when fetching nodes from QryHub (required if `use_qry_hub` is True)

**Example of using custom options with default node override for Hyperion Mainnet:**

```python
from nodepulse import NodePulse

custom_default_nodes = {
    'hyperion': {
        'mainnet': [
            'https://wax.eosrio.io',
            'https://api.waxsweden.org',
            'https://wax.eu.eosamsterdam.net'
        ]
    }
}

# Initialize with custom options and default nodes
node_pulse = NodePulse(
    node_type='hyperion',
    network='mainnet',
    node_count=5,
    update_interval=60000,  # Refresh every minute
    api_url='https://nodes.nodepulse.co/nodes',
    default_nodes=custom_default_nodes,
    history_full=False,
    streaming_enabled=False
)

# Retrieve a node from the custom configuration
node = node_pulse.get_node()
print(f"Using node: {node}")
```

**Example of using custom options with default node override for Atomic Mainnet:**

```python
from nodepulse import NodePulse

# Initialize with custom options
node_pulse = NodePulse(
    node_type='atomic',
    network='mainnet',
    node_count=5,
    update_interval=60000,  # Refresh every minute
    api_url='https://nodes.nodepulse.co/nodes',
    atomic_assets=False,
    atomic_market=False
)

# Retrieve a node from the custom configuration
node = node_pulse.get_node()
print(f"Using node: {node}")
```

**Example of using QryHub to fetch Hyperion nodes for the Jungle testnet:**

```python
from nodepulse import NodePulse

node_pulse = NodePulse(
    use_qry_hub=True,
    chain_id='73e4385a2708e6d7048834fbc1079f2fabb17b3c125b146af438971e90716c4d',
    node_type='hyperion',
    node_count=3,
    history_full=True,
    streaming_enabled=True
)

node = node_pulse.get_node()
print(f"Using QryHub node: {node}")
```

## Event Hooks

NodePulse provides several event hooks that allow developers to react to various events during the node-fetching process:

### on_node_update(nodes)

This hook is triggered every time the node list is successfully updated:

```python
def on_node_update(nodes):
    print(f"Nodes updated: {nodes}")

node_pulse = NodePulse(on_node_update=on_node_update)
```

### on_error(error)

This hook is called whenever there is an error while fetching nodes:

```python
def on_error(error):
    print(f"Error occurred: {str(error)}")

node_pulse = NodePulse(on_error=on_error)
```

### on_fallback(fallback_type, nodes)

This hook is triggered when falling back to existing or default nodes:

```python
def on_fallback(fallback_type, nodes):
    print(f"Falling back to {fallback_type} nodes: {nodes}")

node_pulse = NodePulse(on_fallback=on_fallback)
```

## Logging Options

NodePulse provides flexible logging options to help you debug and monitor its operation:

```python
import logging

# Create custom logger
custom_logger = logging.getLogger("custom_logger")
custom_logger.setLevel(logging.INFO)

# Initialize with custom logger and log level
node_pulse = NodePulse(
    logger=custom_logger,
    log_level='info'
)
```

Available log levels:
- error
- warn
- info
- debug

## Default Nodes

If the API fails to return healthy nodes or an error occurs, NodePulse falls back to a predefined list of default nodes:

```python
DEFAULT_NODES = {
    'hyperion': {
        'mainnet': [
            'https://wax.eosusa.news',
            'https://wax.greymass.com',
            'https://wax.cryptolions.io',
        ],
        'testnet': [
            'https://testnet.waxsweden.org',
            'https://testnet.wax.pink.gg',
            'https://testnet.wax.eosdetroit.io',
        ],
    },
    'atomic': {
        'mainnet': [
            'https://wax.api.atomicassets.io',
            'https://aa.wax.blacklusion.io',
            'https://wax-aa.eu.eosamsterdam.net',
        ],
        'testnet': [
            'https://test.wax.api.atomicassets.io',
            'https://atomic-wax-testnet.eosphere.io',
            'https://testatomic.waxsweden.org',
        ],
    },
}
```

## Error Handling and Retries

If fetching nodes from the API fails, NodePulse will attempt to use existing nodes or fall back to default nodes. The library uses Python's built-in threading for background updates and proper error handling.

## Thread Safety

NodePulse is thread-safe and can be safely used in multi-threaded applications. It uses Python's threading module for background updates and proper locking mechanisms for shared state. 