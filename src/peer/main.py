from src.peer.models import PeerStatus
from src.peer.peers import PeersManager


class PeerService:
    def __init__(self, peer_manager: PeersManager):
        self.peer_manager = peer_manager

    def add_new_peer(self, nickname, is_authorized, public_key):
        return self.peer_manager.add_new_peer(nickname, is_authorized, public_key)

    def get_peers_list(self):
        peers = self.peer_manager.get_peers_list()
        for peer in peers:
            peer.status = PeerStatus(peer.status).name
        return peers

    def remove_peer(self, nickname):
        return self.peer_manager.remove_peer(nickname)

    def ban_peer(self, nickname):
        return self.peer_manager.ban_peer(nickname)

    def unban_peer(self, nickname):
        return self.peer_manager.unban_peer(nickname)
