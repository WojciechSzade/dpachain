from functools import wraps
import logging
import json
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Signature import pss
import base64
import asyncio

from src.block.interfaces import IBlockManager
from src.block.models import Block, GenesisBlock
from src.node.errors import *
from src.peer.interfaces import IPeerManager
from src.utils.utils import normalize_pem

from src.peer.models import PeerStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolManager:
    def __init__(self, node_manager, private_signing_key):
        self.block_manager = None
        self.peer_manager = None
        self.node_manager = node_manager
        self.private_signing_key = RSA.import_key(private_signing_key)

    def set_block_manager(self, block_manager: IBlockManager):
        self.block_manager = block_manager

    def set_peer_manager(self, peers_manager: IPeerManager):
        self.peer_manager = peers_manager

    @staticmethod
    def parse_message(msg):
        try:
            if msg is None or not msg.startswith(b"DPACHAIN"):
                return
            msg = msg[len(b"DPACHAIN"):]
            try:
                msg = json.loads(msg.decode('utf-8'))
            except json.JSONDecodeError as base:
                e = InvalidMessageReceivedError(msg)
                logger.error(e)
                raise e from base

            protocol = msg.get("protocol")
            author = msg.get("author")
            signature = msg.pop("signature", None)
            payload = msg.get("payload")

            if not protocol or not author:
                e = InvalidMessageReceivedError(msg)
                logger.error(e)
                raise e
            # logger.info(
            #     f"RECEIVED MESSAGE: protocol: {protocol}, author: {author}, payload: {payload}, signature: {signature}")
            return msg, protocol, author, payload, signature
        except Exception as base:
            e = InvalidMessageReceivedError(msg)
            logger.error(e)
            raise e from base

    def get_author_peer(self, author, protocol) -> Peer:
        author_peer = self.peer_manager.find_peer_by_nickname(author)
        if protocol != 'new_peer':
            if author_peer is None:
                return self.handle_unknown_author(author, protocol)
            is_not_valid = author_peer.is_not_valid()
            if is_not_valid:
                e = InvalidMessageAuthorError(
                    author_peer.nickname, is_not_valid, protocol)
                logger.error(e)
                raise e
            self.peer_manager.set_peer_status(
                author_peer, PeerStatus.ACTIVE)
        return author_peer

    def verify_signature(self, raw_data, public_key, signature):
        canon = json.dumps(raw_data, separators=(',', ':'), sort_keys=True)
        hobj = SHA256.new(canon.encode('utf-8'))
        public_key = RSA.import_key(public_key)
        verifier = pss.new(public_key)
        try:
            verifier.verify(hobj, base64.b64decode(signature))
            return True
        except (ValueError, TypeError):
            return False

    async def add_peer_protocole_support(self, msg, client_tup, pipe):
        # This try statement is used to log exceptions,
        # as this method exits silenty if it runs into one
        try:
            await asyncio.sleep(0.5)
            # this sleep is so the response message is not missed by the asking node
            parsed = self.parse_message(msg)
            if parsed is None:
                return
            raw_data, protocol, author, payload, signature = parsed
            author_peer = self.get_author_peer(author, protocol)
            signed_correct = self.verify_signature(
                raw_data, author_peer.public_key, signature) if signature else False
            if not signed_correct and protocol != 'new_peer':
                raise InvalidSignatureError(author_peer.nickname)

            match protocol:
                case 'ask_chain_size':
                    logger.info(
                        f"Received ask_chain_size from {author}, handling.")
                    await self.handle_ask_chain_size(pipe)
                case 'response_chain_size':
                    logger.info(
                        f"Received response_chain_size from {author}, {payload} - this should be currently handled in the request.")
                case 'ask_compare_blockchain':
                    logger.info(
                        f"Received ask_compare_blockchain from {author}, handling.")
                    await self.handle_compare_blockchain(pipe)
                case 'response_compare_blockchain':
                    logger.info(
                        f"Received response_compare_blockchain from {author}, {payload} - this should be currently handled in the request.")
                case 'ask_block':
                    logger.info(
                        f"Received ask_block from {author}, handling.")
                    await self.handle_ask_block(pipe, payload)
                case 'response_block':
                    logger.info(
                        f"Received response_block from {author}, {payload} - this should be currently handled in the request.")
                case 'new_peer':
                    logger.info(
                        f"Received new_peer from {author}, handling.")
                    await self.handle_new_peer(pipe, payload)
                case 'present_self':
                    logger.info(
                        f"Received present_self from {author}, handling.")
                    await self.present_self(pipe)
                case 'ask_sync_chain':
                    logger.info(
                        f"Received ask_sync_chain from {author}, handling.")
                    await self.handle_ask_sync(pipe)

                case _:
                    logger.error(f"Unknown protocol {protocol} from {author}")
            await pipe.close()
        except Exception as e:
            await pipe.close()
            logger.error(e)
            raise e

    def handle_unknown_author(self, author, protocol):
        """Respond to unknown author - let them know to present themselves"""
        e = InvalidMessageAuthorError(
            author, "author is unknown and protocol is not new_peer", protocol)
        logger.error(str(e))
        raise e

    def sign_message(self, data: dict) -> str:
        """Sign a dictionary by first canonicalizing it."""
        canon = json.dumps(data, separators=(',', ':'), sort_keys=True)
        encrypted_hash = SHA256.new(canon.encode('utf-8'))
        signature = pss.new(self.private_signing_key).sign(encrypted_hash)
        return base64.b64encode(signature).decode()

    async def send_message(self, pipe, msg, wait_response=False):
        """Send message to peer"""
        protocol = msg["protocol"]

        msg["signature"] = self.sign_message(
            msg) if protocol != 'new_peer' else None
        msg = json.dumps(msg).encode('utf-8')

        logger.info(f"SEND_MESSAGE {msg}")
        msg = b"DPACHAIN" + msg
        if not wait_response:
            await pipe.send(msg)
            await pipe.close()
            return
        await pipe.send(msg)
        res = await pipe.recv(timeout=20)
        if res is None:
            logger.info(
                f"Awaiting timedout.")
            await pipe.close()
            e = NoResponseReceivedError(pipe, protocol)
            raise e
        await pipe.close()
        response = {}
        raw_data, response["protocol"], response["author"], response["payload"], response["signature"] = self.parse_message(
            res)
        author_peer = self.get_author_peer(
            response["author"], response["protocol"])
        signed_correct = self.verify_signature(
            raw_data, author_peer.public_key, response["signature"]) if response["signature"] else False
        if not signed_correct:
            e = InvalidSignatureError(author_peer.nickname)
            logger.error(str(e))
            raise e
        return response["protocol"], response["author"], response["payload"]

    async def request_chain_size(self, pipe):
        """Send request to get chain size from peer"""
        msg = {
            "protocol": "ask_chain_size",
            "author": self.peer_manager.get_own_peer_name(),
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
            "author": self.peer_manager.get_own_peer_name(),
            "payload": {"chain_size": chain_size}
        }
        await self.send_message(pipe, msg)
        return

    async def request_compare_blockchain(self, pipe):
        """Request to compare blockchain with peer"""
        msg = {
            "protocol": "ask_compare_blockchain",
            "author": self.peer_manager.get_own_peer_name(),
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
        own_last_block_hash = self.block_manager.get_last_block(
        ).hash if own_chain_size > 0 else None
        logger.info(f"Own last block hash to respond is {own_last_block_hash}")
        msg = {
            "protocol": "response_compare_blockchain",
            "author": self.peer_manager.get_own_peer_name(),
            "payload": {"chain_size": own_chain_size, "last_block_hash": own_last_block_hash}
        }
        await self.send_message(pipe, msg)
        return

    async def request_block(self, pipe, block_index):
        """Request block with index from peer"""
        msg = {
            "protocol": "ask_block",
            "author": self.peer_manager.get_own_peer_name(),
            "payload": {"block_index": block_index}
        }
        response = {}
        response["protocol"], response["author"], response["payload"] = await self.send_message(pipe, msg, wait_response="response_block")
        if response["payload"] is not None:
            block = response.get("payload").get("block")
            if block is not None:
                try:
                    if block["_id"] == 0:
                        block = GenesisBlock.from_dict(block)
                    else:
                        block = Block.from_dict(block)
                except Exception as base:
                    e = InvalidResponseReceivedError(
                        pipe, response["protocol"], response["payload"])
                    logger.error(str(e) + " from " + base)
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
        logger.info(f"Block to send is {block.as_dict()}")
        msg = {
            "protocol": "response_block",
            "author": self.peer_manager.get_own_peer_name(),
            "payload": {"block": block.as_dict()}
        }
        await self.send_message(pipe, msg)
        return

    async def present_self(self, pipe):
        """Present self to peer"""
        msg = {
            "protocol": "new_peer",
            "author": self.peer_manager.get_own_peer_name(),
            "payload": {
                "nickname": self.peer_manager.get_own_peer_name(),
                "adress": self.peer_manager.get_own_peer_adress(),
                "public_key": self.peer_manager.get_own_peer_public_key()
            }
        }
        await self.send_message(pipe, msg)
        return

    async def handle_new_peer(self, pipe, payload):
        """Handle new peer request"""
        new_peer_nickname = payload.get("nickname")
        new_peer_public_key = payload.get("public_key")
        new_peer_adress = payload.get("adress")
        if new_peer_nickname is None or new_peer_public_key is None:
            e = InvalidMessageReceivedError(payload)
            logger.error(str(e))
            return
        self.peer_manager.add_new_peer(
            new_peer_nickname,  new_peer_public_key, new_peer_adress, False)
        return

    async def ask_to_sync(self, pipe):
        """Ask peer to sync chain"""
        msg = {
            "protocol": "ask_sync_chain",
            "author": self.peer_manager.get_own_peer_name(),
            "payload": None
        }
        await self.send_message(pipe, msg)
        return

    async def handle_ask_sync(self, pipe):
        """Handle ask to sync chain"""
        logger.info(f"Received ask to sync chain from {pipe}")
        await self.node_manager.sync_chain()
        return
