from functools import wraps
import logging
import json

from src.block.manager import BlockManager
from src.block.models import Block
from src.node.errors import *
from src.peer.manager import PeersManager
from src.peer.models import PeerStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolManager:
    def __init__(self, node_manager):
        self.block_manager: BlockManager = None
        self.peers_manager: PeersManager = None
        self.node_manager = node_manager

    def set_block_manager(self, block_manager: BlockManager):
        self.block_manager = block_manager

    def set_peers_manager(self, peers_manager: PeersManager):
        self.peers_manager = peers_manager

    @staticmethod
    def parse_message(msg):
        if msg is None or msg[:8] != b"DPACHAIN":
            return
        msg = msg[8:]
        try:
            msg = json.loads(msg.decode('utf-8'))
        except json.JSONDecodeError as base:
            e = InvalidMessageReceivedError(msg)
            logger.error(e)
            raise e from base

        protocol = msg.get("protocol")
        author = msg.get("author")
        payload = msg.get("payload")

        if not protocol or not author:
            e = InvalidMessageReceivedError(msg)
            logger.error(e)
            raise e
        logger.info(
            f"RECEIVED MESSAGE: protocol: {protocol}, author: {author}, payload: {payload}")
        return protocol, author, payload

    def get_author_peer(self, author, protocol) -> Peer:
        author_peer = self.peers_manager._get_peer_by_nickname(author)
        if protocol != 'new_peer':
            if author_peer is None:
                return self.handle_unknown_author(author, protocol)
            is_not_valid = author_peer.is_not_valid()
            if is_not_valid:
                e = InvalidMessageAuthorError(
                    author_peer.nickname, is_not_valid, protocol)
                logger.error(e)
                raise e
            self.peers_manager.set_peer_status(
                author_peer, PeerStatus.ACTIVE)
        return author_peer

    async def add_peer_protocole_support(self, msg, client_tup, pipe):
        parse = self.parse_message(msg)
        if parse is None:
            return
        protocol, author, payload = parse
        author_peer = self.get_author_peer(author, protocol)
        match protocol:
            case 'ask_chain_size':
                logger.info(
                    f"Received ask_chain_size from {author}, handling.")
                return await self.handle_ask_chain_size(pipe)
            case 'response_chain_size':
                logger.info(
                    f"Received response_chain_size from {author}, {payload} - this should be currently handled in the request.")
                return
            case 'ask_compare_blockchain':
                logger.info(
                    f"Received ask_compare_blockchain from {author}, handling.")
                return await self.handle_compare_blockchain(pipe)
            case 'response_compare_blockchain':
                logger.info(
                    f"Received response_compare_blockchain from {author}, {payload} - this should be currently handled in the request.")
                return
            case 'ask_block':
                logger.info(
                    f"Received ask_block from {author}, handling.")
                return await self.handle_ask_block(pipe, payload)
            case 'response_block':
                logger.info(
                    f"Received response_block from {author}, {payload} - this should be currently handled in the request.")
                return
            case 'new_peer':
                logger.info(
                    f"Received new_peer from {author}, handling.")
                return await self.handle_new_peer(pipe, payload)
            case 'present_self':
                logger.info(
                    f"Received present_self from {author}, handling.")
                return await self.present_self(pipe)
            case 'ask_sync_chain':
                logger.info(
                    f"Received ask_sync_chain from {author}, handling.")
                return await self.handle_ask_sync(pipe)

            case _:
                logger.error(f"Unknown protocol {protocol} from {author}")
                return

    async def handle_unknown_author(self, author, protocol):
        """Respond to unknown author - let them know to present themselves"""
        e = InvalidMessageAuthorError(
            author, "author is unknown and protocol is not new_peer", protocol)
        logger.error(str(e))
        raise e

    async def send_message(self, pipe, msg, wait_response=False):
        """Send message to peer"""
        _protocol = msg["protocol"]
        msg = json.dumps(msg).encode('utf-8')
        logger.info(f"SEND_MESSAGE {msg}")
        msg = b"DPACHAIN" + msg
        await pipe.send(msg)
        if wait_response:
            res = await pipe.recv(timeout=20)
            if res is None:
                logger.info(
                    f"Awaiting timedout.")
                e = NoResponseReceivedError(pipe, _protocol)
                raise e
            response = {}
            response["protocol"], response["author"], response["payload"] = self.parse_message(
                res)
            return response["protocol"], response["author"], response["payload"]

    async def request_chain_size(self, pipe):
        """Send request to get chain size from peer"""
        msg = {
            "protocol": "ask_chain_size",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": None
        }

        response = {}
        response["protocol"], response["author"], response["payload"] = await self.send_message(pipe, msg, wait_response="response_chain_size")
        if response["payload"] is None or type(response["payload"].get("chain_size")) != int:
            e = InvalidResponseReceivedError(
                pipe, response["protocol"], response["payload"])
            logger.warning(str(e))
            raise e
        return response["payload"]["chain_size"]

    async def handle_ask_chain_size(self, pipe):
        """Send chain size to peer"""
        chain_size = self.block_manager.get_chain_size()
        msg = {
            "protocol": "response_chain_size",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": {"chain_size": chain_size}
        }
        await self.send_message(pipe, msg)
        await pipe.close()
        return

    async def request_compare_blockchain(self, pipe):
        """Request to compare blockchain with peer"""
        msg = {
            "protocol": "ask_compare_blockchain",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": None
        }
        response = {}
        response["protocol"], response["author"], response["payload"] = await self.send_message(pipe, msg, wait_response="response_compare_blockchain")
        if response["payload"] is not None:
            chain_size = response.get("payload").get("chain_size")
            last_block_hash = response.get("payload").get("last_block_hash")
            if chain_size is not None:
                return chain_size, last_block_hash
        e = InvalidResponseReceivedError(
            pipe, response["protocol"], response["payload"])
        logger.error(str(e))
        raise e

    async def handle_compare_blockchain(self, pipe):
        """Handle compare blockchain request"""
        own_chain_size = self.block_manager.get_chain_size()
        logger.info(f"Own chain size to respond is {own_chain_size}")
        own_last_block_hash = self.block_manager.get_latest_block(
        ).hash if own_chain_size > 0 else None
        logger.info(f"Own last block hash to respond is {own_last_block_hash}")
        msg = {
            "protocol": "response_compare_blockchain",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": {"chain_size": own_chain_size, "last_block_hash": own_last_block_hash}
        }
        await self.send_message(pipe, msg)
        await pipe.close()
        return

    async def request_block(self, pipe, block_index):
        """Request block with index from peer"""
        msg = {
            "protocol": "ask_block",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": {"block_index": block_index}
        }
        response = {}
        response["protocol"], response["author"], response["payload"] = await self.send_message(pipe, msg, wait_response="response_block")
        if response["payload"] is not None:
            block = response.get("payload").get("block")
            if block is not None:
                try:
                    block = Block.from_dict(block)
                except Exception as base:
                    e = InvalidResponseReceivedError(
                        pipe, response["protocol"], response["payload"])
                    logger.error(str(e))
                    raise e from base
            return block
        e = InvalidResponseReceivedError(
            pipe, response["protocol"], response["payload"])
        logger.error(str(e))
        raise e

    async def handle_ask_block(self, pipe, payload):
        """Handle ask block request"""
        block_index = payload.get("block_index")
        if block_index is None:
            logger.error("Failed to get block index from peer")
            return
        block = self.block_manager.get_block_by_index(block_index)
        logger.info(f"Block to send is {block.dict}")
        msg = {
            "protocol": "response_block",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": {"block": block.dict}
        }
        await self.send_message(pipe, msg)
        await pipe.close()
        return

    async def present_self(self, pipe):
        """Present self to peer"""
        msg = {
            "protocol": "new_peer",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": {
                "nickname": self.peers_manager.get_own_peer_name(),
                "adress": self.peers_manager.get_own_peer_adress(),
            }
        }
        await self.send_message(pipe, msg)
        await pipe.close()
        return

    async def handle_new_peer(self, pipe, payload):
        """Handle new peer request"""
        new_peer_nickname = payload.get("nickname")
        new_peer_adress = payload.get("adress")
        if new_peer_nickname is None:
            e = InvalidMessageReceivedError(payload)
            logger.error(str(e))
            return
        self.peers_manager.add_new_peer(
            new_peer_nickname, new_peer_adress)
        await pipe.close()
        return

    async def ask_to_sync(self, pipe):
        """Ask peer to sync chain"""
        msg = {
            "protocol": "ask_sync_chain",
            "author": self.peers_manager.get_own_peer_name(),
            "payload": None
        }
        await self.send_message(pipe, msg)
        return

    async def handle_ask_sync(self, pipe):
        """Handle ask to sync chain"""
        logger.info(f"Received ask to sync chain from {pipe}")
        await self.node_manager.sync_chain()
        return
