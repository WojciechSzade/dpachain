from functools import wraps
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolManager:
    def __init__(self, peers_manager):
        self.peers_manager = peers_manager

    @staticmethod
    def parse_message():
        """Decorator to parse a message before passing it to the function"""
        def decorator(func):
            @wraps(func)
            def wrapper(self, msg, *args, **kwargs):
                try:
                    msg = json.loads(msg.decode())
                except json.JSONDecodeError:
                    logger.error("Invalid JSON message received")
                    return

                protocol = msg.get("protocol")
                author = msg.get("author")
                payload = msg.get("payload")

                if not protocol or not author:
                    logger.error(f"Invalid message structure: {msg}")
                    return

                return func(self, protocol, author, payload, *args, **kwargs)

            return wrapper
        return decorator

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

    @parse_message()
    async def add_peer_protocole_support(self, protocol, author, payload, client_tup, pipe):
        author_peer = self.get_author_peer(author)
        if author_peer is None:
            self.handle_unknown_author()
            return
        match protocol:
            case 'ask_chain_size':
                self.handle_ask_chain_size(pipe)

    async def handle_unknown_author():
        """Respond to unknown author - let them know to present themselves"""
        pass

    @staticmethod
    async def send_message(self, pipe, msg, wait_response=False):
        """Send message to peer"""
        msg.encode()
        await pipe.send(msg)
        if wait_response:
            res = await pipe.recv(timeout=100)
            if res is None:
                logger.error("Failed to receive response from peer")
                return
            self.parse_message(res)

    async def request_chain_size(self, pipe):
        """Send request to get chain size from peer"""
        msg = {
            "protocol": "ask_chain_size",
            "author": self.peers_manager.own_peer_name,
            "payload": None
        }
        response = self.send_message(pipe, msg, wait_response=True)
        if response is None or response.get("payload") is None:
            logger.error("Failed to get chain size from peer")
            return
        chain_size = response.get("payload")
        return chain_size

    def handle_ask_chain_size(self, pipe):
        """Send chain size to peer"""
        chain_size = self.peers_manager.get_chain_size()
        msg = {
            "protocol": "chain_size_response",
            "author": self.peers_manager.own_peer_name,
            "payload": chain_size
        }
        self.send_message(pipe, msg)
        pipe.close()
        return
