from functools import wraps
import logging
import json

from src.block.manager import BlockManager
from src.peer.manager import PeersManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolManager:
    def __init__(self, peers_manager, block_manager):
        self.peers_manager: PeersManager = peers_manager 
        self.block_manager: BlockManager = block_manager

    @staticmethod
    def parse_message(msg):
        if msg is not None:
            if not msg[:8] == b"DPACHAIN":
                logger.info(f"A non DPACHAIN message received: {msg}")
                return
        else:
            logger.error("Received empty message")
            return
        msg = msg[8:]
        try:
            msg = json.loads(msg.decode('utf-8'))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received {msg}")
            return
        logger.info(f"Received proper message: {msg}")
        protocol = msg.get("protocol")
        author = msg.get("author")
        payload = msg.get("payload")

        if not protocol or not author:
            logger.error(f"Invalid message structure: {msg}")
            return
        logger.info(f"After parsing: protocol: {protocol}, author: {author}, payload: {payload}")
        return protocol, author, payload

    def get_author_peer(self, author, protocol):
        author_peer = self.peers_manager.get_peer_by_name(author)
        if author_peer is None and protocol != 'new_peer':
            self.handle_unknown_author()
            return
        elif not author_peer.is_valid():
            logger.error(
                f"Author {author_peer.nickname} is not valid (probably banned)")
            return
        return author_peer

    async def add_peer_protocole_support(self, msg, client_tup, pipe):
        parse = self.parse_message(msg)
        if parse is None:
            logger.error("Failed to parse message")
            return
        protocol, author, payload = parse
        # author_peer = self.get_author_peer(author)
        # if author_peer is None:
        #     self.handle_unknown_author()
        #     return
        match protocol:
            case 'ask_chain_size':
                logger.info(
                    f"Received ask_chain_size from {author}, handling.")
                return await self.handle_ask_chain_size(pipe)
            case 'chain_size_response':
                logger.info(f"Received chain_size_response from {author}, {payload} - this should be currently handled in the request.")
                return
            case _:
                logger.error(f"Unknown protocol {protocol} from {author}")
                return
        logger.error("I should not be here")

    async def handle_unknown_author():
        """Respond to unknown author - let them know to present themselves"""
        logger.error("Unknown author")
        pass

    @staticmethod
    async def send_message(pipe, msg, wait_response=False):
        """Send message to peer"""
        msg = json.dumps(msg).encode('utf-8')
        msg = b"DPACHAIN" + msg
        logger.info(f"Sending message to {pipe}")
        logger.info(f"Message:\n {msg}")
        await pipe.send(msg)
        if wait_response:
            res = await pipe.recv(timeout=100)
            if res is None:
                logger.error("Failed to receive response from peer")
                raise Exception("Failed to receive response from peer")
            return res

    async def request_chain_size(self, pipe):
        """Send request to get chain size from peer"""
        msg = {
            "protocol": "ask_chain_size",
            "author": self.peers_manager.own_peer_name,
            "payload": None
        }
        logger.info(f"Requesting chain size from {pipe}")
        logger.info(f"Message:\n {msg}")

        res = None
        try:
            res = await self.send_message(pipe, msg, wait_response=True)
        except Exception as e:
            logger.error(f"Failed to get chain size from peer: {e}")

        if res is None:
            logger.error("Failed to get chain size from peer")
            return
        response = {}
        response["protocol"], response["author"], response["payload"] = self.parse_message(
            res)
        if response["payload"] is None:
            logger.error("Failed to get chain size from peer")
            return
        chain_size = response.get("payload")
        return chain_size

    async def handle_ask_chain_size(self, pipe):
        """Send chain size to peer"""
        chain_size = self.block_manager.get_chain_size()
        msg = {
            "protocol": "chain_size_response",
            "author": self.peers_manager.own_peer_name,
            "payload": chain_size
        }
        logger.info(f"Sending chain size to {pipe}")
        logger.info(f"Message:\n {msg}")
        await self.send_message(pipe, msg)
        await pipe.close()
        return
