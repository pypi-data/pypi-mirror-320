import requests
import time
import threading
import logging
from typing import List, Dict, Optional, Callable, Any
from enum import Enum

class NodeType(str, Enum):
    HYPERION = 'hyperion'
    ATOMIC = 'atomic'
    LIGHTAPI = 'lightapi'
    IPFS = 'ipfs'

class Network(str, Enum):
    MAINNET = 'mainnet'
    TESTNET = 'testnet'

class NodePulse:
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
        'lightapi': {
            'mainnet': [
                'https://lightapi.eosamsterdam.net',
                'https://lightapi.eosrio.io',
                'https://api.light.xeos.me',
            ],
            'testnet': [
                'https://testnet.lightapi.eosamsterdam.net',
                'https://testnet.lightapi.eosrio.io',
            ],
        },
        'ipfs': {
            'mainnet': [
                'https://ipfs.io',
                'https://cloudflare-ipfs.com',
                'https://gateway.pinata.cloud',
            ],
            'testnet': [
                'https://test-ipfs.pinata.cloud',
                'https://test.ipfs.io',
            ],
        },
    }

    def __init__(
        self,
        node_type: str = 'hyperion',
        network: str = 'mainnet',
        node_count: int = 3,
        update_interval: int = 30000,
        api_url: str = 'https://nodes.nodepulse.co/nodes',
        default_nodes: Optional[Dict] = None,
        history_full: bool = True,
        streaming_enabled: bool = True,
        atomic_assets: bool = True,
        atomic_market: bool = True,
        use_qry_hub: bool = False,
        qry_hub_api_url: Optional[str] = None,
        chain_id: Optional[str] = None,
        log_level: str = 'warn',
        logger: Optional[Any] = None,
        on_node_update: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_fallback: Optional[Callable] = None
    ):
        self.node_type = NodeType(node_type.lower())
        self.network = Network(network.lower())
        self.node_count = node_count
        self.update_interval = update_interval / 1000  # Convert to seconds
        self.api_url = api_url
        self.default_nodes = default_nodes or self.DEFAULT_NODES
        self.history_full = history_full
        self.streaming_enabled = streaming_enabled
        self.atomic_assets = atomic_assets
        self.atomic_market = atomic_market
        self.use_qry_hub = use_qry_hub
        self.qry_hub_api_url = qry_hub_api_url
        self.chain_id = chain_id
        
        # Setup logging with more detailed format
        self.logger = logger or logging.getLogger(__name__)
        log_level = getattr(logging, log_level.upper())
        self.logger.setLevel(log_level)
        
        # Add console handler if none exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        self.logger.info(f"Initializing NodePulse with options: node_type={self.node_type}, network={self.network}")
        
        # Event hooks
        self.on_node_update = on_node_update
        self.on_error = on_error
        self.on_fallback = on_fallback

        # Internal state
        self.nodes: List[str] = []
        self.current_index = 0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Do initial fetch before starting update thread
        self.refresh_nodes()
        
        # Start update thread
        self._start_update_thread()

    def _start_update_thread(self):
        """Start the background thread for updating nodes."""
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

    def _update_loop(self):
        """Background loop for updating nodes."""
        self.logger.info("Starting node update loop")
        while not self._stop_event.is_set():
            time.sleep(self.update_interval)  # Sleep first since we already have initial nodes
            if not self._stop_event.is_set():  # Check again after sleep
                self.logger.debug(f"Refreshing nodes (current nodes: {self.nodes})")
                self.refresh_nodes()

    def refresh_nodes(self) -> List[str]:
        """Refresh the list of nodes."""
        try:
            self.logger.info("Attempting to refresh nodes")
            if self.use_qry_hub:
                self.logger.debug("Using QryHub to fetch nodes")
                nodes = self._fetch_qry_hub_nodes()
            else:
                self.logger.debug(f"Fetching nodes from {self.api_url}")
                nodes = self._fetch_nodes()

            if nodes:
                self.logger.info(f"Successfully retrieved {len(nodes)} nodes")
                self.logger.debug(f"Retrieved nodes: {nodes}")
                with self._lock:
                    self.nodes = nodes
                if self.on_node_update:
                    self.on_node_update(nodes)
                return nodes
            else:
                self.logger.warning("Received empty node list from API")

        except Exception as e:
            self.logger.error(f"Error refreshing nodes: {str(e)}", exc_info=True)
            if self.on_error:
                self.on_error(e)

            # Fallback logic
            if self.nodes:
                self.logger.info("Falling back to existing nodes")
                if self.on_fallback:
                    self.on_fallback('existing', self.nodes)
                return self.nodes
            
            default_nodes = self.default_nodes[self.node_type][self.network]
            self.logger.info(f"Falling back to default nodes: {default_nodes}")
            if self.on_fallback:
                self.on_fallback('default', default_nodes)
            return default_nodes

    def _fetch_nodes(self) -> List[str]:
        """Fetch nodes from the API."""
        params = {
            'nodeType': self.node_type,
            'network': self.network,
            'nodeCount': self.node_count,
        }
        
        # Only add Hyperion-specific params if using Hyperion
        if self.node_type == NodeType.HYPERION:
            params.update({
                'historyfull': self.history_full,
                'streamingEnabled': self.streaming_enabled,
            })
        
        # Only add Atomic-specific params if using Atomic
        elif self.node_type == NodeType.ATOMIC:
            params.update({
                'atomicassets': self.atomic_assets,
                'atomicmarket': self.atomic_market,
            })
        
        self.logger.debug(f"Fetching nodes with params: {params}")
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            nodes = response.json()
            self.logger.debug(f"API response: {nodes}")
            return nodes
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    def _fetch_qry_hub_nodes(self) -> List[str]:
        """Fetch nodes from QryHub."""
        if not self.chain_id:
            self.logger.error("chain_id is required when using QryHub")
            raise ValueError("chain_id is required when using QryHub")

        api_url = self.qry_hub_api_url or "https://wax.qryhub.com/v1/chain/get_endpoints"
        self.logger.debug(f"Fetching nodes from QryHub: {api_url}")
        try:
            response = requests.post(api_url, json={"chain_id": self.chain_id})
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"QryHub response: {data}")
            return [endpoint['url'] for endpoint in data['endpoints'][:self.node_count]]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"QryHub request failed: {str(e)}")
            raise

    def get_node(self) -> str:
        """Get the next healthy node using round-robin selection."""
        with self._lock:
            if not self.nodes:
                default_node = self.default_nodes[self.node_type][self.network][0]
                self.logger.warning(f"No nodes available, using first default node: {default_node}")
                return default_node

            # Extract URL if node is a dictionary, otherwise use node directly
            node = self.nodes[self.current_index]
            node_url = node['url'] if isinstance(node, dict) else node
            
            self.current_index = (self.current_index + 1) % len(self.nodes)
            self.logger.debug(f"Returning node: {node_url} (index: {self.current_index})")
            return node_url

    def __del__(self):
        """Cleanup when the object is destroyed."""
        self.logger.info("Shutting down NodePulse")
        self._stop_event.set()
        if hasattr(self, 'update_thread'):
            self.update_thread.join() 