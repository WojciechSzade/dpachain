import logging 

from src.core.db import init_db
from src.core.models import BlockManager
from src.peer.nodes import NodeService
from src.peer.peers import PeersManager

class BlockchainManager:
    def __init__(self, mongodb_url, authorized, own_public_key, private_key, network_id, own_node_name, chain_version):
        self.client_db = init_db(mongodb_url)
        self.db = self.client_db.blockchain
        self.block_manager = BlockManager(self.db, network_id, chain_version, authorized, private_key)
        self.peer_manager = PeersManager(self.client_db, authorized, own_public_key)
        self.node_service = NodeService(self.peer_manager, own_node_name)
        
        