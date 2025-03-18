import logging
import random
from p2pd import *
from tenacity import after_log, before_log, before_sleep_log, retry, stop_after_attempt

from src.block.manager import BlockManager
from src.node.protocols import ProtocolManager
from src.node.errors import *
from src.peer.errors import PeerNotFoundError
from src.peer.models import PeerStatus
from src.peer.manager import PeersManager


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

max_tries = 20  # 2 minutes


class NodeManager:
    def __init__(self, nickname):
        self.node = None
        self.peers_manager = None
        self.block_manager = None
        self.protocol_manager = ProtocolManager()
        self.nickname = nickname
        self.pipes = []

    def set_block_manager(self, block_manager: BlockManager):
        self.block_manager = block_manager
        self.protocol_manager.set_block_manager(block_manager)

    def set_peers_manager(self, peers_manager: PeersManager):
        self.peers_manager = peers_manager
        self.protocol_manager.set_peers_manager(peers_manager)

    async def start(self, port):
        self.node: P2PNode = await self.__create_node(port)
        try:
            await self._set_node_nickname(self.nickname)
        except Exception as e:
            logger.error(f"Failed to set node nickname: {e}")
            logger.info(
                f"Setting node adress to ip {self.node.addr_bytes.decode()}")
            self.peers_manager.change_own_peer_nickname(
                self.node.addr_bytes.decode())
        # await self.connect_to_nodes()

    async def stop(self):
        await self.node.close()

    async def _set_node_nickname(self, nickname):
        try:
            node_nickname = await self.node.nickname(nickname)
            self.peers_manager.change_own_peer_nickname(
                node_nickname, self.node.addr_bytes.decode())
            logger.info(f"Node nickname set to: {node_nickname}")
        except Exception as e:
            logger.error(f"Failed to set node name to {nickname}")
            raise e

    async def sync_chain(self):
        logger.info("Starting sync chain")
        nodes_list = self.peers_manager.get_valid_peers_to_connect()
        responses = []
        logger.info(f"Nodes list: {nodes_list}")
        for node in nodes_list:
            logger.info(f"Connecting to {node.nickname}")
            pipe = await self.node.connect(node.nickname)
            if pipe is None:
                logger.info(
                    f"Failed to connect to {node.nickname} with previous state {self.peers_manager.get_peer_state(node.nickname)}")
                self.peers_manager.set_peer_status(
                    node.nickname, PeerStatus.INACTIVE)
                continue
            logger.info(f"Connected to {node.nickname}")
            logger.info(f"Pipe is {pipe.sock}")
            chain_size = await self.protocol_manager.request_chain_size(pipe)
            if chain_size is None:
                logger.info(f"Failed to get chain size from {node.nickname}")
                self.peers_manager.set_peer_status(
                    node.nickname, PeerStatus.INACTIVE)
                continue
            responses.append(
                {"pipe": pipe, "node": node, "chain_size": chain_size})
        # select best node
        if len(responses) == 0:
            raise NoPeersAviableError()
        best_nodes = self.select_best_node(responses)
        for best_node in best_nodes:
            logger.info(f"Connect to best node {best_node['node'].nickname}")
            pipe = await self.node.connect(best_node['node'].nickname)
            if pipe is None:
                logger.info(
                    f"Failed to connect to {best_node['node'].nickname} with previous state {self.peers_manager.get_peer_state(best_node['node'].nickname)}")
                self.peers_manager.set_peer_status(
                    best_node['node'].nickname, PeerStatus.INACTIVE)
                continue
            own_chain_size = self.block_manager.get_chain_size()
            own_last_block_hash = self.block_manager.get_latest_block(
            ).hash if own_chain_size > 0 else None
            res = await self.protocol_manager.request_compare_blockchain(pipe)
            if res is None:
                logger.error("Failed to get response from peer")
                continue
            chain_size, last_block_hash = res
            logger.info(
                f"Own chain size = {own_chain_size}, Own last block hash = {own_last_block_hash}")
            logger.info(
                f"Received peer chain size = {chain_size}, Peer last block hash = {last_block_hash}")
            if own_chain_size == chain_size and own_last_block_hash == last_block_hash:
                logger.info("Chain is synced!")
                return "Chain has been synced!"
            elif own_chain_size > chain_size:
                return "Chain is already synced!"
            elif own_chain_size == chain_size and own_last_block_hash != last_block_hash:
                logger.info(
                    "Chain size is the same, but last block hash is different")
                return "Chain size is the same, but last block hash is different"
            logger.info("Chain size is different - syncing")
            for i in range(own_chain_size, chain_size):
                pipe = await self.node.connect(best_node['node'].nickname)
                if pipe is None:
                    logger.info(
                        f"Failed to connect to {best_node['node'].nickname} with previous state {self.peers_manager.get_peer_state(best_node['node'].nickname)}")
                    self.peers_manager.set_peer_status(
                        best_node['node'].nickname, PeerStatus.INACTIVE)
                    continue
                block = await self.protocol_manager.request_block(pipe, i)
                logger.info(f"Received block {block}")
                if block is None:
                    logger.error("Failed to get block from peer")
                    continue
                if not self.block_manager.add_block(block):
                    logger.error("Failed to add block to blockchain")
                    continue
            return "Chain has been synced!"

        # connect to it
        # sync node list
        # compare blokchain(size and last hash)
        # foreaach missing block ask_for_block
        # if sent an invalid one - ban the node, repeat process
        # synced
        return "Chain has been synced!"

    def select_best_node(self, responses):
        best_authorized = []
        best_authorized_chain_size = 0
        best_unathorized = []
        best_unathorized_chain_size = 0
        for response in responses:
            if response["node"].is_authorized:
                if best_authorized is None or response["chain_size"] > best_authorized_chain_size:
                    best_authorized.append(response)
                    best_authorized_chain_size = response["chain_size"]
                elif response["chain_size"] == best_authorized_chain_size:
                    best_authorized.append(response)
            else:
                if best_unathorized is None or response["chain_size"] > best_unathorized_chain_size:
                    best_unathorized.append(response)
                    best_unathorized_chain_size = response["chain_size"]
                elif response["chain_size"] == best_unathorized_chain_size:
                    best_unathorized.append(response)
        best_authorized.sort(key=lambda x: random.random())
        best_unathorized.sort(key=lambda x: random.random())
        best_nodes = best_authorized + best_unathorized
        if len(best_nodes) > 0:
            return best_nodes
        raise NoPeersAviableError()

    @retry(
        stop=stop_after_attempt(max_tries),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARN),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    async def __create_node(self, port):
        try:
            logger.info("Creating node...")
            node = await P2PNode(port=port)
            node.add_msg_cb(self.protocol_manager.add_peer_protocole_support)
            await node.start(out=True)
            logger.info(f"Node started = {node.addr_bytes}")
            logger.info(f"Node port = {node.listen_port}",)
            return node
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            raise e

    async def change_node_nickname(self, nickname):
        try:
            self.nickname = nickname
            await self._set_node_nickname(nickname)
        except Exception as e:
            logger.error(f"Failed to change node nickname: {e}")
            raise e

    async def present_to_peer(self, nickname):
        peer = self.peers_manager.get_peer_by_nickname(nickname)
        if peer is None:
            raise PeerNotFoundError(nickname)
        pipe = await self.node.connect(nickname)
        if pipe is None:
            raise PeerNotFoundError(nickname)
        await self.protocol_manager.present_self(pipe)
        return "Presented to peer!"
