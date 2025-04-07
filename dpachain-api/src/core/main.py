import logging

from src.block.service import BlockService
from src.core.db import init_db
from src.block.manager import BlockManager
from src.node.manager import NodeManager
from src.peer.service import PeerService
from src.peer.manager import PeersManager
from src.node.service import NodeService


class BlockchainManager:
    def __init__(self, mongodb_url, authorized, own_public_key, private_key, network_id, own_node_name, chain_version):
        self.client_db = init_db(mongodb_url)
        self.db = self.client_db.blockchain
        self.block_manager = BlockManager(
            self.db, network_id, chain_version, authorized, private_key)
        self.peer_manager = PeersManager(
            self.client_db, authorized, own_public_key)
        self.node_manager = NodeManager(own_node_name)

        self.block_manager.set_peer_manager(self.peer_manager)
        self.block_manager.set_node_manager(self.node_manager)
        self.node_manager.set_block_manager(self.block_manager)
        self.node_manager.set_peers_manager(self.peer_manager)

    async def start_node_service(self, p2p_port):
        await self.node_manager.start(p2p_port)


class BlockchainService:
    def __init__(self, blockchain_manager):
        self.blockchain_manager = blockchain_manager
        self.block_service = BlockService(
            self.blockchain_manager.block_manager)
        self.peer_service = PeerService(self.blockchain_manager.peer_manager)
        self.node_service = NodeService(self.blockchain_manager.node_manager)
