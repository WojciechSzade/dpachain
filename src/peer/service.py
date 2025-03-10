from src.peer.models import PeerStatus
from src.peer.manager import PeersManager


class PeerService:
    def __init__(self, peer_manager: PeersManager):
        self.peer_manager = peer_manager

    def add_new_peer(self, nickname, is_authorized, public_key):
        try:
            return self.peer_manager.add_new_peer(nickname, is_authorized, public_key)
        except Exception as e:
            return str(e)

    def get_peers_list(self):
        try:
            peers = self.peer_manager.get_peers_list()
            for peer in peers:
                peer.status = PeerStatus(peer.status).name
            return peers
        except Exception as e:
            return str(e)

    def remove_peer(self, nickname):
        try:
            return self.peer_manager.remove_peer(nickname)
        except Exception as e:
            return str(e)

    def ban_peer(self, nickname):
        try:
            return self.peer_manager.ban_peer(nickname)
        except Exception as e:
            return str(e)

    def unban_peer(self, nickname):
        try:
            return self.peer_manager.unban_peer(nickname)
        except Exception as e:
            return str(e)
