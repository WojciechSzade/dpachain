from src.peer.models import PeerStatus
from src.peer.manager import PeersManager


class PeerService:
    def __init__(self, peer_manager: PeersManager):
        self.peer_manager = peer_manager

    def add_new_peer(self, nickname, adress, is_authorized, public_key=None):
        self.peer_manager.add_new_peer(
            nickname, adress, is_authorized, public_key)
        return "Peer has been added"

    def get_peers_list(self):
        peers = self.peer_manager.get_peers_list()
        for peer in peers:
            peer.status = PeerStatus(peer.status).name
        return peers

    def remove_peer(self, nickname):
        self.peer_manager.remove_peer(nickname)
        return "Peer has been removed"

    def ban_peer(self, nickname):
        self.peer_manager.ban_peer(nickname)
        return "Peer has been banned"

    def unban_peer(self, nickname):
        msg = self.peer_manager.unban_peer(nickname)
        return msg if msg else "Peer has been unbanned"
