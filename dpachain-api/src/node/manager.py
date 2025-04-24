from asyncio import sleep
from datetime import datetime
import logging
import random
from p2pd import *
from tenacity import after_log, before_log, before_sleep_log, retry, stop_after_attempt, retry_if_result

from src.block.manager import BlockManager
from src.block.models import Block
from src.node.protocols import ProtocolManager
from src.node.errors import *
from src.peer.errors import PeerNotFoundError
from src.peer.models import Peer, PeerStatus
from src.peer.manager import PeersManager


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

max_tries = 20  # 2 minutes


class NodeManager:
    def __init__(self, nickname):
        self.node = None
        self.peers_manager = None
        self.block_manager = None
        self.protocol_manager = ProtocolManager(self)
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
        peer_list = self.peers_manager.get_valid_peers_to_connect()
        responses = []
        logger.info(f"Nodes list: {peer_list}")
        for peer in peer_list:
            try:
                pipe = await self.connect_to_peer(peer)
            except PeerUnavailableError:
                continue
            try:
                chain_size = await self.protocol_manager.request_chain_size(pipe)
            except NodeError:
                continue
            responses.append(
                {"pipe": pipe, "node": peer, "chain_size": chain_size})
        if len(responses) == 0:
            raise NoPeersAviableError()
        best_nodes = self.select_best_peer(responses)
        for best_node in best_nodes:
            logger.info(f"Connect to best node {best_node.nickname}")
            try:
                pipe = await self.connect_to_peer(peer)
            except PeerUnavailableError:
                continue
            own_chain_size = self.block_manager.get_chain_size()
            own_last_block_hash = self.block_manager.get_latest_block(
            ).hash if own_chain_size > 0 else None
            try:
                res = await self.protocol_manager.request_compare_blockchain(pipe)
            except NodeError:
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
            fail_counter = 0
            FAIL_LIMIT = 10
            for i in range(own_chain_size, chain_size):
                try:
                    pipe = await self.connect_to_peer(peer)
                except PeerUnavailableError as e:
                    fail_counter += 1
                    if fail_counter > FAIL_LIMIT:
                        raise e
                    i -= 1
                    continue
                try:
                    block = await self.protocol_manager.request_block(pipe, i)
                except NodeError:
                    fail_counter += 1
                    if fail_counter > FAIL_LIMIT:
                        raise e
                    i -= 1
                    continue
                logger.info(f"Received block {block}")
                if block is None:
                    fail_counter += 1
                    if fail_counter > FAIL_LIMIT:
                        raise e
                    i -= 1
                    continue
                self.block_manager.add_block(block)
        return "Chain has been synced!"

    def select_best_peer(self, responses):
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
            return [node['node'] for node in best_nodes]
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
        pipe = await self.node.connect(peer.nickname)
        if pipe is None:
            raise PeerNotFoundError(peer.nickname)
        await self.protocol_manager.present_self(pipe)
        return

    async def ask_peer_to_sync(self, nickname):
        peer = self.peers_manager.get_peer_by_nickname(nickname)
        pipe = await self.node.connect(peer.nickname)
        if pipe is None:
            raise PeerNotFoundError(peer.nickname)
        return await self.protocol_manager.ask_to_sync(pipe)

    @retry(
        stop=stop_after_attempt(max_tries),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARN),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    async def generate_new_block(self, diploma_type: str, pdf_file: str, authors: (list[str] | str), authors_id: (list[str] | str),  title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None):
        await self.sync_chain()
        block = self.block_manager.create_new_block(diploma_type, pdf_file, authors, authors_id,
                                                    title, language, discipline, is_defended, date_of_defense,
                                                    university, faculty, supervisor, reviewer,
                                                    additional_info=None)
        peers_list = self.peers_manager.get_valid_peers_to_connect()
        responses = []
        logger.info(f"Nodes list: {peers_list}")
        for peer in peers_list:
            try:
                pipe = await self.connect_to_peer(peer)
            except PeerUnavailableError:
                continue
            chain_size = await self.protocol_manager.request_chain_size(pipe)
            if chain_size is None:
                logger.info(f"Failed to get chain size from {peer.nickname}")
                self.peers_manager.set_peer_status(
                    peer, PeerStatus.INACTIVE)
                continue
            responses.append(
                {"pipe": pipe, "node": peer, "chain_size": chain_size})
        if len(responses) == 0:
            raise NoPeersAviableError()
        best_peers_list = self.select_best_peer(responses)
        for peer in best_peers_list:
            logger.info(f"Connect to best node {peer.nickname}")
            try:
                pipe = await self.connect_to_peer(peer)
            except PeerUnavailableError:
                continue
            await self.protocol_manager.ask_to_sync(pipe)
        is_propagated = await self.check_if_block_was_added_sucessfully(block, best_peers_list)
        if is_propagated:
            return block
        self.block_manager.remove_block(block._id)
        return "Failed to add block to blockchain"

    async def connect_to_peer(self, peer: Peer):
        logger.info(f"Connecting to {peer.nickname}")
        pipe = await self.node.connect(peer.nickname)
        if pipe is None:
            logger.info(
                f"Failed to connect to {peer.nickname} with previous state {peer.get_state()}")
            self.peers_manager.set_peer_status(
                peer, PeerStatus.INACTIVE)
            raise PeerUnavailableError(peer)
        return pipe

    async def check_if_block_was_added_sucessfully(self, block: Block, best_peers_list):
        for i in range(max_tries):
            await sleep(10)
            for peer in best_peers_list:
                try:
                    pipe = await self.connect_to_peer(peer)
                except PeerUnavailableError:
                    continue
                try:
                    res = await self.protocol_manager.request_compare_blockchain(pipe)
                except NodeError as e:
                    logger.error(f"Failed to get response from peer: {str(e)}")
                    continue
                own_chain_size = self.block_manager.get_chain_size()
                own_last_block_hash = self.block_manager.get_latest_block(
                ).hash if own_chain_size > 0 else None
                chain_size, last_block_hash = res
                logger.info(
                    f"Own chain size = {chain_size}, Own last block hash = {last_block_hash}")
                logger.info(
                    f"Received peer chain size = {chain_size}, Peer last block hash = {last_block_hash}")
                if chain_size >= own_chain_size:
                    pipe = await self.node.connect(peer.nickname)
                    if pipe is None:
                        logger.info(
                            f"Failed to connect to {peer.nickname} with previous state {self.peers_manager.get_peer_state(peer.nickname)}")
                    received_block = await self.protocol_manager.request_block(
                        pipe, own_chain_size - 1)
                    if received_block is None:
                        logger.error("Failed to get block from peer")
                        continue
                    if self.block_manager.compare_blocks(received_block, block):
                        logger.info(f"SUCCESS!!!")
                        return True
                    else:
                        logger.error("Received block is not the same!")
                        continue
        return False
