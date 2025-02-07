import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolManager:
    def __init__(self, peers_manager):
        self.peers_manager = peers_manager

    async def add_peer_protocole_support(self, msg, client_tup, pipe):
        msg = json.loads(msg.decode())
        protocol = msg['protocol'] if 'protocol' in msg else None
        author = msg['author'] if 'author' in msg else None
        payload = msg['payload'] if 'payload' in msg else None
        if protocol is None or author is None:
            logger.error(f"Invalid message received: {msg}")
            return

        author_peer = self.peers_manager.get_peer_by_name(author)
        if author_peer is None and protocol != 'new_peer':
            self.handle_unknown_author()
            return
        elif not author_peer.is_valid():
            logger.error(
                f"Author {author_peer.nickname} is not valid (probably banned)")
            return

        match protocol:
            case 'ask_chain_size':
                self.handle_ask_chain_size(author_peer)

    async def handle_unknown_author():
        """Respond to unknown author - let them know to present themselves"""
        pass

    async def request_chain_size(self, pipe):
        """Send request to get chain size from peer"""
        msg = {
            "protocol": "ask_chain_size",
            "author": self.peers_manager.own_peer_name,
            "payload": None
        }
        msg.encode()
        await pipe.send(msg)

    def handle_ask_chain_size(self, author_peer):
        """Send chain size to peer"""
        pass
