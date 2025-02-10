import logging

from src.core.db import init_db
from src.core.models import BlockManager, Block
from src.peer.nodes import NodeService
from src.peer.peers import PeersManager


class BlockchainManager:
    def __init__(self, mongodb_url, authorized, own_public_key, private_key, network_id, own_node_name, chain_version):
        self.client_db = init_db(mongodb_url)
        self.db = self.client_db.blockchain
        self.block_manager = BlockManager(
            self.db, network_id, chain_version, authorized, private_key)
        self.peer_manager = PeersManager(
            self.client_db, authorized, own_public_key)
        self.node_service = NodeService(self.peer_manager, own_node_name)

    def start_node_service(self, port):
        return self.node_service.start(port)

    def get_latest_block(self):
        return self.block_manager.get_latest_block()

    def get_all_blocks(self):
        return self.block_manager.get_all_blocks()

    def generate_genesis_block(self):
        return self.block_manager.generate_genesis_block()

    def create_new_block(self, diploma_type, pdf_hash, authors, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info=None):
        return self.block_manager.create_new_block(diploma_type, pdf_hash, authors, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info)

    def calculate_pdf_hash(self, pdf_file):
        return Block.calculate_pdf_hash(pdf_file)
