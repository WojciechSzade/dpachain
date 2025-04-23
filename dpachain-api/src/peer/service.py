from src.peer.models import PeerStatus
from src.peer.manager import PeersManager


class PeerService:
    def __init__(self, peer_manager: PeersManager):
        self.peer_manager = peer_manager

    def add_new_peer(self, nickname, adress, is_authorized, public_key=None):
        self.peer_manager.add_new_peer(
            nickname, adress, is_authorized, public_key)

    def get_peers_list(self):
        peers = self.peer_manager.get_peers_list()
        for peer in peers:
            peer.status = PeerStatus(peer.status).name
        return peers

    def remove_peer(self, nickname):
        peer = self.peer_manager.get_peer_by_nickname(nickname)
        self.peer_manager.remove_peer(peer)
        return "Peer has been removed"


    def ban_peer(self, nickname):
        peer = self.peer_manager.get_peer_by_nickname(nickname)
        self.peer_manager.ban_peer(peer)
        return "Peer has been banned"

    def unban_peer(self, nickname):
        peer = self.peer_manager.get_peer_by_nickname(nickname)
        return self.peer_manager.unban_peer(peer)
